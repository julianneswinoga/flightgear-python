"""
Main FlightGear interface module
"""
import copy
import socket
import sys
import re
from typing import Any, ByteString, Callable, Dict, Optional, Tuple, Union, List, NamedTuple

import multiprocess as mp
import requests

from construct import ConstError, Struct, Container, Construct, Int32ub, Int32ul

from .general_util import EventPipe, strip_end, deprecate_rename_wrapper
from .fg_util import FGConnectionError, FGCommunicationError, fix_fg_radian_parsing
from .fdm_v24 import fdm_struct as fdm_struct_v24
from .fdm_v25 import fdm_struct as fdm_struct_v25
from .ctrls_v27 import ctrls_struct as ctrls_struct_v27
from .gui_v8 import gui_struct as gui_struct_v8

rx_callback_type = Callable[[Container, EventPipe], Optional[Container]]
"""
RX callback function type, signature should be:

.. code-block:: python

    def rx_cb(fdm_data: Construct.Container, event_pipe: EventPipe) -> Optional[Construct.Container]:
"""


class FGConnection:
    """
    Base class for FlightGear connections
    sphinx-no-autodoc
    :param rx_timeout_s: Optional timeout value in seconds when receiving data
    """

    # These are filled from the child class
    fg_net_struct: Optional[Struct] = None
    fg_auto_partial_parse: Optional['PartialParseSwitchStruct'] = None

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
        ``--native-fdm=socket,out,30,localhost,5501,udp``)
        :param rx_cb: Callback function, called whenever we receive data from FG.\
        Function signature should follow :attr:`rx_callback_type`
        :return: ``EventPipe`` so that data can be passed from the parent process\
        to the callback process
        """
        # TODO: Support TCP server so that we only need 1 port
        self.fg_rx_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.fg_rx_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        fg_rx_addr = (fg_host, fg_port)
        try:
            self.fg_rx_sock.bind(fg_rx_addr)
        except Exception as e:
            raise FGConnectionError(f'Could not bind to {fg_rx_addr}: {e}')
        self.fg_rx_sock.settimeout(self.rx_timeout_s)
        # See note in _fg_packet_roundtrip()::recvfrom()
        self.fg_rx_cb = rx_cb

        return self.event_pipe

    def connect_tx(self, fg_host: str, fg_port: int):
        """
        Connect to a UDP input of FlightGear

        :param fg_host: IP address of FG (usually localhost)
        :param fg_port: Port of the input socket (i.e. the ``5502`` from\
        ``--native-fdm=socket,in,30,localhost,5502,udp``)
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
        except BlockingIOError as e:
            """
            On Linux, setblocking(True) resets the timeout value to infinite (effectively
            calling settimeout(0)). But on Windows you need to _explicitly_ call
            setblocking(True) AFTER settimeout() or else the socket is nonblocking
            (and will error out with BlockingIOError: [WinError 10035] A non-blocking
            socket operation could not be completed immediately). So instead of
            checking the platform and optionally calling setblocking() (bleh) we catch
            the error, call setblocking(True) and then try again.
            """
            if '10035' in str(e):
                self.fg_rx_sock.setblocking(True)
                return
            else:
                raise e

        # Auto-version logic
        if self.fg_auto_partial_parse and self.fg_net_struct is None:
            # We lazily create the actual struct that will be used for parsing
            self.fg_net_struct = self.fg_auto_partial_parse.resolve(rx_msg)

        try:
            s: Container = self.fg_net_struct.parse(rx_msg)
        except ConstError as e:
            raise FGCommunicationError(f'Could not decode FG stream. Did you set the right version?\n{e}') from e

        if isinstance(self, FDMConnection):
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

        self.event_pipe.child_send((True,))  # Signal to parent that child is running
        while True:
            self._fg_packet_roundtrip()

    def start(self):
        """
        Start the RX/TX loop with FlightGear
        """
        self.rx_proc = mp.Process(target=self._rx_process)
        self.rx_proc.daemon = True  # rx_proc should exit when parent exits
        self.rx_proc.start()
        _ = self.event_pipe.parent_recv()  # Wait for child to actually run

    def stop(self):
        """
        Stop the RX/TX loop
        """
        self.rx_proc.terminate()


