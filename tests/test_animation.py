import numpy as np
import abracatabra
from matplotlib.animation import FuncAnimation


def test_animation(attached_player: bool, attach_location: str = "figure", save=False):
    blit = True
    window = abracatabra.TabbedPlotWindow(
        autohide_tabs=True,
        open_window=True,
        add_animation_player=attached_player and not attach_location == "figure",
    )

    fig1 = window.add_figure_tab(
        "robot arm animation",
        include_toolbar=True,
        blit=blit,
        add_animation_player=attached_player and attach_location == "figure",
    )

    # window.show()

    ax1 = fig1.add_subplot()

    # background elements
    fig1.tight_layout()
    ax1.set_aspect("equal", "box")
    length = 1.0
    lim = 1.25 * length
    ax1.axis((-lim, lim, -lim, lim))
    (baseline,) = ax1.plot([0, length], [0, 0], "k--")

    # draw and save background for fast rendering
    fig1.canvas.draw()
    background1 = fig1.canvas.copy_from_bbox(ax1.bbox)  # type: ignore

    # moving elements
    def get_arm_endpoints(theta):
        x = np.array([0, length * np.cos(theta)])
        y = np.array([0, length * np.sin(theta)])
        return x, y

    t_hist = np.linspace(0, 10, 501)
    theta_hist = np.sin(t_hist)
    x, y = get_arm_endpoints(theta_hist[0])
    (arm_line,) = ax1.plot(x, y, linewidth=5, color="blue")

    def update(frame_idx):
        theta = theta_hist[frame_idx]
        x, y = get_arm_endpoints(theta)
        arm_line.set_xdata(x)
        arm_line.set_ydata(y)

        if blit:
            fig1.canvas.restore_region(background1)  # type: ignore
            ax1.draw_artist(arm_line)

    window.register_animation_callback(update, "robot arm animation")

    window2 = abracatabra.TabbedPlotWindow(ncols=2, autohide_tabs=True)
    fig2 = window2.add_figure_tab("sin", blit=blit)
    ax2 = fig2.add_subplot()
    (sin_line,) = ax2.plot(t_hist, theta_hist)
    fig2.tight_layout()
    fig2.canvas.draw()
    sin_line.set_data([], [])
    fig2.canvas.draw()
    background2 = fig2.canvas.copy_from_bbox(ax2.bbox)  # type: ignore

    def update_sin(frame_idx):
        sin_line.set_data(t_hist[:frame_idx], theta_hist[:frame_idx])
        fig2.canvas.restore_region(background2)  # type: ignore
        ax2.draw_artist(sin_line)

    window2.register_animation_callback(update_sin, "sin")

    fig3 = window2.add_figure_tab("cos", blit=blit)
    ax3 = fig3.add_subplot()
    t_cos = t_hist - 5
    (cos_line,) = ax3.plot(t_cos, np.cos(t_cos))
    fig3.canvas.draw()
    cos_line.set_data([], [])
    fig3.canvas.draw()
    background3 = fig3.canvas.copy_from_bbox(ax3.bbox)  # type: ignore

    def update_cos(frame_idx):
        cos_line.set_data(t_cos[:frame_idx], np.cos(t_cos[:frame_idx]))
        fig3.canvas.restore_region(background3)  # type: ignore
        ax3.draw_artist(cos_line)

    window2.register_animation_callback(update_cos, "cos")

    fig4 = window2.add_figure_tab("wave", blit=blit, col=1)
    ax4 = fig4.add_subplot()
    (wave_line,) = ax4.plot(t_hist, theta_hist)
    fig4.canvas.draw()
    wave_line.set_data([], [])
    fig4.canvas.draw()
    background4 = fig4.canvas.copy_from_bbox(ax4.bbox)  # type: ignore

    def update_wave(frame_idx):
        wave_line.set_data(t_hist, np.sin(t_hist + frame_idx * 0.1))
        fig4.canvas.restore_region(background4)  # type: ignore
        ax4.draw_artist(wave_line)

    window2.register_animation_callback(update_wave, "wave", col=1)

    dt = 0.01
    # if save:
    #     tab = window.tab_groups[0, 0].get_tab("robot arm animation")
    #     tab.save_animation(frames=len(theta_hist), dt=dt, filename="test.mp4")

    abracatabra.animate_all_windows(len(theta_hist), ts=dt, use_player=True)
    assert True


if __name__ == "__main__":
    test_animation(attached_player=False, save=True)
    test_animation(attached_player=True, attach_location="figure")
    test_animation(attached_player=True, attach_location="window")
