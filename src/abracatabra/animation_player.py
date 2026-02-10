from typing import Callable, Optional, Self
from matplotlib.backends.qt_compat import QtWidgets, QtCore, QtGui

from . import keys

# from PySide6 import QtWidgets, QtCore, QtGui


class AnimationPlayer(QtWidgets.QWidget):
    """
    A simple player widget for controlling animations. This is a singleton class,
    meaning that only one instance can exist at a time. It provides basic media
    player controls (play/pause, step forward/backward, jump to start/end). It
    controls all windows within the application that have registered animation
    callbacks.

    Methods:
        `setup`: Sets up the animation player with the given parameters.
        `step_frame`: Steps the animation forward by one step if not paused.
    Static Methods:
        `instance`: Returns the singleton instance of the AnimationPlayer.
    """

    _instance: Optional[Self] = None
    help_text = """Animation Player Controls:
    k or Space: Play/Pause
    Home: Restart
    End: Go to last frame
    LeftArrow: Step back 1 frame
    RightArrow: Step forward 1 frame
    Ctrl+LeftArrow: Jump back
    Ctrl+RightArrow: Jump forward

    Media_Play/Pause: Play/Pause
    Media_Previous: Jump back
    Media_Next: Jump forward
    Ctrl+Media_Previous: Step back 1 frame
    Ctrl+Media_Next: Step forward 1 frame
    """
    shortcuts: dict[str, list[QtGui.QKeySequence]] = {
        "toggle_play_pause": [
            QtGui.QKeySequence(keys.Key_K),
            QtGui.QKeySequence(keys.Key_Space),
            QtGui.QKeySequence(keys.Key_MediaTogglePlayPause),
            QtGui.QKeySequence(keys.Key_MediaPlay),
            QtGui.QKeySequence(keys.Key_MediaPause),
        ],
        "restart": [QtGui.QKeySequence(keys.Key_Home)],
        "go_to_end": [QtGui.QKeySequence(keys.Key_End)],
        "step_backward": [
            QtGui.QKeySequence(keys.Key_Left),
            QtGui.QKeySequence(keys.ControlModifier | keys.Key_MediaPrevious),
        ],
        "jump_backward": [
            QtGui.QKeySequence(keys.ControlModifier | keys.Key_Left),
            QtGui.QKeySequence(keys.Key_MediaPrevious),
        ],
        "step_forward": [
            QtGui.QKeySequence(keys.Key_Right),
            QtGui.QKeySequence(keys.ControlModifier | keys.Key_MediaNext),
        ],
        "jump_forward": [
            QtGui.QKeySequence(keys.ControlModifier | keys.Key_Right),
            QtGui.QKeySequence(keys.Key_MediaNext),
        ],
        "save_animation": [QtGui.QKeySequence(keys.ControlModifier | keys.Key_S)],
    }

    def __init__(self, parent: Optional[QtWidgets.QWidget] = None):
        """
        Initializes the AnimationPlayer widget.
        """
        if AnimationPlayer.instance():
            raise RuntimeError("Only one instance of AnimationPlayer is allowed.")
        AnimationPlayer._instance = self
        super().__init__(parent)

        self.paused = True
        self.current_frame = 0

        # populate with default values; will be updated in setup()
        self.end_frame = 0
        self.ts = 0.0
        s = str(self.ts)
        self.t_decimals = len(s.split(".")[-1]) if "." in s else 2
        end_time = self.end_frame * self.ts
        self.t_digits = len(f"{end_time:.{self.t_decimals}f}")
        self.end_time = f"{end_time:>{self.t_digits}.{self.t_decimals}f}"

        self.step = 10
        self.jump = 10
        self.update_callback = lambda i: None

        main_layout = QtWidgets.QVBoxLayout()
        self.setLayout(main_layout)
        self.std_icon = self.style().standardIcon

        # buttons
        self.play_button = QtWidgets.QPushButton()
        self.play_button.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
        icon = self.std_icon(QtWidgets.QStyle.StandardPixmap.SP_MediaPlay)
        self.play_button.setIcon(icon)
        self.play_button.setToolTip("Play (k/Space)")
        self.play_button.clicked.connect(self._on_play_clicked)
        # shortcuts = [
        #     QtGui.QKeySequence(keys.Key_K),
        #     QtGui.QKeySequence(keys.Key_Space),
        #     QtGui.QKeySequence(keys.Key_MediaTogglePlayPause),
        #     QtGui.QKeySequence(keys.Key_MediaPlay),
        #     QtGui.QKeySequence(keys.Key_MediaPause),
        # ]
        # self.play_shortcuts = []
        # for shortcut in shortcuts:
        #     play_shortcut = QtGui.QShortcut(shortcut, self)
        #     play_shortcut.activated.connect(self.play_button.click)
        #     self.play_shortcuts.append(play_shortcut)

        self.restart_button = QtWidgets.QPushButton()
        self.restart_button.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
        icon = self.std_icon(QtWidgets.QStyle.StandardPixmap.SP_MediaSkipBackward)
        self.restart_button.setIcon(icon)
        self.restart_button.setToolTip("Restart animation (Home)")
        self.restart_button.clicked.connect(self._on_restart_clicked)
        # self.restart_shortcut = QtGui.QShortcut(QtGui.QKeySequence(keys.Key_Home), self)
        # self.restart_shortcut.activated.connect(self.restart_button.click)

        self.end_button = QtWidgets.QPushButton()
        self.end_button.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
        icon = self.std_icon(QtWidgets.QStyle.StandardPixmap.SP_MediaSkipForward)
        self.end_button.setIcon(icon)
        self.end_button.setToolTip("Go to end of animation (End)")
        self.end_button.clicked.connect(self._on_end_clicked)
        # self.end_shortcut = QtGui.QShortcut(QtGui.QKeySequence(keys.Key_End), self)
        # self.end_shortcut.activated.connect(self.end_button.click)

        self.prev_button = QtWidgets.QPushButton()
        self.prev_button.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
        icon = self.std_icon(QtWidgets.QStyle.StandardPixmap.SP_ArrowBack)
        self.prev_button.setIcon(icon)
        self.prev_button.setToolTip("Step back 1 frame (LeftArrow)")
        self.prev_button.clicked.connect(self._on_prev_clicked)
        self.prev_button.setAutoRepeat(True)
        self.prev_button.setAutoRepeatDelay(500)
        self.prev_button.setAutoRepeatInterval(50)
        # shortcuts = [
        #     QtGui.QKeySequence(keys.Key_Left),
        #     QtGui.QKeySequence(keys.ControlModifier | keys.Key_MediaPrevious),
        # ]
        # self.prev_shortcuts = []
        # for shortcut in shortcuts:
        #     prev_shortcut = QtGui.QShortcut(shortcut, self)
        #     prev_shortcut.activated.connect(self.prev_button.click)
        #     self.prev_shortcuts.append(prev_shortcut)

        self.jump_back_button = QtWidgets.QPushButton()
        self.jump_back_button.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
        icon = self.std_icon(QtWidgets.QStyle.StandardPixmap.SP_MediaSeekBackward)
        self.jump_back_button.setIcon(icon)
        self.jump_back_button.setToolTip("Jump back 0 frames (Ctrl+LeftArrow)")
        self.jump_back_button.clicked.connect(self._on_jump_back_clicked)
        self.jump_back_button.setAutoRepeat(self.prev_button.autoRepeat())
        self.jump_back_button.setAutoRepeatDelay(self.prev_button.autoRepeatDelay())
        self.jump_back_button.setAutoRepeatInterval(
            self.prev_button.autoRepeatInterval() * 2
        )
        # shortcuts = [
        #     QtGui.QKeySequence(keys.ControlModifier | keys.Key_Left),
        #     QtGui.QKeySequence(keys.Key_MediaPrevious),
        # ]
        # self.jump_back_shortcuts = []
        # for shortcut in shortcuts:
        #     jump_back_shortcut = QtGui.QShortcut(shortcut, self)
        #     jump_back_shortcut.activated.connect(self.jump_back_button.click)
        #     self.jump_back_shortcuts.append(jump_back_shortcut)

        self.next_button = QtWidgets.QPushButton()
        self.next_button.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
        icon = self.std_icon(QtWidgets.QStyle.StandardPixmap.SP_ArrowForward)
        self.next_button.setIcon(icon)
        self.next_button.setToolTip("Step forward 1 frame (RightArrow)")
        self.next_button.clicked.connect(self._on_next_clicked)
        self.next_button.setAutoRepeat(self.prev_button.autoRepeat())
        self.next_button.setAutoRepeatDelay(self.prev_button.autoRepeatDelay())
        self.next_button.setAutoRepeatInterval(self.prev_button.autoRepeatInterval())
        # shortcuts = [
        #     QtGui.QKeySequence(keys.Key_Right),
        #     QtGui.QKeySequence(keys.ControlModifier | keys.Key_MediaNext),
        # ]
        # self.next_shortcuts = []
        # for shortcut in shortcuts:
        #     next_shortcut = QtGui.QShortcut(shortcut, self)
        #     next_shortcut.activated.connect(self.next_button.click)
        #     self.next_shortcuts.append(next_shortcut)

        self.jump_forward_button = QtWidgets.QPushButton()
        self.jump_forward_button.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
        icon = self.std_icon(QtWidgets.QStyle.StandardPixmap.SP_MediaSeekForward)
        self.jump_forward_button.setIcon(icon)
        self.jump_forward_button.setToolTip("Jump forward 0 frames (Ctrl+RightArrow)")
        self.jump_forward_button.clicked.connect(self._on_jump_forward_clicked)
        self.jump_forward_button.setAutoRepeat(self.prev_button.autoRepeat())
        self.jump_forward_button.setAutoRepeatDelay(
            self.jump_back_button.autoRepeatDelay()
        )
        self.jump_forward_button.setAutoRepeatInterval(
            self.jump_back_button.autoRepeatInterval()
        )
        # shortcuts = [
        #     QtGui.QKeySequence(keys.ControlModifier | keys.Key_Right),
        #     QtGui.QKeySequence(keys.Key_MediaNext),
        # ]
        # self.jump_forward_shortcuts = []
        # for shortcut in shortcuts:
        #     jump_forward_shortcut = QtGui.QShortcut(shortcut, self)
        #     jump_forward_shortcut.activated.connect(self.jump_forward_button.click)
        #     self.jump_forward_shortcuts.append(jump_forward_shortcut)

        self.save_button = QtWidgets.QPushButton()
        self.save_button.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
        icon = self.std_icon(QtWidgets.QStyle.StandardPixmap.SP_DialogSaveButton)
        self.save_button.setIcon(icon)
        self.save_button.setToolTip("Save animation videos (Ctrl+s)")
        # shortcut = QtGui.QKeySequence(keys.ControlModifier | keys.Key_S)
        # self.save_shortcut = QtGui.QShortcut(shortcut, self)
        # self.save_shortcut.activated.connect(self.save_button.click)

        # slider
        self.slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(0)
        self.slider.setValue(0)
        self.slider.valueChanged.connect(self._on_slider_changed)
        # self.slider.setTracking(False)  # only update on release, not while dragging
        self.slider.setFocusPolicy(QtCore.Qt.FocusPolicy.ClickFocus)

        # spin box

        self.spin_box = QtWidgets.QSpinBox()
        self.spin_box.setMinimum(0)
        self.spin_box.setMaximum(0)
        self.spin_box.setValue(0)
        self.spin_box.setKeyboardTracking(False)
        self.spin_box.valueChanged.connect(self._on_spinbox_changed)
        self.spin_box.editingFinished.connect(self._on_spinbox_changed)

        # labels
        frame_label_1 = QtWidgets.QLabel("Frame:")
        self.frame_label_2 = QtWidgets.QLabel("/ 0")

        self.time_label = QtWidgets.QLabel()
        self._set_time_label()

        # layouts
        top_row = QtWidgets.QHBoxLayout()
        top_row.addWidget(self.jump_back_button)
        top_row.addWidget(self.prev_button)
        top_row.addWidget(self.slider)
        top_row.addWidget(self.next_button)
        top_row.addWidget(self.jump_forward_button)
        main_layout.addLayout(top_row)

        bottom_row = QtWidgets.QHBoxLayout()
        bottom_row.addWidget(self.play_button)
        bottom_row.addWidget(self.restart_button)
        bottom_row.addWidget(self.end_button)
        bottom_row.addWidget(self.save_button)
        bottom_row.addItem(
            QtWidgets.QSpacerItem(0, 0, QtWidgets.QSizePolicy.Policy.Expanding)
        )
        bottom_row.addWidget(frame_label_1)
        bottom_row.addWidget(self.spin_box)
        bottom_row.addWidget(self.frame_label_2)
        bottom_row.addItem(
            QtWidgets.QSpacerItem(0, 0, QtWidgets.QSizePolicy.Policy.Expanding)
        )
        bottom_row.addWidget(self.time_label)
        main_layout.addLayout(bottom_row)

        # create new window if no parent
        self._parent = parent
        if not parent:
            self.setWindowTitle("Animation Player")
            self.setMinimumWidth(600)
            play_icon = self.style().standardIcon(
                QtWidgets.QStyle.StandardPixmap.SP_MediaPlay
            )
            self.setWindowIcon(play_icon)
            self.show()
            self.raise_()
            self.adjustSize()
            self.quit_shortcuts = [
                QtGui.QShortcut(QtGui.QKeySequence(keys.Key_Q), self),
                QtGui.QShortcut(
                    QtGui.QKeySequence(keys.Key_Q | keys.ControlModifier), self
                ),
            ]
            for sc in self.quit_shortcuts:
                sc.activated.connect(self.close)
            self.register_shortcuts()

        # allow focus from clicks and tabbing
        self.setFocusPolicy(QtCore.Qt.FocusPolicy.StrongFocus)

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        """
        Overrides the closeEvent to reset the singleton instance.

        Args:
            event (QCloseEvent): The close event.
        """
        super().closeEvent(event)
        AnimationPlayer._instance = None

    def setup(
        self,
        frames: int,
        ts: float,
        step: int,
        update_callback: Optional[Callable[[int], None]] = None,
    ) -> None:
        """
        Sets up the animation player with the given parameters. This essentially
        initializes the player, but allows it to be created in a tab beforehand.

        Args:
            frames (int): The total number of frames in the animation.
            ts (float): The time step between frames in seconds.
            step (int): How many frames to skip between each update.
            update_callback (Callable[[int], None] | None): A callback function
                that is called whenever the frame is changed. The function should
                take a single integer argument, which is the current frame index.
        """
        self.end_frame = frames - 1
        self.ts = ts
        s = str(ts)
        self.t_decimals = len(s.split(".")[-1]) if "." in s else 2

        end_time = self.end_frame * self.ts
        self.t_digits = len(f"{end_time:.{self.t_decimals}f}")
        self.end_time = f"{end_time:>{self.t_digits}.{self.t_decimals}f}"

        self.step = step
        self.jump = int(frames // 20)
        self.update_callback = update_callback or (lambda i: None)

        # relevant UI elements
        self.slider.setMaximum(frames - 1)
        self.spin_box.setMaximum(frames - 1)
        self.jump_back_button.setToolTip(
            f"Jump back {self.jump} frames (Ctrl+LeftArrow)"
        )
        self.jump_forward_button.setToolTip(
            f"Jump forward {self.jump} frames (Ctrl+RightArrow)"
        )
        self.slider.setPageStep(self.jump)
        self.frame_label_2.setText(f"/ {self.end_frame}")
        self._set_time_label()

    def step_frame(self) -> bool:
        """
        Steps the animation forward by one step if not paused.

        Returns:
            stepped (bool): True if the frame was stepped forward, False if
                the animation is paused.
        """
        if not self.paused:
            self.current_frame += self.step
            if self.current_frame > self.end_frame:
                self.current_frame = self.end_frame
                self._pause()
            self.slider.setValue(self.current_frame)
            self.update_callback(self.current_frame)
            return True
        return False

    def register_shortcuts(self, window: QtWidgets.QWidget = None) -> None:
        """
        Registers shortcuts for the animation player on the given window.

        Args:
            window (QWidget | None): The window to register the shortcuts on. If None,
                shortcuts will be registered on the animation player itself.
        """
        for action, shortcuts in self.shortcuts.items():
            for shortcut in shortcuts:
                sc = QtGui.QShortcut(shortcut, window or self)
                sc.setContext(QtCore.Qt.ShortcutContext.WindowShortcut)
                match action:
                    case "toggle_play_pause":
                        sc.activated.connect(self.play_button.click)
                    case "step_forward":
                        sc.activated.connect(self.next_button.click)
                    case "step_backward":
                        sc.activated.connect(self.prev_button.click)
                    case "jump_forward":
                        sc.activated.connect(self.jump_forward_button.click)
                    case "jump_backward":
                        sc.activated.connect(self.jump_back_button.click)
                    case "restart":
                        sc.activated.connect(self.restart_button.click)
                    case "go_to_end":
                        sc.activated.connect(self.end_button.click)
                    case "save_animation":
                        sc.activated.connect(self.save_button.click)
                    case _:
                        raise ValueError(
                            f"Unknown action '{action}' for shortcut '{shortcut}'"
                        )

    def _on_play_clicked(self):
        if self.paused and self.current_frame == self.end_frame:
            self.restart_button.click()
        if self.paused:
            self._play()
        else:
            self._pause()

    def _on_restart_clicked(self):
        self.current_frame = 0
        self.slider.setValue(self.current_frame)
        self.update_callback(self.current_frame)

    def _on_end_clicked(self):
        self.current_frame = self.end_frame
        self.slider.setValue(self.current_frame)
        self.update_callback(self.current_frame)

    def _on_prev_clicked(self):
        if not self.paused:
            return
        if self.current_frame > 0:
            self.current_frame -= 1
            self.slider.setValue(self.current_frame)

    def _on_jump_back_clicked(self):
        if not self.paused:
            return
        self.current_frame -= self.jump
        if self.current_frame < 0:
            self.current_frame = 0
        self.slider.setValue(self.current_frame)
        self.update_callback(self.current_frame)

    def _on_next_clicked(self):
        if not self.paused:
            return
        if self.current_frame < self.end_frame:
            self.current_frame += 1
            self.slider.setValue(self.current_frame)
            self.update_callback(self.current_frame)

    def _on_jump_forward_clicked(self):
        if not self.paused:
            return
        self.current_frame += self.jump
        if self.current_frame > self.end_frame:
            self.current_frame = self.end_frame
        self.slider.setValue(self.current_frame)
        self.update_callback(self.current_frame)

    def _on_slider_changed(self, value: int):
        self.current_frame = value
        self.spin_box.setValue(self.current_frame)
        self._set_time_label()
        self.update_callback(self.current_frame)

    def _on_spinbox_changed(self):
        value = self.spin_box.value()
        self.current_frame = value
        self.slider.setValue(self.current_frame)

    def _set_time_label(self):
        time = self.current_frame * self.ts
        time = f"{time:>{self.t_digits}.{self.t_decimals}f}"
        self.time_label.setText(f"Sim Time: {time} / {self.end_time} s")

    def _pause(self):
        self.paused = True
        icon = self.std_icon(QtWidgets.QStyle.StandardPixmap.SP_MediaPlay)
        self.play_button.setIcon(icon)
        self.play_button.setToolTip("Play")
        self.jump_back_button.setEnabled(True)
        self.prev_button.setEnabled(True)
        self.next_button.setEnabled(True)
        self.jump_forward_button.setEnabled(True)

    def _play(self):
        self.paused = False
        icon = self.std_icon(QtWidgets.QStyle.StandardPixmap.SP_MediaPause)
        self.play_button.setIcon(icon)
        self.play_button.setToolTip("Pause")
        self.jump_back_button.setEnabled(False)
        self.prev_button.setEnabled(False)
        self.next_button.setEnabled(False)
        self.jump_forward_button.setEnabled(False)

    @classmethod
    def instance(cls) -> Optional[Self]:
        """
        Returns:
            instance (AnimationPlayer | None): The singleton instance of the
                AnimationPlayer, or None if it does not exist.
        """
        return cls._instance