class PartialParseSwitchStruct:
    """
    A utility class that allows runtime switching of which version of a struct
    is used to parse an incoming message. We use this (complexity) instead of
    construct's conditional utilities because it makes looking at the individual
    struct versions a bit less overwhelming, and easier to compare.
    sphinx-no-autodoc
    :param partial_parse_construct: The Construct that will be used to switch which
    version of the Struct is resolved
    :param replacement_full_structs: Mapping of struct versions to Structs
    """

    def __init__(self, partial_parse_construct: Construct, replacement_full_structs: Dict[Any, Struct]):
        self.partial_parse_construct = partial_parse_construct
        self.replacement_full_structs = replacement_full_structs

    def resolve(self, message: bytes) -> Struct:
        """
        Resolve a message to a full Struct
        :param message: The message to partially parse
        :return: The full Struct based on the partial parsing of the message
        """
        version: Any = self.partial_parse_construct.parse(message)
        supported_version_list = list(self.replacement_full_structs.keys())
        if version not in supported_version_list:
            raise FGCommunicationError(
                f'Auto-version detected {version} is not in the list of supported versions: {supported_version_list}'
            )
        return self.replacement_full_structs[version]


class FDMConnection(FGConnection):
    """
    FlightGear Flight Dynamics Model Connection

    :param fdm_version: Net FDM version (24, 25, or None for auto-detection)
    :param rx_timeout_s: Optional timeout value in seconds when receiving data
    """

    def __init__(self, fdm_version: Optional[int] = None, rx_timeout_s: float = 2.0):
        super().__init__(rx_timeout_s=rx_timeout_s)
        fdm_support_dict: Dict[int, Struct] = {
            24: fdm_struct_v24,
            25: fdm_struct_v25,
        }

        if fdm_version is None:
            self.fg_auto_partial_parse = PartialParseSwitchStruct(
                partial_parse_construct=Int32ub,
                replacement_full_structs=fdm_support_dict,
            )
        else:
            self.fg_net_struct = fdm_support_dict.get(fdm_version)
            if self.fg_net_struct is None:
                raise NotImplementedError(f'Manually specified FDM version {fdm_version} not supported yet')


class CtrlsConnection(FGConnection):
    """
    FlightGear Controls Connection

    :param ctrls_version: Net Ctrls version (27, or None for auto-detection)
    :param rx_timeout_s: Optional timeout value in seconds when receiving data
    """

    def __init__(self, ctrls_version: Optional[int] = None, rx_timeout_s: float = 2.0):
        super().__init__(rx_timeout_s=rx_timeout_s)
        ctrls_support_dict: Dict[int, Struct] = {
            27: ctrls_struct_v27,
        }
        if ctrls_version is None:
            self.fg_auto_partial_parse = PartialParseSwitchStruct(
                partial_parse_construct=Int32ub,
                replacement_full_structs=ctrls_support_dict,
            )
        else:
            self.fg_net_struct = ctrls_support_dict.get(ctrls_version)
            if self.fg_net_struct is None:
                raise NotImplementedError(f'Manually specified Controls version {ctrls_version} not supported yet')


class GuiConnection(FGConnection):
    """
    FlightGear GUI Connection

    :param gui_version: Net GUI version (8, or None for auto-detection)
    :param rx_timeout_s: Optional timeout value in seconds when receiving data
    """

    def __init__(self, gui_version: Optional[int] = None, rx_timeout_s: float = 2.0):
        super().__init__(rx_timeout_s=rx_timeout_s)
        gui_support_dict: Dict[int, Struct] = {
            8: gui_struct_v8,
        }
        if gui_version is None:
            self.fg_auto_partial_parse = PartialParseSwitchStruct(
                partial_parse_construct=Int32ul,
                replacement_full_structs=gui_support_dict,
            )
        else:
            self.fg_net_struct = gui_support_dict.get(gui_version)
            if self.fg_net_struct is None:
                raise NotImplementedError(f'Manually specified GUI version {gui_version} not supported yet')


class PropertyTreeValue(NamedTuple):
    """
    Internal representation for working with values from the property tree
    sphinx-no-autodoc
    """

    absolute_path: str
    value_str: str
    type_str: str


