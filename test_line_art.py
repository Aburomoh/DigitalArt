"""Tests for Line_art.py geometry helpers."""

import numpy as np
from Line_art import int_points, line_pixels, generate_pins


def test_int_points_diagonal():
    """Points along a diagonal should start and end at the given coordinates."""
    x, y = int_points((0, 0), (4, 4))
    assert x[0] == 0 and y[0] == 0
    assert x[-1] == 4 and y[-1] == 4
    assert np.array_equal(x, y)  # diagonal: row == col


def test_int_points_horizontal():
    """A horizontal line should have constant y."""
    x, y = int_points((0, 0), (3, 0))
    assert np.all(y == 0)
    assert len(x) == 3


def test_int_points_vertical():
    """A vertical line should have constant x."""
    x, y = int_points((0, 0), (0, 5))
    assert np.all(x == 0)
    assert len(y) == 5


def test_int_points_single_point():
    """Identical start and end should return a single point."""
    x, y = int_points((3, 7), (3, 7))
    assert len(x) == 1
    assert len(y) == 1


def test_line_pixels_endpoints():
    """line_pixels should include both endpoints."""
    p1, p2 = (0, 0), (5, 3)
    rows, cols = line_pixels(p1, p2)
    assert rows[0] == p1[0] and cols[0] == p1[1]
    assert rows[-1] == p2[0] and cols[-1] == p2[1]


def test_generate_pins_on_border():
    """All pins should lie on the image border."""
    H, W = 100, 80
    pins = generate_pins(H, W, num_pins=50)
    assert len(pins) == 50
    for r, c in pins:
        assert r == 0 or r == H - 1 or c == 0 or c == W - 1


def test_generate_pins_count():
    """generate_pins should return the requested number of pins."""
    pins = generate_pins(200, 150, num_pins=300)
    assert len(pins) == 300
