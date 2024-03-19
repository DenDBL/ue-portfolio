import unreal
import sys
import os

sys.path.append(os.environ['CTENTACULO_LOCATION'])

import Source.ui.unreal_stylesheet as unreal_stylesheet
from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


def __qt_app_tick(delta_seconds):
    for window in opened_windows:
        window.eventTick(delta_seconds)


def __qt_app_quit():
    unreal.unregister_slate_post_tick_callback(tick_handle)
    print('QUITED')


def __qt_window_closed(window=None):
    if window in opened_windows:
        opened_windows.remove(window)
        existing_windows[type(window)] = None
        window.close()
        print(window, ' destroyed')
        del window


unreal_app = QApplication(sys.argv)

unreal_stylesheet.setup()

tick_handle = unreal.register_slate_post_tick_callback(__qt_app_tick)
unreal_app.aboutToQuit.connect(__qt_app_quit)
existing_windows = {}
opened_windows = []


def _spawn_qt_window(desired_window_class=None):
    window = existing_windows.get(desired_window_class, None)

    if not window:
        window = desired_window_class()
        existing_windows[desired_window_class] = window
        window.aboutToClose = __qt_window_closed
    if window not in opened_windows:
        opened_windows.append(window)
    window.show()
    window.activateWindow()

    return window


def show_window(window_class):

    return _spawn_qt_window(window_class)
