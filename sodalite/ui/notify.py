import threading
import time

import urwid

from sodalite.ui import graphics, theme, viewmodel
from sodalite.ui.viewmodel import Topic, Mode

txt = urwid.AttrMap(urwid.Text('', align='center'), urwid.DEFAULT)
_notify_box = theme.DynamicAttrMap(urwid.LineBox(txt, tline=''))
_notify_lock = threading.Lock()
_last_message = ''
_original_footer = None


def show(message, duration=1.5):
    """
    Triggers a notification
    :param message: the message to display
    :param duration: if set to 0, the message is displayed until another call to 'show' or 'clear'
    """
    thread = threading.Thread(target=_show, args=(message, duration,))
    thread.daemon = True
    thread.start()


def _show(message, duration):
    global _last_message
    global _original_footer
    frame = graphics.frame
    loop = graphics.loop
    if _notify_lock.locked() and _last_message == message:
        return
    _notify_lock.acquire()
    if frame.footer != _notify_box:
        _original_footer = frame.footer
    frame.footer = _notify_box
    _notify_box.base_widget.set_text(message)
    loop.draw_screen()
    _last_message = message
    if duration != 0:
        time.sleep(duration)
        frame.footer = _original_footer
        loop.draw_screen()
    _notify_lock.release()


def clear():
    if graphics.frame and graphics.frame.footer == _notify_box:
        graphics.frame.footer = None
        graphics.loop.draw_screen()


def trigger_notifications(model):
    if viewmodel.global_mode == Mode.ASSIGN_CHOOSE_ENTRY:
        show("choose entry", duration=0)
    elif viewmodel.global_mode == Mode.ASSIGN_CHOOSE_KEY:
        show("choose new key", duration=0)
    else:
        clear()


viewmodel.global_mode.register(trigger_notifications, topic=Topic.MODE, immediate_update=False)
