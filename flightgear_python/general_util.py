"""
non-FlightGear-specific utility functionality
"""
import warnings
from typing import Any, Union, ByteString

import multiprocess as mp


class EventPipe:
    """
    Helper abstraction for passing data from a parent process to a child
    process.

    :param duplex: Allow internal pipe to also pass data from child to \
    parent. Recommended to leave at default
    """

    def __init__(self, duplex=True):
        self.event = mp.Event()
        # If not duplex, can only transfer data from parent to child
        self.child_pipe, self.parent_pipe = mp.Pipe(duplex=duplex)

        # function aliases
        self.set = self.event.set
        self.is_set = self.event.is_set
        self.clear = self.event.clear
        self.child_send = self.child_pipe.send
        self.child_poll = self.child_pipe.poll
        self.parent_recv = self.parent_pipe.recv
        self.parent_poll = self.parent_pipe.poll

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


def strip_end(text: Union[str, ByteString], suffix: Union[str, ByteString]) -> Union[str, ByteString]:
    """
    This could be removed if we want to move lowest supported version to 3.9 (.removesuffix())
    sphinx-no-autodoc

    :param text: text to strip the end from
    :param suffix: string to remove from the end
    :return: text with suffix removed
    """
    if suffix and text.endswith(suffix):
        return text[: -len(suffix)]
    return text


def deprecate_rename_wrapper(old_obj: object, old_fn: str, new_obj: object, new_fn: str):
    """
    Small wrapper function to soft-rename objects
    sphinx-no-autodoc
    """

    def new_fn_with_warning(*args, **kwargs):
        # Turn on warnings after the old name has been used
        warnings.simplefilter('default')

        warnings.warn(
            f'{old_obj}:{old_fn} has been renamed to {new_obj}:{new_fn}. Please use the new name',
            DeprecationWarning,
            stacklevel=2,
        )
        return getattr(new_obj, new_fn)(*args, **kwargs)

    setattr(old_obj, old_fn, new_fn_with_warning)
