from PIL import Image
import matplotlib.pyplot as plt
import numpy as np

FileName = "Abraham_Lincoln.jpg"

with Image.open(FileName) as im:
    img = np.mean(np.array(im), axis=2)
    # im.show()

L = np.shape(img)[0]
W = np.shape(img)[1]

Canvas = np.zeros(np.shape(img)) + 255

plt.figure(figsize=(10, 12))


def pick(L, W):
    a, b = 0, 0
    while np.abs(a - b) < np.max((L, W)) or np.abs(a - b) > 2 * L + 2 * W - np.max(
        (L, W)
    ):
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

    return (point1), (point2)


def int_points(p1, p2):
    H = p1[0] - p2[0]
    V = p1[1] - p2[1]

    steps = np.max((np.abs(H), np.abs(V)))
    x = np.round(np.linspace(p1[0], p2[0], steps))
    y = np.round(np.linspace(p1[1], p2[1], steps))
    return x, y


Diff = 128 + img / 2

for _ in range(5000):
    CORD = []
    for trial in range(10):
        p1, p2 = pick(L, W)
        x, y = int_points(p1, p2)
        Line = list(zip(y.astype(int), x.astype(int)))
        val = 0
        for i in Line:
            val += Diff[i] / len(Line)
        if trial == 0:
            val_high = val
            val_low = val
            line_dark = Line
            line_light = Line
        elif val < val_low:
            line_dark = Line
            val_low = val
        elif val > val_high:
            line_light = Line
            val_high = val
    for i in line_dark:
        Canvas[i] -= 255
    for i in line_light:
        Canvas[i] += 255

    Canvas = np.clip(Canvas, 0, 255)
    Diff = 128 + (img - Canvas) / 2
imgg = Image.fromarray(Canvas, "L")
# imgg.save('my.png')
# imgg.show()

Diff = 128 + (img - Canvas) / 2

plt.figure()
plt.imshow(img, cmap="gray", vmin=0, vmax=255)
plt.title("Original")
plt.figure()
plt.imshow(Canvas, cmap="gray", vmin=0, vmax=255)
plt.title("Line Art")
plt.figure()
plt.imshow(Diff, cmap="gray", vmin=0, vmax=255)
plt.title("Differntial image")
