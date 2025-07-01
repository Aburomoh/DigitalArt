"""Create wavy line art based on the luminance of an input image."""

from __future__ import annotations

import argparse
from matplotlib import pyplot as plt
from matplotlib import image as imagelib
import numpy as np


def load_image(path: str) -> np.ndarray:
    """Load an image as a normalized grayscale array."""

    data = imagelib.imread(path)
    if data.ndim == 3:
        return 1 - np.mean(data, axis=2) / 256
    return 1 - data / 256


def parse_args() -> argparse.Namespace:
    """Return the command line arguments."""

    parser = argparse.ArgumentParser(description="Generate squiggly line art")
    parser.add_argument("image", help="Path to the input image")
    parser.add_argument("output", help="Filename for the rendered art")
    parser.add_argument(
        "--lines",
        type=int,
        default=40,
        help="Number of horizontal lines to draw",
    )
    parser.add_argument(
        "--frequency",
        type=float,
        default=0.15,
        help="Frequency of the wave pattern",
    )
    return parser.parse_args()


def main() -> None:
    """Generate the art and save it to the requested file."""

    args = parse_args()
    img = load_image(args.image)

    L, W = img.shape
    N = W * 16
    t = np.linspace(0, W, N, endpoint=False)

    signal = np.cos(t * args.frequency) * 0.3 + (1 + (np.cos(t * args.frequency) > 0).astype(int)) / 2

    plt.figure(figsize=(10, 12))
    for k in range(0, L, int(L / args.lines)):
        segment = img[k : k + int(L / args.lines), :]
        A = (2 * np.mean(segment, axis=0) + np.max(segment, axis=0)) / 3
        line = np.repeat(A, 16) * signal
        plt.plot(t, line - 1.3 * k / int(L / args.lines), "k", linewidth=1 + 3 * np.mean(np.abs(line) ** 2))

    plt.axis("off")
    plt.savefig(args.output, bbox_inches="tight")


if __name__ == "__main__":
    main()

