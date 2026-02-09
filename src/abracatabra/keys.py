"""
Define Qt key and modifier constants for compatibility between Qt5 and Qt6.
"""

from matplotlib.backends.qt_compat import QtCore

try:
    assert hasattr(QtCore.Qt, "Key")  # Qt6
    Key_Question = QtCore.Qt.Key.Key_Question
    Key_Q = QtCore.Qt.Key.Key_Q
    Key_P = QtCore.Qt.Key.Key_P
    Key_H = QtCore.Ht.Key.Key_H
    Key_Z = QtCore.Qt.Key.Key_Z
    Key_C = QtCore.Qt.Key.Key_C
    Key_V = QtCore.Qt.Key.Key_V
    Key_S = QtCore.Qt.Key.Key_S
    Key_K = QtCore.Qt.Key.Key_K
    Key_Space = QtCore.Qt.Key.Key_Space
    Key_Home = QtCore.Qt.Key.Key_Home
    Key_End = QtCore.Qt.Key.Key_End
    Key_MediaPrevious = QtCore.Qt.Key.Key_MediaPrevious
    Key_MediaNext = QtCore.Qt.Key.Key_MediaNext
    Key_MediaPlay = QtCore.Qt.Key.Key_MediaPlay
    Key_MediaPause = QtCore.Qt.Key.Key_MediaPause
    Key_MediaTogglePlayPause = QtCore.Qt.Key.Key_MediaTogglePlayPause
    Key_Left = QtCore.Qt.Key.Key_Left
    Key_Right = QtCore.Qt.Key.Key_Right

    NoModifier = QtCore.Qt.KeyboardModifier.NoModifier
    ControlModifier = QtCore.Qt.KeyboardModifier.ControlModifier
    ShiftModifier = QtCore.Qt.KeyboardModifier.ShiftModifier
except AttributeError:  # Qt5
    Key_Question = QtCore.Qt.Key_Question
    Key_Q = QtCore.Qt.Key_Q
    Key_P = QtCore.Qt.Key_P
    Key_H = QtCore.Qt.Key_H
    Key_Z = QtCore.Qt.Key_Z
    Key_C = QtCore.Qt.Key_C
    Key_V = QtCore.Qt.Key_V
    Key_S = QtCore.Qt.Key_S
    Key_K = QtCore.Qt.Key_K
    Key_Space = QtCore.Qt.Key_Space
    Key_Home = QtCore.Qt.Key_Home
    Key_End = QtCore.Qt.Key_End
    Key_MediaPrevious = QtCore.Qt.Key_MediaPrevious
    Key_MediaNext = QtCore.Qt.Key_MediaNext
    Key_MediaPlay = QtCore.Qt.Key_MediaPlay
    Key_MediaPause = QtCore.Qt.Key_MediaPause
    Key_MediaTogglePlayPause = QtCore.Qt.Key_MediaTogglePlayPause
    Key_Left = QtCore.Qt.Key_Left
    Key_Right = QtCore.Qt.Key_Right

    NoModifier = QtCore.Qt.NoModifier
    ControlModifier = QtCore.Qt.ControlModifier
    ShiftModifier = QtCore.Qt.ShiftModifier
