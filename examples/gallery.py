"""Render the AIMFAHR style gallery. Run: python examples/gallery.py"""
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
import aimfahr_mpl

OUT = Path(__file__).resolve().parent.parent / "docs" / "gallery"
OUT.mkdir(exist_ok=True)
rng = np.random.default_rng(7)

# --- synthetic storm data (illustrative only) -------------------------------
t = np.linspace(-12, 60, 289)                       # hours from storm onset
def storm(t, depth, rec):
    main = np.where(t < 0, 0, -depth * (1 - np.exp(-t / 4)))
    return 10 * np.exp(-((t + 3) / 2) ** 2) + main * np.exp(-np.clip(t - 8, 0, None) / rec)
obs = storm(t, 190, 18) + rng.normal(0, 4, t.size)
xgb = storm(t + 0.8, 175, 20) + rng.normal(0, 2, t.size)
lstm = storm(t + 1.6, 160, 15) + rng.normal(0, 2, t.size)
pers = np.roll(obs, 12); pers[:12] = obs[0]
band = 12 + 0.08 * np.abs(xgb)

def timeseries(ax):
    ax.fill_between(t, xgb - band, xgb + band, color="C0", alpha=0.18, lw=0, label="_band")
    ax.plot(t, obs, color=plt.rcParams["text.color"], lw=plt.rcParams["lines.linewidth"] * 0.8, label="Observed")
    ax.plot(t, xgb, color="C0", label="XGBoost")
    ax.plot(t, lstm, color="C1", label="LSTM")
    ax.plot(t, pers, color="C2", ls="--", label="Persistence")
    ax.axhline(0, color=plt.rcParams["axes.edgecolor"], lw=plt.rcParams["axes.linewidth"])
    ax.set(xlabel="Hours from storm onset", ylabel="Dst (nT)", title="Dst during a severe storm")
    ax.legend(loc="lower right", ncols=2)

def scatter(ax, fig):
    obs_rho = 10 ** rng.normal(-11.8, 0.35, 900)
    kp = np.clip(rng.gamma(2.2, 1.3, 900), 0, 9)
    pred = obs_rho * 10 ** (rng.normal(0, 0.08, 900) + 0.02 * (kp - 3))
    sc = ax.scatter(obs_rho, pred, c=kp, s=plt.rcParams["lines.markersize"] ** 2 * 0.5, alpha=0.9, vmin=0, vmax=9)
    lim = [obs_rho.min() * 0.8, obs_rho.max() * 1.2]
    ax.plot(lim, lim, color=plt.rcParams["axes.labelcolor"], lw=plt.rcParams["axes.linewidth"] * 1.2, ls="--")
    ax.set(xscale="log", yscale="log", xlim=lim, ylim=lim, xlabel=r"Observed $\rho$ (kg m$^{-3}$)",
           ylabel=r"Predicted $\rho$ (kg m$^{-3}$)", title="Model vs observed density")
    cb = fig.colorbar(sc, ax=ax, pad=0.02); cb.set_label("Kp"); cb.outline.set_visible(False)

def heatmap(ax, fig):
    hrs = np.linspace(0, 72, 145); alt = np.linspace(250, 600, 71)
    H, A = np.meshgrid(hrs, alt)
    base = -11 - (A - 250) / 120
    enh = 0.9 * np.exp(-((H - 30) / 10) ** 2) * (A / 600)
    diurnal = 0.15 * np.sin(2 * np.pi * H / 24)
    Z = base + enh + diurnal
    m = ax.pcolormesh(H, A, Z, shading="auto")
    ax.set(xlabel="Hours", ylabel="Altitude (km)", title=r"Thermospheric density, $\log_{10}\rho$")
    ax.grid(False)
    cb = fig.colorbar(m, ax=ax, pad=0.02); cb.set_label(r"$\log_{10}\rho$ (kg m$^{-3}$)"); cb.outline.set_visible(False)

def bars(ax):
    cls = ["G1", "G2", "G3", "G4", "G5"]; x = np.arange(len(cls)); w = 0.26
    vals = {"XGBoost": [6, 9, 14, 22, 31], "LSTM": [7, 11, 17, 27, 38], "Persistence": [10, 16, 25, 41, 60]}
    for i, (k, v) in enumerate(vals.items()):
        ax.bar(x + (i - 1) * w, v, w, label=k, color=f"C{i}")  # same colour per model as the line plot
    ax.set_xticks(x, cls); ax.grid(axis="x", visible=False)
    ax.set(xlabel="NOAA storm class", ylabel="RMSE (nT)", title="Error grows with storm strength")
    ax.legend(loc="upper left")

def residuals(ax, fig, theme):
    hrs = np.linspace(0, 48, 97); lat = np.linspace(-80, 80, 81)
    H, L = np.meshgrid(hrs, lat)
    R = 0.35 * np.sin(np.radians(L) * 2) * np.exp(-((H - 20) / 9) ** 2) + 0.12 * np.cos(2 * np.pi * H / 24) * np.cos(np.radians(L))
    cmap = "aimfahr_div_dark" if theme == "dark" else "aimfahr_div"
    m = ax.pcolormesh(H, L, R, cmap=cmap, vmin=-0.4, vmax=0.4, shading="auto")
    ax.set(xlabel="Hours", ylabel="Latitude (°)", title="Density residual, model − obs (log)")
    ax.grid(False)
    cb = fig.colorbar(m, ax=ax, pad=0.02); cb.outline.set_visible(False)

