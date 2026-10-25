# AIMFAHR brand assets

Source SVGs for the AIMFAHR logos. These are not installed with the Python package; the package ships PNG versions in `src/aimfahr_mpl/logos/`.

## Files

| Pattern | Use |
| --- | --- |
| `aimfahr-mark-*` | The sun-and-A symbol |
| `aimfahr-wordmark-*` | The name only |
| `aimfahr-lockup-horizontal-*` | Mark and name side by side (default lockup) |
| `aimfahr-lockup-tagline-*` | Horizontal plus the full name |
| `aimfahr-lockup-stacked-*` | Mark above the name |
| `aimfahr-app-icon` | Mark on a navy tile (GitHub avatar, favicon) |

`-dark` files are for navy (`#0B1F3B`) or darker backgrounds: the A and the gap around Earth are transparent cut-outs. `-light` files are for white or pale backgrounds: the A is navy. `-bg` files include their own background. All text is outlined, so no fonts are needed.

## Colours

| Name | Hex | Use |
| --- | --- | --- |
| Navy | `#0B1F3B` | Home background, A on light |
| Sun core | `#FFD84A` | Top of the sun gradient |
| Flare orange | `#FF8A00` | Middle of the sun gradient, wordmark triangle |
| Sun limb | `#E5400B` | Bottom of the sun gradient |
| Earth | `#1C73E8` | Ocean |
| Land | `#3DDBA8` | Continents |
| Cyan | `#00D1FF` | Earth ring on dark |
| Blue | `#007BFF` | Wordmark accent, Earth ring on light |

Orange and land green are for graphics only; they fail contrast as text on white.

## Usage

- Clear space: at least the Earth's diameter on every side.
- Minimum widths: mark 32 px, horizontal lockup 180 px, tagline lockup 320 px.
- Don't recolour, stretch, rotate, outline or add shadows.
- Don't put a `-dark` file on a light background or the reverse.
- Don't rebuild the wordmark in a font.
- In text, write **AIMFAHR** in capitals and spell out the full name on first use: Artificial Intelligence Modeling Framework for Advanced Heliophysics Research.
