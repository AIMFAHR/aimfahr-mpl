"""AIMFAHR matplotlib styles.

Quick start
-----------
>>> import aimfahr_mpl
>>> aimfahr_mpl.use("dark", "slides")      # theme + context

Themes:   "dark" (navy ground), "light" (white ground)
Contexts: "web", "slides", "poster", "journal"

The style files also work on their own once the package is installed:
>>> plt.style.use(["aimfahr_mpl.dark", "aimfahr_mpl.web"])
but importing the package is what registers the Montserrat font and the
AIMFAHR colormaps (aimfahr_sun, aimfahr_sun_dark, aimfahr_ice, aimfahr_div,
aimfahr_div_dark).
"""
from __future__ import annotations
from pathlib import Path
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.colors import LinearSegmentedColormap, ListedColormap

__all__ = ["use", "COLORS", "CYCLE", "THEMES", "CONTEXTS", "direct_labels", "colormaps",
           "journal_size", "add_logo", "logo_path", "LOGOS"]
__version__ = "1.1.0"

_HERE = Path(__file__).parent
THEMES = ("dark", "light")
CONTEXTS = ("web", "slides", "poster", "journal")

# Brand colours (graphics). Text colours live in the style files.
COLORS = {
    "navy": "#0B1F3B", "navy_deep": "#061326", "surface": "#0F2A4F",
    "sun_core": "#FFD84A", "sun": "#FF8A00", "sun_limb": "#E5400B",
    "earth": "#1C73E8", "land": "#3DDBA8", "cyan": "#00D1FF", "blue": "#007BFF",
}
# Categorical cycles, fixed order. Validated for CVD separation and contrast
# against each theme's ground. Use them in this order; don't reorder by rank.
CYCLE = {
    "dark":  ["#DC7411", "#0CA3BE", "#DA4339", "#1E76D8", "#16A56E", "#855DD7", "#AF930D", "#D45198"],
    "light": ["#C9690C", "#1687A9", "#CC2823", "#005DC9", "#06915F", "#703DC6", "#9E840A", "#C32E85"],
}
CYCLE_NAMES = ["orange", "cyan", "red", "blue", "green", "violet", "gold", "pink"]


# ---------------------------------------------------------------- fonts
def _register_fonts() -> None:
    for f in sorted((_HERE / "fonts").glob("*.ttf")):
        try:
            font_manager.fontManager.addfont(str(f))
        except Exception:
            pass


# ---------------------------------------------------------------- colormaps
def _hex2lin(h):
    c = np.array([int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)])
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)

def _lin2oklab(c):
    M1 = np.array([[0.4122214708, 0.5363325363, 0.0514459929],
                   [0.2119034982, 0.6806995451, 0.1073969566],
                   [0.0883024619, 0.2817188376, 0.6299787005]])
    M2 = np.array([[0.2104542553, 0.7936177850, -0.0040720468],
                   [1.9779984951, -2.4285922050, 0.4505937099],
                   [0.0259040371, 0.7827717662, -0.8086757660]])
    return M2 @ np.cbrt(M1 @ c)

def _oklab2srgb(lab):
    M2i = np.array([[1, 0.3963377774, 0.2158037573],
                    [1, -0.1055613458, -0.0638541728],
                    [1, -0.0894841775, -1.2914855480]])
    M1i = np.array([[4.0767416621, -3.3077115913, 0.2309699292],
                    [-1.2684380046, 2.6097574011, -0.3413193965],
                    [-0.0041960863, -0.7034186147, 1.7076147010]])
    lin = M1i @ ((M2i @ lab) ** 3)
    lin = np.clip(lin, 0, 1)
    return np.where(lin <= 0.0031308, 12.92 * lin, 1.055 * lin ** (1 / 2.4) - 0.055)

def _ramp(name, stops, n=256):
    """Interpolate hex stops evenly in OKLab (perceptually smooth)."""
    labs = np.array([_lin2oklab(_hex2lin(h)) for h in stops])
    xs = np.linspace(0, 1, len(stops))
    t = np.linspace(0, 1, n)
    out = np.array([_oklab2srgb(np.array([np.interp(v, xs, labs[:, k]) for k in range(3)])) for v in t])
    return ListedColormap(out, name=name)

