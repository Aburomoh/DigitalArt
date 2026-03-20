"""Generate stylized line art from an input image.

Reconstructs a photograph using only dark, border-to-border lines of uniform
thickness.  A greedy algorithm selects the line that most reduces the error
between the current canvas and the target at each step, producing a
recognisable likeness with surprisingly few lines.
"""

from __future__ import annotations

import argparse
from typing import Tuple

import numpy as np
from PIL import Image


# ---------------------------------------------------------------------------
# Geometry helpers
# ---------------------------------------------------------------------------

def generate_pins(height: int, width: int, num_pins: int = 200) -> list[Tuple[int, int]]:
    """Return *num_pins* (row, col) coordinates evenly spaced around the image border."""

    perimeter = 2 * height + 2 * width
    pins: list[Tuple[int, int]] = []
    for i in range(num_pins):
        pos = i * perimeter / num_pins
        if pos < width:
            pins.append((0, min(int(pos), width - 1)))
        elif pos < width + height:
            pins.append((min(int(pos - width), height - 1), width - 1))
        elif pos < 2 * width + height:
            pins.append((height - 1, max(int(2 * width + height - pos), 0)))
        else:
            pins.append((max(int(2 * width + 2 * height - pos), 0), 0))
    return pins


def line_pixels(p1: Tuple[int, int], p2: Tuple[int, int]) -> Tuple[np.ndarray, np.ndarray]:
    """Return integer (row, col) arrays for the pixels along the line from *p1* to *p2*."""

    dr = p2[0] - p1[0]
    dc = p2[1] - p1[1]
    steps = max(abs(dr), abs(dc))
    if steps == 0:
        return np.array([p1[0]]), np.array([p1[1]])
    rows = np.round(np.linspace(p1[0], p2[0], steps + 1)).astype(int)
    cols = np.round(np.linspace(p1[1], p2[1], steps + 1)).astype(int)
    return rows, cols


# Keep the original helpers available for tests / backwards compatibility
pick = None  # removed – use generate_pins instead


def int_points(p1: Tuple[int, int], p2: Tuple[int, int]) -> Tuple[np.ndarray, np.ndarray]:
    """Return the integer coordinates along the line connecting two points."""

    dr = p1[0] - p2[0]
    dc = p1[1] - p2[1]
    steps = max(abs(dr), abs(dc))
    if steps == 0:
        return np.array([p1[0]], dtype=float), np.array([p1[1]], dtype=float)
    x = np.round(np.linspace(p1[0], p2[0], steps))
    y = np.round(np.linspace(p1[1], p2[1], steps))
    return x, y


# ---------------------------------------------------------------------------
# Core algorithm
# ---------------------------------------------------------------------------

def precompute_lines(
    pins: list[Tuple[int, int]],
    height: int,
    width: int,
) -> dict[Tuple[int, int], Tuple[np.ndarray, np.ndarray]]:
    """Build a cache mapping every (i, j) pin pair to its pixel coordinates."""

    cache: dict[Tuple[int, int], Tuple[np.ndarray, np.ndarray]] = {}
    n = len(pins)
    for i in range(n):
        for j in range(i + 1, n):
            rows, cols = line_pixels(pins[i], pins[j])
            rows = np.clip(rows, 0, height - 1)
            cols = np.clip(cols, 0, width - 1)
            cache[(i, j)] = (rows, cols)
    return cache


def generate_art(
    img: np.ndarray,
    num_pins: int = 200,
    num_lines: int = 4000,
    line_darkness: int = 30,
    min_distance: int = 20,
) -> np.ndarray:
    """Return a canvas rendered as line art using the provided image.

    Parameters
    ----------
    img : 2-D float array (0 = black, 255 = white)
    num_pins : number of anchor points placed around the border
    num_lines : maximum number of lines to draw
    line_darkness : how much each line darkens the canvas (0–255)
    min_distance : minimum pin-index separation (avoids very short lines)
    """

    height, width = img.shape
    pins = generate_pins(height, width, num_pins)
    cache = precompute_lines(pins, height, width)

    canvas = np.full_like(img, 255, dtype=np.float64)
    error = img.astype(np.float64) - canvas  # negative where canvas is too bright

    current_pin = 0
    used_sequence: list[int] = [current_pin]

    for iteration in range(num_lines):
        best_score = -np.inf
        best_pin = -1

        for j in range(num_pins):
            if abs(j - current_pin) < min_distance and abs(j - current_pin) > num_pins - min_distance:
                continue
            if j == current_pin:
                continue
            key = (min(current_pin, j), max(current_pin, j))
            rows, cols = cache[key]
            # Score = how much darkening is needed along this line
            score = -np.mean(error[rows, cols])
            if score > best_score:
                best_score = score
                best_pin = j

        if best_pin == -1 or best_score <= 0:
            break  # no line can improve the image

        key = (min(current_pin, best_pin), max(current_pin, best_pin))
        rows, cols = cache[key]
        canvas[rows, cols] = np.clip(canvas[rows, cols] - line_darkness, 0, 255)
        error = img.astype(np.float64) - canvas

        used_sequence.append(best_pin)
        current_pin = best_pin

        if (iteration + 1) % 500 == 0:
            print(f"  {iteration + 1} / {num_lines} lines drawn")

    print(f"Finished after {len(used_sequence) - 1} lines")
    return canvas.astype(np.uint8)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""

    parser = argparse.ArgumentParser(
        description="Generate line art from an image using border-to-border lines",
    )
    parser.add_argument("image", help="Path to the input image")
    parser.add_argument("output", help="Filename for the rendered art")
    parser.add_argument("--num-pins", type=int, default=200, help="Anchor points on the border")
    parser.add_argument("--num-lines", type=int, default=4000, help="Maximum lines to draw")
    parser.add_argument("--line-darkness", type=int, default=30, help="Darkness per line (0-255)")
    parser.add_argument("--min-distance", type=int, default=20, help="Minimum pin separation")
    parser.add_argument("--max-size", type=int, default=500, help="Downscale longest side to this (0 = no resize)")
    return parser.parse_args()


def main() -> None:
    """Entry point for command line execution."""

    args = parse_args()
    with Image.open(args.image) as im:
        if args.max_size > 0:
            im.thumbnail((args.max_size, args.max_size))
        img = np.mean(np.array(im), axis=2)

    print(f"Image size: {img.shape[1]}x{img.shape[0]}")
    print(f"Generating line art with {args.num_pins} pins, up to {args.num_lines} lines ...")

    art = generate_art(
        img,
        num_pins=args.num_pins,
        num_lines=args.num_lines,
        line_darkness=args.line_darkness,
        min_distance=args.min_distance,
    )
    Image.fromarray(art, "L").save(args.output)
    print(f"Saved to {args.output}")


if __name__ == "__main__":
    main()
