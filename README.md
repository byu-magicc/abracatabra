# AbracaTABra

This repository is basically a matplotlib extension using the Qt backend to create plot windows with groups of tabs, where the contents of each tab is a matplotlib figure.
This package is essentially a replacement for pyplot; it creates and manages figures separately from pyplot, so calling `pyplot.show()` or `pyplot.pause()` will not do anything with windows created from this package.
This package provides the functions `show_all_windows()` and `update_all_windows(delay_seconds)`, which are very similar in behavior to `show()` and `pause(interval)`, respectively, from pyplot.
Also, `abracatabra()` is a more fun equivalent to `show_all_windows()`...you should try it out!

## Dependencies

- matplotlib
- One of the following Qt bindings for Python (this is the order matplotlib looks for them):
    - PyQt6
    - PySide6 (preferred option)
    - PyQt5
    - PySide2

## Installation

This will install the package as well as matplotlib, if it isn't installed:

```
pip install abracatabra
```

Qt bindings are an optional dependency of the package.
A PyQt package is required for functionality, but there is no good way to have a default optional dependency with pip...so you have to install separately or manually specify one of the following optional dependencies:

- [qt-pyside6]
- [qt-pyqt6]
- [qt-pyqt5]
- [qt-pyside2]

For example, run this to install PySide6 along with this package:
```
pip install "abracatabra[qt-pyside6]"
```

## Usage

```python
import numpy as np
import abracatabra


window1 = abracatabra.TabbedPlotWindow(window_id='test', ncols=2)
window2 = abracatabra.TabbedPlotWindow(size=(500,400))

# data
t = np.arange(0, 10, 0.001)
ysin = np.sin(t)
ycos = np.cos(t)


fig = window1.add_figure_tab("sin", col=0)
ax = fig.add_subplot()
line1, = ax.plot(t, ysin, '--')
ax.set_xlabel('time')
ax.set_ylabel('sin(t)')
ax.set_title('Plot of sin(t)')

fig = window1.add_figure_tab("time", col=1)
ax = fig.add_subplot()
ax.plot(t, t)
ax.set_xlabel('time')
ax.set_ylabel('t')
ax.set_title('Plot of t')

window1.apply_tight_layout()

fig = window2.add_figure_tab("cos")
ax = fig.add_subplot()
line2, = ax.plot(t, ycos, '--')
ax.set_xlabel('time')
ax.set_ylabel('cos(t)')
ax.set_title('Plot of cos(t)')

fig = window2.add_figure_tab("sin^2")
ax = fig.add_subplot()
ax.plot(t, ysin**2)
ax.set_xlabel('time')
ax.set_ylabel('t')
ax.set_title('Plot of t', fontsize=20)

window2.apply_tight_layout()

# animate
dt = 0.1
for k in range(100):
    t += dt
    ysin = np.sin(t)
    line1.set_ydata(ysin)
    ycos = np.cos(t)
    line2.set_ydata(ycos)
    abracatabra.update_all_windows(0.01)

abracatabra.abracatabra()
```

### Example using blitting

```python
import numpy as np
import abracatabra


blit = True
window = abracatabra.TabbedPlotWindow(autohide_tabs=True)
fig = window.add_figure_tab("robot arm animation", include_toolbar=False,
                            blit=blit)
ax = fig.add_subplot()

# background elements
fig.tight_layout()
ax.set_aspect('equal', 'box')
length = 1.0
lim = 1.25 * length
ax.axis((-lim, lim, -lim, lim))
baseline, = ax.plot([0, length], [0, 0], 'k--')

# draw and save background for fast rendering
fig.canvas.draw()
background = fig.canvas.copy_from_bbox(ax.bbox)

# moving elements
def get_arm_endpoints(theta):
    x = np.array([0, length*np.cos(theta)])
    y = np.array([0, length*np.sin(theta)])
    return x, y

theta_hist = np.sin(np.linspace(0, 10, 501))
x, y = get_arm_endpoints(theta_hist[0])
arm_line, = ax.plot(x, y, linewidth=5, color='blue')

# animate
for theta in theta_hist:
    x, y = get_arm_endpoints(theta)
    arm_line.set_xdata(x)
    arm_line.set_ydata(y)

    if blit:
        fig.canvas.restore_region(background)
        ax.draw_artist(arm_line)

    abracatabra.update_all_windows(0.01)

# keep window open
abracatabra.abracatabra()
```
