"""Place AIMFAHR logos on matplotlib figures, positioned like a legend."""
from __future__ import annotations

from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.colors import to_rgb
from matplotlib.figure import Figure, SubFigure
from matplotlib.image import BboxImage, imread
from matplotlib.legend import Legend
from matplotlib.legend_handler import HandlerBase
from matplotlib.transforms import Bbox, TransformedBbox

__all__ = ["add_logo", "logo_path", "LOGOS"]

_DIR = Path(__file__).parent / "logos"

#: Logo names accepted by :func:`add_logo` and :func:`logo_path`.
LOGOS = ("mark", "icon", "wordmark", "horizontal", "tagline", "stacked")

# Default logo height as a multiple of the current font size.
_HEIGHT = {"mark": 3.4, "icon": 3.4, "stacked": 4.6, "wordmark": 1.6, "horizontal": 2.4, "tagline": 2.8}

_cache: dict[str, object] = {}


def logo_path(name: str = "mark", theme: str = "dark") -> Path:
    """Return the path of a bundled logo PNG.

    ``theme`` is the ground the logo sits on: "dark" (navy or darker) or
    "light" (white or pale). The app icon has a single version.
    """
    if name not in LOGOS:
        raise ValueError(f"logo must be one of {LOGOS}, got {name!r}")
    if theme not in ("dark", "light"):
        raise ValueError(f"theme must be 'dark' or 'light', got {theme!r}")
    return _DIR / ("icon.png" if name == "icon" else f"{name}-{theme}.png")


def _image(path: Path):
    key = str(path)
    if key not in _cache:
        _cache[key] = imread(path)
    return _cache[key]


def _is_dark(color) -> bool:
    try:
        r, g, b = to_rgb(color)
    except ValueError:
        return False
    return 0.2126 * r + 0.7152 * g + 0.0722 * b < 0.5


class _LogoHandle:
    """Stand-in legend handle that carries the image to draw."""

    def __init__(self, img, alpha):
        self.img, self.alpha = img, alpha


class _LogoHandler(HandlerBase):
    def legend_artist(self, legend, orig_handle, fontsize, handlebox):
        # Fill the whole handle box (including its descent) with the image.
        x0, y0 = -handlebox.xdescent, -handlebox.ydescent
        bbox = TransformedBbox(Bbox.from_bounds(x0, y0, handlebox.width, handlebox.height),
                               handlebox.get_transform())
        art = BboxImage(bbox, interpolation="antialiased", resample=True)
        art.set_data(orig_handle.img)
        if orig_handle.alpha is not None:
            art.set_alpha(orig_handle.alpha)
        handlebox.add_artist(art)
        return art


class LogoBox(Legend):
    """A one-entry legend whose entry is a logo image.

    Subclassing Legend reuses matplotlib's own placement: every ``loc`` code,
    ``loc="best"``, ``bbox_to_anchor``, ``borderaxespad`` and dragging.
    """

    def _auto_legend_data(self, renderer):
        # Same obstacles as a normal legend, plus any other legend or logo
        # already on the axes, so "best" doesn't land on top of them.
        bboxes, lines, offsets = super()._auto_legend_data(renderer)
        for art in self.parent._children + [self.parent.get_legend()]:
            if isinstance(art, Legend) and art is not self and art.get_visible():
                bboxes.append(art.get_window_extent(renderer))
        return bboxes, lines, offsets


