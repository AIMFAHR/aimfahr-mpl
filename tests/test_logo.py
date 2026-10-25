import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pytest

import aimfahr_mpl
from aimfahr_mpl.logo import LogoBox


@pytest.fixture(autouse=True)
def _style():
    aimfahr_mpl.use("dark", "web")
    yield
    plt.close("all")


@pytest.mark.parametrize("name", aimfahr_mpl.LOGOS)
@pytest.mark.parametrize("theme", ["dark", "light"])
def test_logo_files_exist(name, theme):
    assert aimfahr_mpl.logo_path(name, theme).is_file()


@pytest.mark.parametrize("name", aimfahr_mpl.LOGOS)
@pytest.mark.parametrize("loc", ["best", "upper right", "lower left", "center", (0.1, 0.1)])
def test_add_logo_axes(name, loc, tmp_path):
    fig, ax = plt.subplots()
    ax.plot([0, 1], [0, 1])
    box = aimfahr_mpl.add_logo(ax, name, loc)
    assert isinstance(box, LogoBox)
    fig.savefig(tmp_path / "out.png")


def test_add_logo_figure_outside(tmp_path):
    fig, ax = plt.subplots()
    ax.plot([0, 1], [0, 1])
    box = aimfahr_mpl.add_logo(fig, "horizontal")
    assert box in fig.legends
    fig.savefig(tmp_path / "out.png")


def test_best_avoids_existing_legend():
    fig, ax = plt.subplots()
    x = np.linspace(0, 10, 200)
    ax.plot(x, np.sin(x), label="a")
    ax.plot(x, np.cos(x), label="b")
    leg = ax.legend(loc="upper left")
    box = aimfahr_mpl.add_logo(ax)
    fig.canvas.draw()
    r = fig.canvas.get_renderer()
    assert not box.get_window_extent(r).overlaps(leg.get_window_extent(r))


def test_outside_axes_not_clipped():
    fig, ax = plt.subplots()
    box = aimfahr_mpl.add_logo(ax, "icon", "upper left", bbox_to_anchor=(1.02, 1))
    assert not box.get_clip_on()


def test_theme_auto():
    aimfahr_mpl.use("light", "web")
    fig, ax = plt.subplots()
    box = aimfahr_mpl.add_logo(ax)
    assert box is not None  # light background picks the light version without error


def test_remove():
    fig, ax = plt.subplots()
    box = aimfahr_mpl.add_logo(ax)
    box.remove()
    assert box not in ax.get_children()


def test_bad_logo():
    fig, ax = plt.subplots()
    with pytest.raises(ValueError):
        aimfahr_mpl.add_logo(ax, "banner")