class PropsConnectionBase:
    """
    Base class for interacting with the properties interface.
    Not to be instantiated directly.
    sphinx-no-autodoc
    """

    @staticmethod
    def _auto_convert_fg_prop(value_str: str, type_str: str) -> Any:
        convert_fn = {
            'bool': bool,
            'int': int,
            'string': str,
            'double': float,
            'float': float,
        }.get(type_str, lambda x: x)
        try:
            value = convert_fn(value_str)
        except ValueError as e:
            raise FGCommunicationError(f'Could not auto-convert "{value_str}" to "{type_str}": {e}') from e
        return value

    @staticmethod
    def check_and_normalize_prop_path(path: str) -> str:
        """
        Make sure the path is always absolute and strip trailing slashes
        sphinx-no-autodoc
        """
        if not path.startswith('/'):
            raise ValueError(f'Path must be absolute (start with /): {path}')
        path = path.rstrip('/') if path != "/" else path  # Strip trailing slash to keep things consistent
        return path

    def get_values_and_dirs(self, path: str) -> Tuple[List[PropertyTreeValue], List[str]]:
        raise NotImplementedError('Function needs to be implemented in subclasses')

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
        path = self.check_and_normalize_prop_path(path)

        val_list, dir_list = self.get_values_and_dirs(path)

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
        for val_entry in val_list:
            converted_value = self._auto_convert_fg_prop(val_entry.value_str, val_entry.type_str)
            prop_dict[val_entry.absolute_path] = converted_value

        # Returned paths are absolute
        rtn_dict = {
            # sort the list because we're nice
            'directories': dir_list,
            'properties': prop_dict,
        }
        return rtn_dict


deprecate_rename_wrapper(sys.modules[__name__], 'PropsConnection', sys.modules[__name__], 'TelnetConnection')