for theme in aimfahr_mpl.THEMES:
    # web: four-panel overview
    aimfahr_mpl.use(theme, "web")
    fig, axs = plt.subplots(2, 2, figsize=(13, 8.4))
    timeseries(axs[0, 0]); scatter(axs[0, 1], fig); heatmap(axs[1, 0], fig); bars(axs[1, 1])
    fig.savefig(OUT / f"{theme}-web.png"); plt.close(fig)
    # web: residual map
    fig, ax = plt.subplots(); residuals(ax, fig, theme)
    fig.savefig(OUT / f"{theme}-web-diverging.png"); plt.close(fig)
    # slides: one message per chart
    aimfahr_mpl.use(theme, "slides")
    fig, ax = plt.subplots(); timeseries(ax)
    fig.savefig(OUT / f"{theme}-slides.png"); plt.close(fig)
    # poster
    aimfahr_mpl.use(theme, "poster")
    fig, ax = plt.subplots(); bars(ax)
    fig.savefig(OUT / f"{theme}-poster.png", dpi=150); plt.close(fig)
# --- journal: two-column figure, panels (a) and (b) -------------------------
aimfahr_mpl.use("light", "journal")
fig, (a1, a2) = plt.subplots(1, 2, figsize=aimfahr_mpl.journal_size("double", 0.38))
a1.plot(t, obs, color="0.15", lw=0.9, label="Observed")
a1.plot(t, xgb, color="C0", label="XGBoost"); a1.plot(t, lstm, color="C1", label="LSTM")
a1.set(xlabel="Hours from storm onset", ylabel="Dst (nT)", title="(a)"); a1.legend(loc="lower right")
heatmap(a2, fig); a2.set_title("(b)")
fig.savefig(OUT / "journal-double.png", dpi=300); plt.close(fig)

# --- logos: placement examples -------------------------------------------------
x = np.linspace(0, 10, 200)
for theme in aimfahr_mpl.THEMES:
    aimfahr_mpl.use(theme, "web")
    fig, axs = plt.subplots(2, 2, figsize=(12, 7.5))
    a = axs[0, 0]; a.plot(x, np.sin(x) + x / 3, label="A"); a.plot(x, np.cos(x) + x / 3, label="B")
    a.legend(loc="best"); aimfahr_mpl.add_logo(a); a.set_title('add_logo(ax)  ·  loc="best"')
    a = axs[0, 1]; a.plot(x, 10 - x); aimfahr_mpl.add_logo(a, "horizontal", "upper right")
    a.set_title('add_logo(ax, "horizontal", "upper right")')
    a = axs[1, 0]; heatmap(a, fig); aimfahr_mpl.add_logo(a, "mark", "upper right", frame=True)
    a.set_title('add_logo(ax, "mark", "upper right", frame=True)')
    a = axs[1, 1]; a.bar(range(5), [3, 5, 2, 6, 4]); a.grid(axis="x", visible=False)
    aimfahr_mpl.add_logo(a, "icon", "upper left", bbox_to_anchor=(1.02, 1))
    a.set_title('add_logo(ax, "icon", "upper left", bbox_to_anchor=(1.02, 1))', fontsize=10)
    aimfahr_mpl.add_logo(fig, "tagline")
    fig.savefig(OUT / f"logo-placement-{theme}.png", dpi=110); plt.close(fig)

# slides with the horizontal lockup in the figure corner
aimfahr_mpl.use("dark", "slides")
fig, ax = plt.subplots(); timeseries(ax)
aimfahr_mpl.add_logo(fig, "horizontal", "outside upper right")
fig.savefig(OUT / "logo-slides.png"); plt.close(fig)

# --- logos: every bundled logo ----------------------------------------------
from matplotlib.image import imread
names = list(aimfahr_mpl.LOGOS)
W, ROW = 6.0, 1.5                              # inches per column, per row
fig = plt.figure(figsize=(2 * W, ROW * len(names)), layout="none")
for col, (theme, ground, ink) in enumerate([("dark", "#0B1F3B", "#E8EEF7"), ("light", "#FFFFFF", "#0B1F3B")]):
    ax = fig.add_axes([col * 0.5, 0, 0.5, 1]); ax.set_facecolor(ground)
    ax.set_xlim(0, W); ax.set_ylim(ROW * len(names), 0); ax.set_axis_off()
    ax.add_patch(plt.Rectangle((0, 0), W, ROW * len(names), color=ground, zorder=0))
    for row, name in enumerate(names):
        img = imread(aimfahr_mpl.logo_path(name, theme))
        aspect = img.shape[1] / img.shape[0]
        h = min(1.0, 3.6 / aspect)                 # fit inside the right-hand 3.6 in
        x0, y0 = 2.1, row * ROW + (ROW - h) / 2
        ax.imshow(img, extent=(x0, x0 + h * aspect, y0 + h, y0), interpolation="antialiased", zorder=2)
        label = f'"{name}"' if name == "icon" else f'"{name}"\n{theme}'
        ax.text(0.3, row * ROW + ROW / 2, label, va="center", ha="left", color=ink,
                fontsize=13, fontweight=600, linespacing=1.4)
    ax.set_aspect("equal")
fig.savefig(OUT / "logos-all.png", dpi=110, bbox_inches=None, pad_inches=0); plt.close(fig)

print("wrote", sorted(p.name for p in OUT.glob("*.png")))
