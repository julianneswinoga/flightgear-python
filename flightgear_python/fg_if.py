"""
Main FlightGear interface module
"""
import copy
import math
import socket
import sys
import re
import multiprocessing as mp
from typing import Callable, Optional, Tuple, Any, Union, ByteString

from construct import ConstError, Struct


class FGConnectionError(Exception):
    pass


class FGCommunicationError(Exception):
    pass


class EventPipe:
    """
    Helper abstraction for passing data from a parent process to a child
    process.

    :param duplex: Allow internal pipe to also pass data from child to \
    parent. Recommended to leave at default
    """

    def __init__(self, duplex=False):
        self.event = mp.Event()
        # TODO: Any value in duplex?
        # If not duplex, can only transfer data from parent to child
        self.child_pipe, self.parent_pipe = mp.Pipe(duplex=duplex)

        # function aliases
        self.set = self.event.set
        self.is_set = self.event.is_set
        self.clear = self.event.clear
        # self.child_send = self.child_pipe.send
        self.child_poll = self.child_pipe.poll
        # self.parent_recv = self.parent_pipe.recv
        # self.parent_poll = self.parent_pipe.poll

    def parent_send(self, *args, **kwargs):
        """
        Send data from the parent process to the child process, then set\
        our event flag

        :param args: Passed to :meth:`multiprocessing.connection.Connection.send()`
        :param kwargs: Passed to :meth:`multiprocessing.connection.Connection.send()`
        """
        if not self.is_set():
            # Only send when data has been received
            self.parent_pipe.send(*args, **kwargs)
            self.set()

    def child_recv(self, *args, **kwargs) -> Any:
        """
        Receive data from the parent process to the child process, then clear\
        our event flag

        :param args: Passed to :meth:`multiprocessing.connection.Connection.recv()`
        :param kwargs: Passed to :meth:`multiprocessing.connection.Connection.recv()`
        """
        msg = self.child_pipe.recv(*args, **kwargs)
        self.clear()
        return msg


def offset_fg_radian(in_rad: float) -> float:
    """
    Even when echoing back literally what FG sends over the Net FDM connection,
    (i.e. UDP bytes in -> UDP bytes out) the latitude/longitude shown in FG
    appear to decrease. After plotting the offsets at a couple different lat/lons
    it appears to be a linear relationship and identical in anything that is
    represented in radians. The coefficient was chosen through trial-and-error.
    sphinx-no-autodoc

    :param in_rad: Input property, in radians
    :return: Offset that needs to be applied to the input, in radians
    """
    coeff = 1.09349403e-9
    return math.degrees(in_rad) * coeff


def fix_fg_radian_parsing(s: Struct) -> Struct:
    """
    Helper for all the radian values in the FDM
    sphinx-no-autodoc
    """
    s.lon_rad += offset_fg_radian(s.lon_rad)
    s.lat_rad += offset_fg_radian(s.lat_rad)
    s.phi_rad += offset_fg_radian(s.phi_rad)
    s.theta_rad += offset_fg_radian(s.theta_rad)
    s.psi_rad += offset_fg_radian(s.psi_rad)
    s.alpha_rad += offset_fg_radian(s.alpha_rad)
    s.beta_rad += offset_fg_radian(s.beta_rad)
    s.phidot_rad_per_s += offset_fg_radian(s.phidot_rad_per_s)
    s.thetadot_rad_per_s += offset_fg_radian(s.thetadot_rad_per_s)
    s.psidot_rad_per_s += offset_fg_radian(s.psidot_rad_per_s)
    return s


rx_callback_type = Callable[[Struct, EventPipe], Struct]
"""
RX callback function type, signature should be:

.. code-block:: python

    def rx_cb(fdm_data: Construct.Struct, event_pipe: EventPipe):
"""