_CMAP_STOPS = {
    # Sequential, dark -> bright: the sun. Magnitudes such as density, flux, power.
    "aimfahr_sun": ["#14193A", "#43205E", "#8E2A5F", "#D2452E", "#F0800F", "#FCBC33", "#FFF1B8"],
    # The same sun, starting brighter so the low end stays visible on navy.
    "aimfahr_sun_dark": ["#3A2163", "#7A2A62", "#B93A45", "#E2621F", "#F59A14", "#FDCB4A", "#FFF4C8"],
    # Sequential, dark -> bright: Earth and atmosphere. Use for a second magnitude.
    "aimfahr_ice": ["#0A1530", "#123B78", "#1E6FD0", "#1FA8DA", "#7FDCF5", "#EAFAFF"],
    # Diverging for white grounds: blue (negative) - grey - orange (positive).
    "aimfahr_div": ["#123B78", "#1E6FD0", "#8FB3E3", "#EEF1F5", "#F2B57A", "#D9650A", "#6B2A05"],
    # Diverging for navy grounds: midpoint is a dark neutral that sits on the ground.
    "aimfahr_div_dark": ["#7FC4FF", "#2F86E0", "#1B4C8A", "#26344A", "#8E4A14", "#E07A1F", "#FFC27A"],
}

def colormaps() -> dict:
    """Return the AIMFAHR colormaps (registered on import)."""
    return {k: mpl.colormaps[k] for k in _CMAP_STOPS}

def _register_cmaps() -> None:
    for name, stops in _CMAP_STOPS.items():
        cm = _ramp(name, stops)
        for c in (cm, cm.reversed()):
            if c.name not in mpl.colormaps:
                mpl.colormaps.register(c)


# ---------------------------------------------------------------- styles
def use(theme: str = "dark", context: str = "web", *extra) -> None:
    """Apply an AIMFAHR theme and context, e.g. use("light", "poster").

    Also sets the default colormap: aimfahr_sun_dark on dark, aimfahr_sun on light. Extra arguments are
    passed on to plt.style.use after the AIMFAHR sheets (later ones win).
    """
    if theme not in THEMES:
        raise ValueError(f"theme must be one of {THEMES}, got {theme!r}")
    if context not in CONTEXTS:
        raise ValueError(f"context must be one of {CONTEXTS}, got {context!r}")
    plt.style.use([str(_HERE / f"{theme}.mplstyle"), str(_HERE / f"{context}.mplstyle"), *extra])
    mpl.rcParams["image.cmap"] = "aimfahr_sun_dark" if theme == "dark" else "aimfahr_sun"


# Generic journal column widths (inches): 89 mm single, 183 mm double.
_JOURNAL_WIDTH = {"single": 3.5, "onehalf": 5.5, "double": 7.2}

def journal_size(width: str | float = "single", aspect: float = 0.75) -> tuple:
    """Figure size for the journal context: (width, width * aspect) in inches.

    width: "single" (89 mm), "onehalf" (140 mm), "double" (183 mm) or inches.
    aspect: height / width. 0.75 suits one panel; use ~0.4 for a wide row.
    """
    w = _JOURNAL_WIDTH[width] if isinstance(width, str) else float(width)
    return (w, round(w * aspect, 3))


def direct_labels(ax=None, x="end", pad=0.01, **kw):
    """Write each line's label at its right-hand end, in the theme's text colour.

    Use instead of (or as well as) a legend when there are four lines or fewer.
    """
    ax = ax or plt.gca()
    color = mpl.rcParams["text.color"]
    x0, x1 = ax.get_xlim()
    for line in ax.get_lines():
        lab = line.get_label()
        if not lab or lab.startswith("_"):
            continue
        xd, yd = np.asarray(line.get_xdata(), float), np.asarray(line.get_ydata(), float)
        if xd.size == 0:
            continue
        i = -1 if x == "end" else int(np.argmin(np.abs(xd - x)))
        ax.annotate(lab, (xd[i], yd[i]), xytext=(6, 0), textcoords="offset points",
                    va="center", ha="left", color=color, fontweight=500,
                    annotation_clip=False, **kw)
        ax.plot([], [])  # keep cycle position stable
    return ax


_register_fonts()
_register_cmaps()

from .logo import add_logo, logo_path, LOGOS  # noqa: E402
