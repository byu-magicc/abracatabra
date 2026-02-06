from matplotlib.backends.qt_compat import QtWidgets, QtGui
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt import NavigationToolbar2QT as NavigationToolbar
from typing import Callable

from .animation_player import AnimationPlayer
from . import keys

# from PySide6 import QtWidgets


class FigureWidget(QtWidgets.QWidget):
    """
    A Qt widget that contains a matplotlib figure canvas with an optional toolbar.
    Inherits from `QWidget`.

    Methods:
        `update_figure`: Updates the figure canvas if anything has changed.
        `show_toolbar`: Show or hide the navigation toolbar.
        `register_animation_callback`: Registers a callback function for how to
            update the figure during an animation.
    """

    help_text = """Figure Controls:
    h: Home (reset view)
    c: Back 1 view
    v: Forward 1 view
    p: Toggle pan mode
    z: Toggle zoom mode
    Ctrl+s: Save figure
    """

    def __init__(
        self,
        name: str | int = "figure",
        blit: bool = False,
        include_toolbar: bool = True,
        add_animation_player: bool = False,
        parent=None,
    ):
        """
        Initializes the FigureWidget. This creates a matplotlib figure canvas
        and optionally includes a navigation toolbar.

        Args:
            name (str): The name of the figure widget, used as the default
                filename when saving the figure.
            blit (bool): If True, enables blitting for faster rendering.
            include_toolbar (bool): If True, includes a navigation toolbar
                with the canvas.
            add_animation_player (bool): Whether to include an animation player
                widget in this tab (play, pause, etc.). Only works if animation
                callbacks are registered.
            parent: The parent widget for this widget.
        """
        super().__init__(parent)
        self.blit = blit
        layout = QtWidgets.QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        self.canvas = FigureCanvas()
        # override default save behavior to use pdf and custom filename
        if isinstance(name, int):
            name = f"figure_{name}"
        self._id: str = name
        self.canvas.get_default_filetype = lambda: "pdf"
        self.canvas.get_default_filename = lambda: f"{name}.pdf"

        self.figure = self.canvas.figure
        # self.figure.set_layout_engine('tight') # slows down rendering ~2x
        # self.figure.tight_layout() # does not seem to do anything here

        self.toolbar = NavigationToolbar(self.canvas, self)
        self.toolbar.setMaximumHeight(25)
        self.toolbar.setVisible(include_toolbar)

        layout.addWidget(self.canvas, stretch=1)
        layout.addWidget(self.toolbar)

        if add_animation_player:
            animation_player = AnimationPlayer(parent=self)
            layout.addWidget(animation_player, stretch=0)

        self.setLayout(layout)

        self._update_callback: Callable[[int], None] = lambda i: None
        self._callback_registered = False
        self._latest_callback_idx = 0

    def update_figure(self, callback_idx: int = 0) -> None:
        """
        Updates the figure canvas if anything has changed. If blitting is
        enabled, it will only redraw the parts of the figure that have changed.
        If not, it will redraw the entire canvas. NOTE that blitting requires
        the user to manage the background and artist updates manually, i.e., the
        user must call `canvas.copy_from_bbox()` and `canvas.restore_region()`
        at the appropriate times AND ensure that the artists are drawn before
        calling this method.

        Args:
            callback_idx (int): An index passed to the registered animation
                callback function. This index is intended to specify which frame
                of the animation to draw, if an animation callback has been
                registered.
        """
        # Attempting to detect if the same frame as last time to avoid re-drawing
        if self._callback_registered and callback_idx == self._latest_callback_idx:
            # print("Skipping figure update; same frame as last time.")
            return
        self._update_callback(callback_idx)
        self._latest_callback_idx = callback_idx
        if not self.figure.stale:
            return
        if self.blit:
            self.canvas.blit()
        else:
            self.canvas.draw_idle()
        self.canvas.flush_events()

    def show_toolbar(self, show: bool = True) -> None:
        """
        Show or hide the navigation toolbar.

        Args:
            show (bool): If True, shows the toolbar. If False, hides it.
        """
        self.toolbar.setVisible(show)

    def register_animation_callback(self, callback: Callable[[int], None]) -> None:
        """
        Registers a callback function for how to update the figure during an
        animation. Note that if the figure has multiple axes or artists, the
        user is responsible for managing the updates to all of those objects in
        the callback function (callback is per figure not per axis/artist).

        Args:
            callback (Callable[[int], None]): A function specifying how to update
                the widget. The function should take a single integer argument,
                which is the index of the current frame in the animation to draw.
                Registering callbacks allows abracatabra to better manage the
                timing of updates.
        """
        self._update_callback = callback
        self._callback_registered = True

    def _handle_keypress(self, event: QtGui.QKeyEvent) -> bool:
        """
        Forwards key press events to the figure canvas to enable keyboard
        shortcuts for matplotlib (e.g., zoom, pan, save, etc.).

        Args:
            event (QKeyEvent): The key event.
        Returns:
            bool: True if the key event was handled, False otherwise.
        """
        match event.key():
            case keys.Key_P:
                self.toolbar.pan()
            case keys.Key_H:
                self.toolbar.home()
            case keys.Key_Z:
                self.toolbar.zoom()
            case keys.Key_C:
                self.toolbar.back()
            case keys.Key_V:
                self.toolbar.forward()
            case keys.Key_S:
                if event.modifiers() & keys.ControlModifier:
                    self.toolbar.save_figure()
            case _:
                return False
        return True
