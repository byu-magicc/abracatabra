import os
from matplotlib.figure import Figure
from matplotlib.backends.qt_compat import QtWidgets, QtCore, QtGui

from .figure_widget import FigureWidget
from .custom_widget import CustomWidget

# Suppress atspi accessibility warnings from Qt (started happening after using slots)
os.environ["QT_LOGGING_RULES"] = "qt.accessibility.atspi=false"


class TabbedFigureWidget(QtWidgets.QTabWidget):
    """
    A Qt widget that can contain multiple tabs, each with a matplotlib Figure
    or custom widget. This class inherits from QTabWidget to create a tabbed
    interface with visual focus indication (blue accent bar when focused).

    The widget automatically manages focus by transferring it to tab contents
    when tabs are clicked or changed, ensuring keyboard shortcuts work properly.
    An event filter tracks focus changes to show/hide the focus indicator.

    Methods:
        `update_active_tab`: Updates the currently active tab's widget.
        `add_figure_tab`: Adds a new tab with a matplotlib Figure.
        `add_custom_tab`: Adds a new tab with a custom Qt widget.
        `get_tab`: Returns the widget associated with a given tab ID.
        `set_tab_position`: Sets the position of the tab bar.
        `set_tab_fontsize`: Sets the font size of the tab bar.
    """

    def __init__(self, autohide: bool, position: str = "top", fontsize: int = 8):
        """
        Initializes the TabbedFigureWidget.

        Args:
            autohide (bool): If True, the tab bar will auto-hide when there is
                only one tab.
            position (str): The position of the tab bar. Can be 'top', 'bottom',
                'left', or 'right' as well as 'north', 'south', 'east', or
                'west' (only first character is checked).
            fontsize (int): The font size of the tab labels.
        """
        super().__init__()
        tabbar = self.tabBar()
        tabbar.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
        assert isinstance(tabbar, QtWidgets.QTabBar)
        tabbar.setAutoHide(autohide)
        tabbar.setContentsMargins(0, 0, 0, 0)
        self.set_tab_position(position)
        self.set_tab_fontsize(fontsize)
        self._figure_widgets: dict[str, FigureWidget] = {}
        self._custom_widgets: dict[str, CustomWidget] = {}
        self._latest_callback_idx = 0
        self.currentChanged.connect(self._on_tab_changed)
        self.tabBarClicked.connect(self._on_tab_clicked)
        self.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)

        # Visual indicator for focused tab group (thin accent bar)
        self._focused = False
        self._focus_indicator = QtWidgets.QWidget(self)
        self._focus_indicator.setFixedHeight(3)
        self._focus_indicator.setStyleSheet("background-color: #2196F3;")
        self._focus_indicator.hide()
        self._update_focus_indicator_position()
        self._update_focus_style()

        # Connect to global focus change signal instead of using event filters
        # This eliminates race conditions from deferred callbacks during cleanup
        app = QtWidgets.QApplication.instance()
        if app:
            app.focusChanged.connect(self._on_focus_changed)

    def __getitem__(self, tab_id: str | int) -> FigureWidget | CustomWidget:
        """
        Provides dictionary-like access to tabs by their ID for convenience.

        Args:
            tab_id (str|int): The title/ID of the tab.

        Returns:
            widget (FigureWidget | CustomWidget): The widget associated with the
                given tab ID.
        """
        return self.get_tab(tab_id)

    def _on_focus_changed(self, old_widget, new_widget):
        """
        Slot called when application focus changes. Updates the focus
        indicator based on whether the new focused widget is a descendant
        of this tab group.

        This approach is cleaner than using event filters and deferred
        callbacks, eliminating race conditions during widget cleanup.

        Args:
            old_widget: The previously focused widget (may be None).
            new_widget: The newly focused widget (may be None).
        """
        # Check if the newly focused widget is a child of this tab group
        has_focus = new_widget is not None and self.isAncestorOf(new_widget)

        if self._focused != has_focus:
            self._focused = has_focus
            self._update_focus_style()

    def _update_focus_indicator_position(self):
        """
        Position the focus indicator bar at the top edge of the widget.
        """
        self._focus_indicator.setGeometry(0, 0, self.width(), 3)
        self._focus_indicator.raise_()

    def resizeEvent(self, event):
        """
        Handle resize events to reposition the focus indicator bar.

        Args:
            event: The resize event.
        """
        super().resizeEvent(event)
        self._update_focus_indicator_position()

    def _update_focus_style(self):
        """
        Update the visual style of the tab group based on focus state.
        Shows a thin blue accent bar at the top when focused, works even
        with autohide tabs. No changes to tab bar to preserve original look.
        """
        if self._focused:
            # Show blue accent bar when focused
            self._focus_indicator.show()
        else:
            # Hide accent bar when not focused
            self._focus_indicator.hide()

    def update_active_tab(self, callback_idx: int = 0) -> None:
        """
        Updates the currently active tab's widget.

        Args:
            callback_idx (int): An index passed to the registered animation
                callback function. This index is intended to specify which frame
                to draw.
        """
        self._latest_callback_idx = callback_idx
        active_widget = self.currentWidget()
        if isinstance(active_widget, FigureWidget):
            active_widget.update_figure(callback_idx)
        elif isinstance(active_widget, CustomWidget):
            active_widget.update_widget(callback_idx)

    def add_figure_tab(
        self,
        tab_id: str | int,
        blit: bool = False,
        include_toolbar: bool = True,
        add_animation_player: bool = False,
    ) -> Figure:
        """
        Adds a new tab to the widget with the given title/tab_id, which
        creates and returns a matplotlib Figure. Tabs are displayed in the
        order they are added. If the tab ID already exists, returns the
        existing Figure without creating a new tab.

        The new tab widget has an event filter installed to track focus changes
        for the focus indicator.

        Args:
            tab_id (str|int): The title/ID of the tab. If the tab ID already
                exists, the existing Figure from that tab will be returned.
            blit (bool): If True, enables blitting for faster rendering on the
                Figure in this tab.
            include_toolbar (bool): If True, includes a navigation toolbar
                with the Figure in this tab.
            add_animation_player (bool): Whether to include an animation player
                widget in this tab (play, pause, etc.). Only works if animation
                callbacks are registered.

        Returns:
            figure: The matplotlib Figure object for the tab.
        """
        id_ = str(tab_id)
        if id_ in self._figure_widgets:
            return self._figure_widgets[id_].figure
        new_tab = FigureWidget(
            tab_id, blit, include_toolbar, add_animation_player, self
        )
        self._figure_widgets[id_] = new_tab
        idx = self.currentIndex()
        super().addTab(new_tab, id_)
        self.setCurrentWidget(new_tab)  # activate tab to auto size figure
        self.setCurrentIndex(idx)  # switch back to original tab
        return new_tab.figure

    def add_custom_tab(
        self,
        widget: QtWidgets.QWidget,
        tab_id: str | int,
        add_animation_player: bool = False,
    ) -> None:
        """
        Adds a new tab to the widget with the given title/tab_id, which
        contains the provided custom Qt widget. Tabs are displayed in the
        order they are added.

        The new tab widget has an event filter installed to track focus changes
        for the focus indicator.

        Args:
            widget (QWidget): The custom Qt widget to add as a tab.
            tab_id (str|int): The title/ID of the tab. Must be unique.
            add_animation_player (bool): Whether to include an animation player
                widget in this tab (play, pause, etc.). Only works if animation
                callbacks are registered.

        Raises:
            ValueError: If a tab with the given ID already exists.
        """
        id_ = str(tab_id)
        if id_ in self._figure_widgets | self._custom_widgets:
            raise ValueError(f"Tab with id '{id_}' already exists.")
        new_tab = CustomWidget(widget, add_animation_player)
        self._custom_widgets[id_] = new_tab
        super().addTab(new_tab, id_)
        return

    def get_tab(self, tab_id: str | int) -> FigureWidget | CustomWidget:
        """
        Returns the widget associated with the given tab ID.

        Args:
            tab_id (str|int): The title/ID of the tab.

        Returns:
            widget: The widget associated with the given tab ID.

        Raises:
            ValueError: If no tab with the given ID exists.
        """
        id_ = str(tab_id)
        if id_ in self._figure_widgets:
            return self._figure_widgets[id_]
        elif id_ in self._custom_widgets:
            return self._custom_widgets[id_]
        else:
            raise ValueError(f"Tab with id '{id_}' does not exist.")

    def set_tab_position(self, position: str = "top") -> None:
        """
        Sets the position of the tab bar.

        Args:
            position (str): The position of the tab bar. Can be 'top', 'bottom',
                'left', or 'right' as well as 'north', 'south', 'east', or
                'west' (only first character is checked).
        """
        char = position[0].lower()
        if char in ["b", "s"]:
            self.setTabPosition(QtWidgets.QTabWidget.TabPosition.South)
        elif char in ["l", "w"]:
            self.setTabPosition(QtWidgets.QTabWidget.TabPosition.West)
        elif char in ["r", "e"]:
            self.setTabPosition(QtWidgets.QTabWidget.TabPosition.East)
        else:
            self.setTabPosition(QtWidgets.QTabWidget.TabPosition.North)

    def set_tab_fontsize(self, fontsize: int) -> None:
        """
        Sets the font size of the tab bar.

        Args:
            fontsize (int): The font size to set for the tab bar.
        """
        tabbar = self.tabBar()
        assert isinstance(tabbar, QtWidgets.QTabBar)
        font = tabbar.font()
        font.setPointSize(fontsize)
        tabbar.setFont(font)

    @QtCore.Slot(int)
    def _on_tab_changed(self, index: int) -> None:
        """
        Slot called when the current tab is changed. This is used to make sure
        the animation callback is called for the newly active tab, and to
        transfer focus to the newly active widget so its shortcuts work.

        Args:
            index (int): The index of the newly selected tab.
        """
        # Transfer focus to current widget so its shortcuts work when tab is clicked
        current_widget = self.currentWidget()
        if current_widget:
            current_widget.setFocus()

        if self._latest_callback_idx > 0:
            self.update_active_tab(self._latest_callback_idx)

    @QtCore.Slot(int)
    def _on_tab_clicked(self, index: int) -> None:
        """
        Slot called when a tab is clicked. This transfers focus to the clicked
        tab's widget, even if it was already the active tab. This ensures
        shortcuts work when clicking on an already-visible tab.

        Args:
            index (int): The index of the clicked tab.
        """
        current_widget = self.currentWidget()
        if current_widget:
            current_widget.setFocus()
