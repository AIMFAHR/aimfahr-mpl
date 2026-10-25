import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pytest

import aimfahr_mpl


@pytest.mark.parametrize("theme", aimfahr_mpl.THEMES)
@pytest.mark.parametrize("context", aimfahr_mpl.CONTEXTS)
def test_use_and_save(theme, context, tmp_path):
    aimfahr_mpl.use(theme, context)
    fig, ax = plt.subplots()
    for i in range(8):
        ax.plot(np.arange(10), np.arange(10) + i, label=f"s{i}")
    ax.pcolormesh(np.random.rand(5, 5))
    ax.legend()
    for ext in ("png", "pdf", "svg"):
        fig.savefig(tmp_path / f"out.{ext}")
    plt.close(fig)


@pytest.mark.parametrize("name", ["dark", "light", "web", "slides", "poster", "journal"])
def test_style_by_name(name):
    plt.style.use(f"aimfahr_mpl.{name}")


def test_cycle_matches_theme():
    aimfahr_mpl.use("dark", "web")
    cyc = [c.upper().lstrip("#") for c in plt.rcParams["axes.prop_cycle"].by_key()["color"]]
    assert cyc == [c.lstrip("#") for c in aimfahr_mpl.CYCLE["dark"]]


def test_colormaps_registered():
    for name in ("aimfahr_sun", "aimfahr_sun_dark", "aimfahr_ice", "aimfahr_div", "aimfahr_div_dark"):
        assert name in matplotlib.colormaps
        assert f"{name}_r" in matplotlib.colormaps


def test_font_bundled():
    from matplotlib import font_manager
    path = font_manager.findfont(font_manager.FontProperties(family="Montserrat"), fallback_to_default=False)
    assert "Montserrat" in path


def test_journal_size():
    assert aimfahr_mpl.journal_size("double", 0.5) == (7.2, 3.6)
    assert aimfahr_mpl.journal_size(4.0, 0.75) == (4.0, 3.0)


def test_bad_names():
    with pytest.raises(ValueError):
        aimfahr_mpl.use("blue", "web")
    with pytest.raises(ValueError):
        aimfahr_mpl.use("dark", "billboard")
