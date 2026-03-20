"""Create wavy line art based on the luminance of an input image.

Each horizontal line's amplitude, frequency, and thickness vary per-pixel
according to the local brightness of the source image, producing an
engraving-style effect with rich tonal range.
"""

from __future__ import annotations

import argparse

import numpy as np
from matplotlib import pyplot as plt
from matplotlib.collections import LineCollection


# ---------------------------------------------------------------------------
# Image loading
# ---------------------------------------------------------------------------

def load_image(path: str) -> np.ndarray:
    """Load an image as a normalised grayscale array in [0, 1] (0 = white, 1 = black)."""

    from matplotlib import image as imagelib

    data = imagelib.imread(path)
    if data.ndim == 3:
        gray = np.mean(data[:, :, :3], axis=2)
    else:
        gray = data.copy()
    # Normalise to 0-1 range
    if gray.max() > 1.0:
        gray = gray / 255.0
    return 1.0 - gray  # invert so 1 = dark, 0 = light


# ---------------------------------------------------------------------------
# Adaptive line placement
# ---------------------------------------------------------------------------

def adaptive_line_rows(img: np.ndarray, num_lines: int) -> np.ndarray:
    """Return row positions that concentrate lines in darker image regions."""

    row_darkness = np.mean(img, axis=1)
    # Add a small floor so light areas still get some lines
    row_darkness = row_darkness + 0.05
    cumulative = np.cumsum(row_darkness)
    cumulative /= cumulative[-1]
    targets = np.linspace(0, 1, num_lines + 2)[1:-1]
    return np.searchsorted(cumulative, targets)


# ---------------------------------------------------------------------------
# Per-pixel squiggle generation
# ---------------------------------------------------------------------------

def compute_squiggle(
    row_luminance: np.ndarray,
    x: np.ndarray,
    max_amplitude: float,
    max_frequency: float,
) -> tuple[np.ndarray, np.ndarray]:
    """Return (y_offsets, widths) for a squiggle modulated by *row_luminance*.

    Both amplitude and frequency increase in dark areas, producing tight
    oscillations where the image is dark and gentle waves where it is light.
    """

    n = len(x)
    y = np.zeros(n)
    widths = np.zeros(n)
    phase = 0.0

    for i in range(1, n):
        col = min(int(x[i]), len(row_luminance) - 1)
        darkness = row_luminance[col]

        local_freq = max_frequency * (0.08 + 0.92 * darkness)
        local_amp = max_amplitude * darkness

        dx = x[i] - x[i - 1]
        phase += local_freq * dx
        y[i] = local_amp * np.sin(phase)
        widths[i] = 0.4 + 2.5 * darkness

    widths[0] = widths[1]
    return y, widths


# ---------------------------------------------------------------------------
# Drawing
# ---------------------------------------------------------------------------

def draw_variable_width_line(
    ax: plt.Axes,
    x: np.ndarray,
    y: np.ndarray,
    widths: np.ndarray,
) -> None:
    """Draw a single polyline with per-segment varying width."""

    points = np.column_stack([x, y]).reshape(-1, 1, 2)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)
    lc = LineCollection(segments, linewidths=widths[1:], colors="black")
    ax.add_collection(lc)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    """Return the command line arguments."""

    parser = argparse.ArgumentParser(description="Generate squiggly line art")
    parser.add_argument("image", help="Path to the input image")
    parser.add_argument("output", help="Filename for the rendered art")
    parser.add_argument("--lines", type=int, default=80, help="Number of horizontal lines to draw")
    parser.add_argument("--frequency", type=float, default=0.15, help="Base frequency of the wave pattern")
    parser.add_argument("--amplitude", type=float, default=8.0, help="Maximum wave amplitude")
    return parser.parse_args()


def main() -> None:
    """Generate the art and save it to the requested file."""

    args = parse_args()
    img = load_image(args.image)
    height, width = img.shape

    # Determine which rows to draw lines on
    line_rows = adaptive_line_rows(img, args.lines)

    # X sample points (high resolution for smooth curves)
    x = np.linspace(0, width, width * 4, endpoint=False)

    fig, ax = plt.subplots(figsize=(10, 10 * height / width))
    ax.set_xlim(0, width)
    ax.set_ylim(-height, 0)
    ax.set_aspect("equal")
    ax.axis("off")

    for row in line_rows:
        row_lum = img[min(row, height - 1), :]
        y_offset, widths = compute_squiggle(row_lum, x, args.amplitude, args.frequency)
        y_plot = -(row + y_offset)
        draw_variable_width_line(ax, x, y_plot, widths)

    plt.savefig(args.output, bbox_inches="tight", dpi=150)
    print(f"Saved to {args.output}")


if __name__ == "__main__":
    main()