class TelnetConnection(PropsConnectionBase):
    """
    FlightGear Telnet Interface Connection (also known as the property interface).
    See https://wiki.flightgear.org/Telnet_usage for general details.

    :param host: IP address of FG (usually localhost)
    :param tcp_port: Port of the telnet socket (i.e. the ``5500`` from\
        ``--telnet=socket,bi,60,localhost,5500,tcp``)
    :param rx_timeout_s: Optional timeout value in seconds when receiving data
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

        self.sock.settimeout(self.rx_timeout_s)
        # force move to the root directory (maybe someone was connected before we were)
        _ = self._send_cmd_get_resp('cd /')

    @staticmethod
    def _telnet_str(in_str: str) -> ByteString:
        return f'{in_str}\r\n'.encode()

    def _send_cmd_get_resp(self, cmd_str: str, buflen: int = 512) -> str:
        self.sock.sendall(self._telnet_str(cmd_str))

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
    def _telnet_resp_to_val(resp_str: str) -> Tuple[str, str, str]:
        try:
            match = re.search(r"^(.+)\s=\s+'(.*)'\s+\((.+)\)$", resp_str, flags=re.DOTALL)
        except Exception as e:
            raise FGCommunicationError(f'Could not parse FG telnet response for msg "{resp_str}": {e}') from e
        if match is None:
            raise FGCommunicationError(f'Could not parse FG telnet response for msg "{resp_str}"')
        key_str = match.group(1)
        value_str = match.group(2)
        type_str = match.group(3)
        return key_str, value_str, type_str

    def get_prop(self, prop_str: str) -> Any:
        """
        Get a property from FlightGear.

        :param prop_str: Location of the property, should always be relative to\
            the root (``/``)
        :return: The value of the property. If FG tells us what the type is we \
            will pre-convert it (i.e. make an int from a string)
        """
        prop_str = self.check_and_normalize_prop_path(prop_str)
        resp_str = self._send_cmd_get_resp(f'get {prop_str}')
        abs_path, value_str, type_str = self._telnet_resp_to_val(resp_str)
        converted_value = self._auto_convert_fg_prop(value_str, type_str)
        return converted_value

    def set_prop(self, prop_str: str, value: Any):
        """
        Set a property in FlightGear.

        :param prop_str: Location of the property, should always be relative to\
            the root (``/``)
        :param value: Value to set the property to. Must be convertible to ``str``
        """
        prop_str = self.check_and_normalize_prop_path(prop_str)
        _ = self._send_cmd_get_resp(f'set {prop_str} {str(value)}')
        # We don't care about the response

    def get_values_and_dirs(self, path: str) -> Tuple[List[PropertyTreeValue], List[str]]:
        """
        Internal method to populate a shared property tree data structure
        sphinx-no-autodoc
        """
        resp_list = self._send_cmd_get_resp(f'ls {path}').split('\r\n')
        val_list: List[PropertyTreeValue] = []
        dir_list: List[str] = []
        for prop_entry in resp_list:
            if '=' in prop_entry:
                # prepend the key with the working directory, keep naming consistent
                abs_path, value_str, type_str = self._telnet_resp_to_val(f'{path}/{prop_entry.rstrip("/")}')
                val_list.append(
                    PropertyTreeValue(
                        absolute_path=abs_path,
                        value_str=value_str,
                        type_str=type_str,
                    )
                )
            elif prop_entry.endswith('/'):
                dir_list.append(f'{path}/{prop_entry.rstrip("/")}')
            else:
                raise FGCommunicationError(f'Unknown Telnet response: {prop_entry}')
        return val_list, dir_list


class HTTPConnection(PropsConnectionBase):
    """
    FlightGear HTTP Interface Connection (also known as the property interface).
    See https://wiki.flightgear.org/Property_Tree_Servers for general details.

    :param host: IP address of FG (usually localhost)
    :param tcp_port: Port of the telnet socket (i.e. the ``5050`` from\
        ``--httpd=5050``)
    :param timeout_s: Optional timeout value in seconds for the HTTP connection
    """

    def __init__(self, host: str, tcp_port: int, timeout_s: float = 2.0):
        self.url = f'http://{host}:{tcp_port}/json'
        self.session = requests.Session()
        self.timeout_s = timeout_s

    def request_shim(self, method: str, url: str, *args, **kwargs) -> requests.Response:
        """
        Shim layer over session.request so we can set default options and handle errors in a unified fashion
        sphinx-no-autodoc

        :param method: Directly copied from :meth:`requests.Session.request()`
        :param url: Directly copied from :meth:`requests.Session.request()`
        """
        try:
            return self.session.request(method, url, *args, timeout=self.timeout_s, **kwargs)
        except requests.exceptions.ConnectionError:
            raise FGConnectionError(f'Problem connecting to {self.url}')

    def get_prop(self, prop_str: str) -> Any:
        """
        Get a property from FlightGear.

        :param prop_str: Location of the property, should always be relative to\
            the root (``/``)
        :return: The value of the property. If FG tells us what the type is we \
            will pre-convert it (i.e. make an int from a string)
        """
        prop_str = self.check_and_normalize_prop_path(prop_str)
        resp_json = self.request_shim('GET', self.url + prop_str).json()
        converted_value = self._auto_convert_fg_prop(resp_json['value'], resp_json['type'])
        return converted_value

    def set_prop(self, prop_str: str, value: Any):
        """
        Set a property in FlightGear.

        :param prop_str: Location of the property, should always be relative to\
            the root (``/``)
        :param value: Value to set the property to. Must be convertible to ``str``
        """
        prop_str = self.check_and_normalize_prop_path(prop_str)
        # Fetch the type of the property
        resp_json = self.request_shim('GET', self.url + prop_str).json()
        # Set the property
        data = {
            'path': prop_str,
            'value': str(value),
            'type': resp_json['type'],
        }
        self.request_shim('POST', self.url + prop_str, json=data)
        # We don't care about the response

    def get_values_and_dirs(self, path: str) -> Tuple[List[PropertyTreeValue], List[str]]:
        """
        Internal method to populate a shared property tree data structure
        sphinx-no-autodoc
        """
        resp_json = self.request_shim('GET', self.url + path).json()
        if resp_json['nChildren'] == 0:
            return [], []
        resp_list = resp_json['children']
        # extract of directories, absolute path
        val_list: List[PropertyTreeValue] = []
        dir_list: List[str] = []
        for prop_entry in resp_list:
            if 'value' not in prop_entry.keys():
                # Sometimes there's weird no-value things in the property tree
                prop_entry['value'] = None

            if prop_entry['nChildren'] > 0:
                dir_list.append(prop_entry['path'].rstrip('/'))
            else:
                val_list.append(
                    PropertyTreeValue(
                        absolute_path=prop_entry['path'],
                        value_str=prop_entry['value'],
                        type_str=prop_entry['type'],
                    )
                )
        return val_list, dir_list
