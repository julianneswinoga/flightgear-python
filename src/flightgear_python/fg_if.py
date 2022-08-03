import socket
import sys
import multiprocessing as mp
from typing import Callable

from construct import ConstError


class EventPipe:
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
        self.parent_pipe.send(*args, **kwargs)
        self.set()

    def child_recv(self, *args, **kwargs):
        msg = self.child_pipe.recv(*args, **kwargs)
        self.clear()
        return msg


class FGConnection:
    fg_net_struct = None

    def __init__(self):
        self.event_pipe = EventPipe(duplex=False)

        self.fg_rx_sock = None
        self.fg_rx_cb = None

        self.fg_tx_sock = None
        self.fg_tx_addr = None

        self.rx_proc = None

    def connect_rx(self, fg_host: str, fg_port: int, rx_cb: Callable):
        self.fg_rx_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        fg_rx_addr = (fg_host, fg_port)
        self.fg_rx_sock.bind(fg_rx_addr)
        self.fg_rx_cb = rx_cb
        print(f'Connected to FlightGear RX socket {fg_port}')

        return self.event_pipe

    def connect_tx(self, fg_host: str, fg_port: int):
        self.fg_tx_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.fg_tx_addr = (fg_host, fg_port)
        print(f'Connected to FlightGear TX socket {fg_port}')

    def _rx_process(self):
        while True:
            # Receive up to 1KB of data from FG
            rx_msg, _ = self.fg_rx_sock.recvfrom(1024)
            try:
                s = self.fg_net_struct.parse(rx_msg)
            except ConstError as e:
                raise AssertionError(f'Could not decode FG stream. Is this the right FDM version?\n{e}')
            # Call user method
            if self.event_pipe.is_set() and self.event_pipe.child_poll():
                # only update when we have data to send
                s = self.fg_rx_cb(s, self.event_pipe)
            else:
                print('Receiving FG updates but no data to send', flush=True)
            sys.stdout.flush()
            tx_msg = self.fg_net_struct.build(dict(**s))
            # Send data back to FG
            self.fg_tx_sock.sendto(tx_msg, self.fg_tx_addr)

    def start(self):
        self.rx_proc = mp.Process(target=self._rx_process)
        self.rx_proc.start()

    def stop(self):
        self.rx_proc.terminate()


class FDMConnection(FGConnection):
    def __init__(self, fdm_version):
        super().__init__()
        if fdm_version == 24:
            from .fdm_v24 import fdm_struct
        elif fdm_version == 25:
            from .fdm_v25 import fdm_struct
        else:
            raise NotImplementedError(f'FDM version {fdm_version} not supported yet')
        self.fg_net_struct = fdm_struct
