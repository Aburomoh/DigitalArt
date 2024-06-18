from PIL import Image
import matplotlib.pyplot as plt
import numpy as np
       # symbol duration
FileName = 'art-photography-or-pop-art.png'

with Image.open(FileName) as im:
    img = np.array(im)/256
    # im.show()
    
L = np.shape(img)[0]
W = np.shape(img)[1]

Canvas = np.zeros(np.shape(img))+255

plt.figure(figsize=(10,12))

def pick(L,W):
    a,b = 0,0
    while np.abs(a-b) < np.max((L,W)) or np.abs(a-b) > 2*L +2*W -np.max((L,W)):
        a = np.random.randint(2*L+2*W)
        b = np.random.randint(2*L+2*W)
    if a<L:
        point1 = (0,a)
    elif a<L+W:
        point1 = (a-L,L-1)
    elif a<2*L+W:
        point1 = (W-1,a-W-L)
    else:
        point1 = (a-W-2*L,0)
    
    if b<L:
        point2 = (0,b)
    elif b<L+W:
        point2 = (b-L,L-1)
    elif b<2*L+W:
        point2 = (W-1,b-W-L)
    else:
        point2 = (b-W-2*L,0)
        
    return (point1),(point2)

def int_points(p1,p2):
    H = p1[0]-p2[0]
    V = p1[1]-p2[1]
    
    steps = np.max((np.abs(H),np.abs(V)))
    x = np.round(np.linspace(p1[0],p2[0],steps))
    y = np.round(np.linspace(p1[1],p2[1],steps))
    return x,y
        
for _ in range(4000):
    val_old = 255000
    CORD = []
    for _ in range(6):
        p1,p2 = pick(L,W)
        x,y = int_points(p1,p2)
        cord = list(zip(y.astype(int),x.astype(int)))
        val = 0
        for i in cord:
            val += img[i]/len(cord)
        if val<val_old:
            CORD = cord
            val_old = val
    blank = np.zeros(np.shape(img))
    for i in CORD:
        blank[i] = 20
        img[i] = min(1,img[i]+0.15)
    Canvas -= blank
imgg = Image.fromarray(Canvas, 'L')
# imgg.save('my.png')
# imgg.show()

Diff = 128+(im-Canvas)/2

plt.figure()
plt.imshow(im,cmap='gray', vmin=0, vmax=255)
plt.title("Original")
plt.figure()
plt.imshow(Canvas,cmap='gray', vmin=0, vmax=255)
plt.title("Line Art")
plt.figure()
plt.imshow(Diff,cmap='gray', vmin=0, vmax=255)
plt.title("Differntial image")


