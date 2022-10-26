"""
Main FlightGear interface module
"""
import copy
import socket
import sys
import re
import multiprocessing as mp
from typing import Callable, Optional, Tuple, Any, Dict, Union, ByteString

from construct import ConstError, Struct

from .general_util import EventPipe, strip_end
from .fg_util import FGConnectionError, FGCommunicationError, fix_fg_radian_parsing

rx_callback_type = Callable[[Struct, EventPipe], Optional[Struct]]
"""
RX callback function type, signature should be:

.. code-block:: python

    def rx_cb(fdm_data: Construct.Struct, event_pipe: EventPipe) -> Optional[Construct.Struct]:
"""


class FGConnection:
    """
    Base class for FlightGear connections
    sphinx-no-autodoc
    """
    fg_net_struct: Optional[Struct] = None

    def __init__(self, rx_timeout_s: float = 2.0):
        self.event_pipe = EventPipe(duplex=True)

        self.fg_rx_sock: Optional[socket.socket] = None
        self.fg_rx_cb: Optional[rx_callback_type] = None

        self.fg_tx_sock: Optional[socket.socket] = None
        self.fg_tx_addr: Optional[Tuple[str, int]] = None

        self.rx_proc: Optional[mp.Process] = None
        self.rx_timeout_s = rx_timeout_s

    def connect_rx(self, fg_host: str, fg_port: int, rx_cb: rx_callback_type) -> EventPipe:
        """
        Connect to a UDP output of FlightGear

        :param fg_host: IP address of FG (usually localhost)
        :param fg_port: Port of the output socket (i.e. the ``5501`` from\
        ``--native-fdm=socket,out,30,,5501,udp``)
        :param rx_cb: Callback function, called whenever we receive data from FG.\
        Function signature should follow :attr:`rx_callback_type`
        :return: ``EventPipe`` so that data can be passed from the parent process\
        to the callback process
        """
        # TODO: Support TCP server so that we only need 1 port
        self.fg_rx_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        fg_rx_addr = (fg_host, fg_port)
        try:
            self.fg_rx_sock.bind(fg_rx_addr)
        except Exception as e:
            raise FGConnectionError(f'Could not bind to {fg_rx_addr}: {e}')
        self.fg_rx_cb = rx_cb

        return self.event_pipe

    def connect_tx(self, fg_host: str, fg_port: int):
        """
        Connect to a UDP input of FlightGear

        :param fg_host: IP address of FG (usually localhost)
        :param fg_port: Port of the input socket (i.e. the ``5502`` from\
        ``--native-fdm=socket,in,,,5502,udp``)
        """
        self.fg_tx_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.fg_tx_addr = (fg_host, fg_port)

    def _fg_packet_roundtrip(self):
        # Receive up to 1KB of data from FG
        # blocking is fine here since we're in a separate process

        try:
            rx_msg, _ = self.fg_rx_sock.recvfrom(1024)
        except socket.timeout as e:
            raise FGConnectionError(f'Timeout waiting for data, waited {self.rx_timeout_s} seconds') from e
        try:
            s = self.fg_net_struct.parse(rx_msg)
        except ConstError as e:
            raise FGCommunicationError(f'Could not decode FG stream. Is this the right FDM version?\n{e}') from e

        # Fix FG's radian parsing error :(
        s = fix_fg_radian_parsing(s)

        # Call user method
        s = self.fg_rx_cb(s, self.event_pipe)
        sys.stdout.flush()  # flush so that `print()` works

        # Send data back to FG
        if self.fg_tx_sock is not None and s is not None:
            tx_msg = self.fg_net_struct.build(dict(**s))
            self.fg_tx_sock.sendto(tx_msg, self.fg_tx_addr)

    def _rx_process(self):
        if self.fg_tx_sock is None:
            print(f'Warning: TX not connected, not sending updates to FG for RX {self.fg_rx_sock.getsockname()}')

        self.fg_rx_sock.settimeout(self.rx_timeout_s)
        while True:
            self._fg_packet_roundtrip()

    def start(self):
        """
        Start the RX/TX loop with FlightGear
        """
        self.rx_proc = mp.Process(target=self._rx_process)
        self.rx_proc.start()

    def stop(self):
        """
        Stop the RX/TX loop
        """
        self.rx_proc.terminate()


