"""把白底 JPG 卡通图抠成透明底 PNG + 黑色剪影 PNG。
输出: assets/games/cut/<key>.png 和 assets/games/sil/<key>.png
"""
import os, glob
from collections import deque
from PIL import Image

SRC = os.path.join(os.path.dirname(__file__), 'assets', 'games')
CUT = os.path.join(SRC, 'cut')
SIL = os.path.join(SRC, 'sil')
os.makedirs(CUT, exist_ok=True)
os.makedirs(SIL, exist_ok=True)

def near_white(p, tol=28):
    r, g, b, a = p
    return r > 255 - tol and g > 255 - tol and b > 255 - tol

def cutout(src_path, out_path):
    im = Image.open(src_path).convert('RGBA')
    w, h = im.size
    px = im.load()
    visited = [[False] * w for _ in range(h)]
    q = deque()
    for x in range(w):
        for y in (0, h - 1):
            if near_white(px[x, y]) and not visited[y][x]:
                visited[y][x] = True; q.append((x, y))
    for y in range(h):
        for x in (0, w - 1):
            if near_white(px[x, y]) and not visited[y][x]:
                visited[y][x] = True; q.append((x, y))
    while q:
        x, y = q.popleft()
        px[x, y] = (255, 255, 255, 0)
        for dx, dy in ((1,0),(-1,0),(0,1),(0,-1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h and not visited[ny][nx] and near_white(px[nx, ny]):
                visited[ny][nx] = True; q.append((nx, ny))
    # 边缘羽化 1px：半透明过渡
    alpha = im.split()[3].load()
    edge = []
    for y in range(h):
        for x in range(w):
            if alpha[x, y] == 255:
                for dx, dy in ((1,0),(-1,0),(0,1),(0,-1)):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < w and 0 <= ny < h and alpha[nx, ny] == 0:
                        edge.append((x, y)); break
    for x, y in edge:
        r, g, b, a = px[x, y]
        px[x, y] = (r, g, b, 150)
    im.save(out_path)
    return im

def silhouette(cut_im, out_path, color=(58, 51, 80)):
    im = cut_im.copy()
    px = im.load()
    w, h = im.size
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a:
                px[x, y] = (color[0], color[1], color[2], a)
    im.save(out_path)

if __name__ == '__main__':
    files = sorted(glob.glob(os.path.join(SRC, '*.jpg')))
    for f in files:
        key = os.path.splitext(os.path.basename(f))[0]
        cut = cutout(f, os.path.join(CUT, key + '.png'))
        silhouette(cut, os.path.join(SIL, key + '.png'))
        print('ok', key)
    print('done', len(files), 'images')
