"""Generate stylized line art from an input image."""

from __future__ import annotations

import argparse
from typing import Tuple
from PIL import Image
import matplotlib.pyplot as plt
import numpy as np


def pick(L: int, W: int) -> Tuple[Tuple[int, int], Tuple[int, int]]:
    """Randomly pick two points on the image border.

    The points are guaranteed to be far enough apart so that a line between them
    crosses the image in an interesting way.
    """

    a, b = 0, 0
    while np.abs(a - b) < np.max((L, W)) or np.abs(a - b) > 2 * L + 2 * W - np.max((L, W)):
        a = np.random.randint(2 * L + 2 * W)
        b = np.random.randint(2 * L + 2 * W)

    if a < L:
        point1 = (0, a)
    elif a < L + W:
        point1 = (a - L, L - 1)
    elif a < 2 * L + W:
        point1 = (W - 1, a - W - L)
    else:
        point1 = (a - W - 2 * L, 0)

    if b < L:
        point2 = (0, b)
    elif b < L + W:
        point2 = (b - L, L - 1)
    elif b < 2 * L + W:
        point2 = (W - 1, b - W - L)
    else:
        point2 = (b - W - 2 * L, 0)

    return point1, point2


def int_points(p1: Tuple[int, int], p2: Tuple[int, int]) -> Tuple[np.ndarray, np.ndarray]:
    """Return the integer coordinates along the line connecting two points."""

    H = p1[0] - p2[0]
    V = p1[1] - p2[1]

    steps = np.max((np.abs(H), np.abs(V)))
    x = np.round(np.linspace(p1[0], p2[0], steps))
    y = np.round(np.linspace(p1[1], p2[1], steps))
    return x, y


def generate_art(img: np.ndarray, iterations: int = 5000) -> np.ndarray:
    """Return a canvas rendered as line art using the provided image."""

    L, W = img.shape
    canvas = np.zeros_like(img) + 255
    diff = 128 + img / 2

    for _ in range(iterations):
        for _ in range(10):
            p1, p2 = pick(L, W)
            x, y = int_points(p1, p2)
            line = list(zip(y.astype(int), x.astype(int)))
            val = diff[tuple(zip(*line))].mean()

            if "best_dark" not in locals() or val < best_dark_val:
                best_dark = line
                best_dark_val = val
            if "best_light" not in locals() or val > best_light_val:
                best_light = line
                best_light_val = val

        for point in best_dark:
            canvas[point] -= 255
        for point in best_light:
            canvas[point] += 255

        canvas = np.clip(canvas, 0, 255)
        diff = 128 + (img - canvas) / 2

    return canvas


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""

    parser = argparse.ArgumentParser(description="Generate line art from an image")
    parser.add_argument("image", help="Path to the input image")
    parser.add_argument("output", help="Filename for the rendered art")
    parser.add_argument(
        "--iterations",
        type=int,
        default=5000,
        help="Number of iterations used to generate the art",
    )
    return parser.parse_args()


def main() -> None:
    """Entry point for command line execution."""

    args = parse_args()
    with Image.open(args.image) as im:
        img = np.mean(np.array(im), axis=2)

    art = generate_art(img, iterations=args.iterations)
    Image.fromarray(art.astype(np.uint8), "L").save(args.output)

    plt.figure()
    plt.imshow(img, cmap="gray", vmin=0, vmax=255)
    plt.title("Original")
    plt.figure()
    plt.imshow(art, cmap="gray", vmin=0, vmax=255)
    plt.title("Line Art")


if __name__ == "__main__":
    main()