class FGConnection:
    """
    Base class for FlightGear connections
    sphinx-no-autodoc
    """
    fg_net_struct: Optional[Struct] = None

    def __init__(self):
        self.event_pipe = EventPipe(duplex=False)

        self.fg_rx_sock: Optional[socket.socket] = None
        self.fg_rx_cb: Optional[rx_callback_type] = None

        self.fg_tx_sock: Optional[socket.socket] = None
        self.fg_tx_addr: Optional[Tuple[str, int]] = None

        self.rx_proc: Optional[mp.Process] = None

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

    def _rx_process(self):
        while True:
            # Receive up to 1KB of data from FG
            # blocking is fine here since we're in a separate process
            rx_msg, _ = self.fg_rx_sock.recvfrom(1024)
            try:
                s = self.fg_net_struct.parse(rx_msg)
            except ConstError as e:
                raise FGCommunicationError(f'Could not decode FG stream. Is this the right FDM version?\n{e}')

            # Fix FG's radian parsing error :(
            s = fix_fg_radian_parsing(s)

            # Call user method
            if self.event_pipe.is_set() and self.event_pipe.child_poll():
                # only update when we have data to send
                s = self.fg_rx_cb(s, self.event_pipe)
            else:
                print('Receiving FG updates but no data to send', flush=True)
            sys.stdout.flush()
            tx_msg = self.fg_net_struct.build(dict(**s))
            # Send data back to FG
            if self.fg_tx_sock is not None:
                self.fg_tx_sock.sendto(tx_msg, self.fg_tx_addr)
            else:
                print(f'Warning: TX not connected, not sending updates to FG for RX {self.fg_rx_sock.getsockname()}')

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


def strip_end(text: Union[str, ByteString], suffix: Union[str, ByteString]):
    if suffix and text.endswith(suffix):
        return text[:-len(suffix)]
    return text


class PropsConnection:
    def __init__(self, host: str, tcp_port: int):
        self.host = host
        self.port = tcp_port
        # SOCK_STREAM == TCP
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self):
        telnet_addr = (self.host, self.port)
        try:
            self.sock.connect(telnet_addr)
        except Exception as e:
            raise FGConnectionError(f'Could not connect to FlightGear telnet server {telnet_addr}: {e}')
        # force move to the root directory (maybe someone was connected before we were)
        _ = self._send_cmd_get_resp('cd /')

    @staticmethod
    def _telnet_str(in_str: str):
        return f'{in_str}\r\n'.encode()

    def _send_cmd_get_resp(self, cmd_str: str, buflen: int = 512):
        self.sock.sendall(self._telnet_str(cmd_str))
        # FG telnet always ends with a prompt (`cwd`> ), and since we always
        # operate relative to the root directory, it should always be the same prompt
        ending_bytes = b'/> '
        resp_bytes = b''
        while not resp_bytes.endswith(ending_bytes):
            # Loop until FG sends us all the data
            resp_bytes += self.sock.recv(buflen)
        resp_bytes = strip_end(resp_bytes, b'\r\n' + ending_bytes)  # trim the prompt

        resp_str = resp_bytes.decode()
        if resp_str.startswith('-ERR'):
            raise FGCommunicationError(f'Bad telnet command "{cmd_str}". Response: "{resp_str}"')
        return resp_str

    @staticmethod
    def _extract_fg_prop(resp_str: str):
        try:
            match = re.search(r"^(.+)\s=\s+'(.*)'\s+\((.+)\)$", resp_str, flags=re.DOTALL)
        except Exception as e:
            raise FGCommunicationError(f'Could not parse FG telnet response for msg "{resp_str}": {e}')
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
            raise FGCommunicationError(f'Could not auto-convert "{resp_str}": {e}')
        return key_str, value

    def get_prop(self, prop_str: str):
        if not isinstance(prop_str, str):
            raise ValueError(f'prop_str must be a string, not {type(prop_str)}')
        resp_str = self._send_cmd_get_resp(f'get {prop_str}')
        _, value = self._extract_fg_prop(resp_str)
        return value

    def set_prop(self, prop_str: str, value: Any):
        _ = self._send_cmd_get_resp(f'set {prop_str} {str(value)}')
        # We don't care about the response

    def list_props(self, path: str = '/', recurse_limit: Optional[int] = 1):
        path = path.rstrip('/')  # Strip trailing slash to keep things consistent

        resp_list = self._send_cmd_get_resp(f'ls {path}').split('\r\n')
        # List of directories, absolute path
        dir_list = [f'{path}/{s.rstrip("/")}' for s in resp_list if s.endswith('/')]

        prop_dict = {}
        # recursion support
        if recurse_limit is None or recurse_limit > 1:
            dir_list_cwd = copy.deepcopy(dir_list)
            for dir_str in dir_list_cwd:
                # Handle None as a recursion limit
                if recurse_limit is None:
                    new_recurse_limit = None
                else:
                    new_recurse_limit = recurse_limit - 1
                # recursion!
                dir_dict = self.list_props(dir_str, recurse_limit=new_recurse_limit)
                prop_dict = {**prop_dict, **dir_dict['properties']}
                dir_list.remove(dir_str)  # Remove the non-recursed directory
                dir_list += dir_dict['directories']  # add all the newly found directories

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