class FDMConnection(FGConnection):
    """
    FlightGear Flight Dynamics Model Connection

    :param fdm_version: Net FDM version (24 or 25)
    """

    def __init__(self, fdm_version: int):
        super().__init__()
        # TODO: Support auto-version check
        if fdm_version == 24:
            from .fdm_v24 import fdm_struct
        elif fdm_version == 25:
            from .fdm_v25 import fdm_struct
        else:
            raise NotImplementedError(f'FDM version {fdm_version} not supported yet')
        # Create Struct from Dict
        self.fg_net_struct = Struct(*[k / v for k, v in fdm_struct.items()])


class PropsConnection:
    """
    FlightGear Telnet Interface Connection (also known as the property interface).
    See https://wiki.flightgear.org/Telnet_usage for general details.

    :param host: IP address of FG (usually localhost)
    :param tcp_port: Port of the telnet socket (i.e. the ``5500`` from\
        ``--telnet=socket,bi,60,localhost,5500,tcp``)
    :param rx_timeout_s: Optional timeout value in seconds when recieving data
    """

    def __init__(self, host: str, tcp_port: int, rx_timeout_s: float = 2.0):
        self.host = host
        self.port = tcp_port
        # SOCK_STREAM == TCP
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.rx_timeout_s = rx_timeout_s

    def connect(self):
        """
        Connect to the FlightGear telnet server
        """
        telnet_addr = (self.host, self.port)
        try:
            self.sock.connect(telnet_addr)
        except Exception as e:
            raise FGConnectionError(f'Could not connect to FlightGear telnet server {telnet_addr}: {e}') from e
        # force move to the root directory (maybe someone was connected before we were)
        _ = self._send_cmd_get_resp('cd /')

    @staticmethod
    def _telnet_str(in_str: str) -> ByteString:
        return f'{in_str}\r\n'.encode()

    def _send_cmd_get_resp(self, cmd_str: str, buflen: int = 512) -> str:
        self.sock.sendall(self._telnet_str(cmd_str))

        self.sock.settimeout(self.rx_timeout_s)
        # FG telnet always ends with a prompt (`cwd`> ), and since we always
        # operate relative to the root directory, it should always be the same prompt
        ending_bytes = b'/> '
        resp_bytes = b''
        while not resp_bytes.endswith(ending_bytes):
            # Loop until FG sends us all the data
            try:
                resp_bytes += self.sock.recv(buflen)
            except socket.timeout as e:
                raise FGConnectionError(f'Timeout waiting for data, waited {self.rx_timeout_s} seconds') from e
        resp_bytes = strip_end(resp_bytes, b'\r\n' + ending_bytes)  # trim the prompt

        resp_str = resp_bytes.decode()
        if resp_str.startswith('-ERR'):
            raise FGCommunicationError(f'Bad telnet command "{cmd_str}". Response: "{resp_str}"')
        return resp_str

    @staticmethod
    def _extract_fg_prop(resp_str: str) -> Tuple[str, Any]:
        try:
            match = re.search(r"^(.+)\s=\s+'(.*)'\s+\((.+)\)$", resp_str, flags=re.DOTALL)
        except Exception as e:
            raise FGCommunicationError(f'Could not parse FG telnet response for msg "{resp_str}": {e}') from e
        if match is None:
            raise FGCommunicationError(f'Could not parse FG telnet response for msg "{resp_str}"')
        key_str = match.group(1)
        value_str = match.group(2)
        type_str = match.group(3)
        convert_fn = {
            'bool': bool,
            'int': int,
            'string': str,
            'double': float,
        }.get(type_str, lambda x: x)
        try:
            value = convert_fn(value_str)
        except ValueError as e:
            raise FGCommunicationError(f'Could not auto-convert "{resp_str}": {e}') from e
        return key_str, value

    def get_prop(self, prop_str: str) -> Any:
        """
        Get a property from FlightGear.

        :param prop_str: Location of the property, should always be relative to\
            the root (``/``)
        :return: The value of the property. If FG tells us what the type is we \
            will pre-convert it (i.e. make an int from a string)
        """
        if not prop_str.startswith('/'):
            raise ValueError(f'Property must be absolute (start with /): {prop_str}')
        resp_str = self._send_cmd_get_resp(f'get {prop_str}')
        _, value = self._extract_fg_prop(resp_str)
        return value

    def set_prop(self, prop_str: str, value: Any):
        """
        Set a property in FlightGear.

        :param prop_str: Location of the property, should always be relative to\
            the root (``/``)
        :param value: Value to set the property to. Must be convertible to ``str``
        """
        if not prop_str.startswith('/'):
            raise ValueError(f'Property must be absolute (start with /): {prop_str}')
        _ = self._send_cmd_get_resp(f'set {prop_str} {str(value)}')
        # We don't care about the response

    def list_props(self, path: str = '/', recurse_limit: Optional[int] = 0) -> Dict[str, Union[list, Dict]]:
        """
        List properties in the FlightGear property tree.

        :param path: Directory to list from, should always be relative to
            the root (``/``)
        :param recurse_limit: How many times to recurse into subdirectories.
            1 (default) is no recursion, 2 is 1 level deep, etc. Passing in
            ``None`` disables the recursion limit. Be warned that enabling any kind of recursion will take a long time!
        :return: Dictionary with keys:

            * ``directories``: List of directories, absolute path
            * ``properties``: Dictionary with property name as the key (absolute path), value as their value.

        Example for ``list_props('/position', recurse_limit=0)``:

        .. code-block:: python

            {
                'directories': [
                    '/position/model'
                ],
                'properties': {
                    '/position/altitude-agl-ft': 3.148566963,
                    '/position/altitude-agl-m': 0.9596832103,
                    '/position/altitude-ft': 3491.986254,
                    '/position/ground-elev-ft': 3488.469757,
                    '/position/ground-elev-m': 1063.285582,
                    '/position/latitude-deg': 0.104476136,
                    '/position/latitude-string': '0*06\\'16.1"N',
                    '/position/longitude-deg': 100.023135,
                    '/position/longitude-string': '100*01\\'23.3"E',
                    '/position/sea-level-radius-ft': 20925646.09
                }
            }
        """
        if not path.startswith('/'):
            raise ValueError(f'Path must be absolute (start with /): {path}')
        path = path.rstrip('/')  # Strip trailing slash to keep things consistent

        resp_list = self._send_cmd_get_resp(f'ls {path}').split('\r\n')
        # extract of directories, absolute path
        dir_list = [f'{path}/{s.rstrip("/")}' for s in resp_list if s.endswith('/')]

        prop_dict = {}
        # recursion support
        if recurse_limit is None or recurse_limit > 0:
            dir_list_cwd = copy.deepcopy(dir_list)
            for dir_str in dir_list_cwd:
                # Handle None as a recursion limit
                if recurse_limit is None:
                    new_recurse_limit = None
                else:
                    new_recurse_limit = recurse_limit - 1
                # recursion!
                dir_dict = self.list_props(dir_str, recurse_limit=new_recurse_limit)
                # add the recursed properties
                prop_dict = {**prop_dict, **dir_dict['properties']}
                dir_list.remove(dir_str)  # remove the non-recursed directory
                # add the recursed directories
                dir_list += dir_dict['directories']

        # extract all the values
        for s in resp_list:
            if '=' in s:
                key, val = self._extract_fg_prop(s)
                # prepend the key with the working directory, keep naming consistent
                prop_dict[f'{path}/{key}'] = val

        # Returned paths are absolute
        rtn_dict = {
            # sort the list because we're nice
            'directories': dir_list,
            'properties': prop_dict,
        }
        return rtn_dict
