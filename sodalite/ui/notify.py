import threading
import time
from typing import Union, Tuple, Optional

import urwid
from urwid import AttrSpec

from sodalite.ui import graphics, theme, viewmodel
from sodalite.ui.viewmodel import Mode
from sodalite.util import pubsub

txt = urwid.AttrMap(urwid.Text('', align='center'), urwid.DEFAULT)
_notify_box = theme.DynamicAttrMap(urwid.LineBox(txt, tline=''))
_notify_lock = threading.Lock()
_last_message: Optional[Union[str, Tuple[AttrSpec, str]]] = ''
_original_footer = None


def show(message: Union[str, Tuple[AttrSpec, str]], duration: float = 1.5) -> None:
    """
    Triggers a notification
    :param message: the message to display
    :param duration: if set to 0, the message is displayed until another call to 'show' or 'clear'
    """
    thread = threading.Thread(target=_show, args=(message, duration,), daemon=True)
    thread.start()


def show_error(message: str, duration: float = 1.5) -> None:
    """
    Triggers a notification
    :param message: the error to display
    :param duration: if set to 0, the message is displayed until another call to 'show' or 'clear'
    """
    show((AttrSpec(theme.forbidden + ',bold', '', colors=16), message), duration)


def _show(message: Union[str, Tuple[AttrSpec, str]], duration: float) -> None:
    global _last_message
    global _original_footer
    frame = graphics.frame
    if _notify_lock.locked() and _last_message == message:
        return
    _notify_lock.acquire()
    if frame.footer != _notify_box:
        _original_footer = frame.footer
    frame.footer = _notify_box
    _notify_box.base_widget.set_text(message)
    graphics.draw_screen()
    _last_message = message
    if duration != 0:
        time.sleep(duration)
        frame.footer = _original_footer
        _last_message = None
        graphics.draw_screen()
    _notify_lock.release()


def clear() -> None:
    if graphics.frame and graphics.frame.footer == _notify_box:
        graphics.frame.footer = None
        graphics.draw_screen()


def trigger_notifications(mode: Mode) -> None:
    if viewmodel.global_mode == Mode.ASSIGN_CHOOSE_ENTRY:
        show("choose entry", duration=0)
    elif viewmodel.global_mode == Mode.ASSIGN_CHOOSE_KEY:
        show("choose new key", duration=0)
    else:
        clear()


def setup():
    pubsub.mode_connect(trigger_notifications)