def add_logo(target=None, logo: str = "mark", loc: str | int | tuple = "best", *,
             height: float | None = None, theme: str = "auto", alpha: float | None = None,
             bbox_to_anchor=None, pad: float = 0.4, frame: bool = False,
             draggable: bool = False, zorder: float = 5) -> LogoBox:
    """Add an AIMFAHR logo to an axes or a figure, placed like a legend.

    Parameters
    ----------
    target : Axes, Figure or None
        Where to put the logo. ``None`` uses the current axes. Pass a Figure
        to place it relative to the whole figure, like ``fig.legend``.
    logo : {"mark", "icon", "wordmark", "horizontal", "tagline", "stacked"}
        Which logo. See ``aimfahr_mpl.LOGOS``.
    loc : str, int or (x, y)
        Any legend location: "best", "upper right", "lower left", "center",
        "right", ... "best" (axes only) avoids lines, points, bars, text and
        any legend already on the axes. A pair of numbers places the
        lower-left corner in axes (or figure) fraction coordinates, as with
        ``legend(loc=(x, y))``.
        With a Figure, prefix "outside" to make constrained layout leave room
        for the logo beside the plots: "outside lower right" (the default for
        figures), "outside upper left", "outside right upper", ... Without the
        prefix the logo sits on top of whatever is at that corner.
    height : float, optional
        Logo height in points. Defaults scale with the font size, so the
        logo is in proportion in the web, slides, poster and journal styles.
    theme : {"auto", "dark", "light"}
        Which colour version. "auto" picks from the axes (or figure)
        background colour.
    alpha : float, optional
        Opacity of the logo, 0 to 1.
    bbox_to_anchor : optional
        As for ``legend``: the box that ``loc`` is relative to. Use it to put
        the logo outside the axes, e.g. ``loc="upper left",
        bbox_to_anchor=(1.02, 1)``.
    pad : float
        Space between the logo and the axes edge, in font-size units
        (legend ``borderaxespad``).
    frame : bool
        Draw a background box in the axes colour behind the logo. Useful over
        images and heatmaps.
    draggable : bool
        Let the logo be moved with the mouse in interactive windows.
    zorder : float
        Drawing order. Default draws above data and below most annotations.

    Returns
    -------
    LogoBox
        A Legend subclass. Call ``.remove()`` to take the logo off again.

    Examples
    --------
    >>> aimfahr_mpl.add_logo(ax)                          # best spot in ax
    >>> aimfahr_mpl.add_logo(ax, "horizontal", "upper left")
    >>> aimfahr_mpl.add_logo(fig, "tagline", "lower right")
    >>> aimfahr_mpl.add_logo(ax, "mark", "upper left", bbox_to_anchor=(1.01, 1))
    """
    if logo not in LOGOS:
        raise ValueError(f"logo must be one of {LOGOS}, got {logo!r}")
    if target is None:
        target = plt.gca()
    is_axes = isinstance(target, Axes)
    if not is_axes and not isinstance(target, (Figure, SubFigure)):
        raise TypeError("target must be a matplotlib Axes or Figure")

    if theme == "auto":
        ground = target.get_facecolor()
        if is_axes and ground[3] == 0:  # transparent axes: use the figure colour
            ground = target.figure.get_facecolor()
        theme = "dark" if _is_dark(ground) else "light"
    img = _image(logo_path(logo, theme))
    aspect = img.shape[1] / img.shape[0]

    fs = mpl.rcParams["font.size"]
    if height is None:
        height = _HEIGHT[logo] * fs
    width = height * aspect

    # Legend sizes its handle box from fontsize * handleheight, minus a
    # descent of 0.35 * fontsize * (handleheight - 0.7). Solve so the drawn
    # image is exactly `height` points tall.
    handleheight = (height / fs - 0.245) / 0.65
    handlelength = width / fs

    if not is_axes and loc in ("best", 0):
        loc = "outside lower right"

    handle = _LogoHandle(img, alpha)
    box = LogoBox(target, [handle], [""], loc=loc, bbox_to_anchor=bbox_to_anchor,
                  handler_map={_LogoHandle: _LogoHandler()},
                  handlelength=handlelength, handleheight=handleheight, handletextpad=0,
                  borderpad=0.35 if frame else 0.0, borderaxespad=pad, labelspacing=0,
                  fontsize=fs, frameon=frame, fancybox=True, framealpha=0.85,
                  facecolor="inherit", edgecolor="none", shadow=False)
    # Drop the empty text column so the box hugs the image.
    for t in box.get_texts():
        t.set_fontsize(0.01)
    box.set_zorder(zorder)
    if is_axes:
        target.add_artist(box)
        # add_artist clips to the axes; logos may sit outside (bbox_to_anchor),
        # and unclipped artists are also counted by tight/constrained layout.
        box.set_clip_on(False)
    else:
        target.legends.append(box)
    if draggable:
        box.set_draggable(True)
    return box
