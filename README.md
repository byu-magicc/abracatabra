# AbracaTABra

[![PyPI](https://img.shields.io/pypi/v/abracatabra.svg)](https://pypi.org/project/abracatabra/)
[![CI](https://github.com/byu-magicc/abracatabra/actions/workflows/ci.yml/badge.svg)](https://github.com/byu-magicc/abracatabra/actions/workflows/ci.yml)
[![Build and publish to PyPI](https://github.com/byu-magicc/abracatabra/actions/workflows/publish.yml/badge.svg)](https://github.com/byu-magicc/abracatabra/actions/workflows/publish.yml)

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
A Python Qt package is required for functionality, but there is no good way to have a default optional dependency with pip...so you have to install separately or manually specify one of the following optional dependencies:

- [qt-pyside6]
- [qt-pyqt6]

For example, run this to install PySide6 along with this package:

```
pip install "abracatabra[qt-pyside6]"
```

**NOTE:**
Optional dependency installations are not provided for PyQt5 or PySide2 because QT 5 has reached end of life and it is not recommended to use them.

## Usage

```python
import numpy as np
import abracatabra as tabby


window1 = tabby.TabbedPlotWindow(window_id="README example", ncols=2)
window2 = tabby.TabbedPlotWindow(size=(500, 400))

# data
t = np.arange(0, 10, 0.001)
ysin = np.sin(t)
ycos = np.cos(t)


f = window1.add_figure_tab("sin", col=0)
ax = f.add_subplot()
(line1,) = ax.plot(t, ysin, "--")
ax.set_xlabel("time")
ax.set_ylabel("sin(t)")
ax.set_title("Plot of sin(t)")

f = window1.add_figure_tab("time", col=1)
ax = f.add_subplot()
ax.plot(t, t)
ax.set_xlabel("time")
ax.set_ylabel("t")
ax.set_title("Plot of t")

window1.apply_tight_layout()

f = window2.add_figure_tab("cos")
ax = f.add_subplot()
(line2,) = ax.plot(t, ycos, "--")
ax.set_xlabel("time")
ax.set_ylabel("cos(t)")
ax.set_title("Plot of cos(t)")

f = window2.add_figure_tab("time")
ax = f.add_subplot()
ax.plot(t, t)
ax.set_xlabel("time")
ax.set_ylabel("t")
ax.set_title("Plot of t", fontsize=20)

window2.apply_tight_layout()


### animate

## option 1
dt = 0.1
for k in range(100):
    t += dt
    ysin = np.sin(t)
    line1.set_ydata(ysin)
    ycos = np.cos(t)
    line2.set_ydata(ycos)

    # For timing to be accurate, you would have to calculate how long it took to
    # run the previous 5 lines and subtract that from dt
    tabby.update_all_windows(dt)

# You would need this to keep windows open if not in an interactive environment
# tabby.show_all_windows(block=True)


## option 2: use animation callbacks
print("Same thing, but using animation callbacks now")


def update_sin(frame: int):
    time = t + frame * dt
    line1.set_ydata(np.sin(time))


def update_cos(frame: int):
    time = t + frame * dt
    line2.set_ydata(np.cos(time))


window1.tab_groups[0, 0].get_tab("sin").register_animation_callback(update_sin)
window2.tab_groups[0, 0].get_tab("cos").register_animation_callback(update_cos)

# This method accounts for how long it takes to call the animation callbacks
# so that the time between frames is closer to the specified time step. Also,
# if a tab is not active (visible), it will not call the animation callback
# for that tab, which can save a lot of time if you have many tabs.
tabby.animate_all_windows(frames=100, ts=dt, print_timing=True, hold=False)

tabby.abracatabra()  # keep windows open if not in an interactive environment
```

### Example using blitting

```python
import numpy as np
import abracatabra


blit = True
window = abracatabra.TabbedPlotWindow(autohide_tabs=True)
fig = window.add_figure_tab("robot arm animation", include_toolbar=False, blit=blit)
ax = fig.add_subplot()

# background elements
fig.tight_layout()
ax.set_aspect("equal", "box")
length = 1.0
lim = 1.25 * length
ax.axis((-lim, lim, -lim, lim))
(baseline,) = ax.plot([0, length], [0, 0], "k--")

# draw and save background for fast rendering
fig.canvas.draw()
background = fig.canvas.copy_from_bbox(ax.bbox)


# moving elements
def get_arm_endpoints(theta):
    x = np.array([0, length * np.cos(theta)])
    y = np.array([0, length * np.sin(theta)])
    return x, y


time = np.linspace(0, 10, 501)
theta_hist = np.sin(time)
x, y = get_arm_endpoints(theta_hist[0])
(arm_line,) = ax.plot(x, y, linewidth=5, color="blue")


# animate
def animation_step(idx: int):
    theta = theta_hist[idx]
    x, y = get_arm_endpoints(theta)
    arm_line.set_xdata(x)
    arm_line.set_ydata(y)

    if blit:
        fig.canvas.restore_region(background)
        ax.draw_artist(arm_line)


dt = time[1] - time[0]
window.register_animation_callback(animation_step, "robot arm animation")
abracatabra.animate_all_windows(frames=len(theta_hist), ts=dt, print_timing=True)
```
