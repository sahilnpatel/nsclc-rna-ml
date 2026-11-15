"""Small dependency-free SVG charts; exact data tables accompany every figure."""
from html import escape
from pathlib import Path

COLORS = ['#2563eb', '#e76f51', '#2a9d8f', '#9b5de5', '#d49a00', '#d45087', '#4e657b', '#7b9e32']


def scatter(path, x, y, labels, title, xlabel, ylabel):
    lo_x, hi_x = min(x), max(x)
    lo_y, hi_y = min(y), max(y)
    dx, dy = max(hi_x-lo_x, 1e-10), max(hi_y-lo_y, 1e-10)
    parts = ['<svg xmlns="http://www.w3.org/2000/svg" width="900" height="620" viewBox="0 0 900 620">',
             '<rect width="900" height="620" fill="#fff"/>',
             '<g font-family="Arial,sans-serif" fill="#172a3a">',
             f'<text x="60" y="34" font-size="21">{escape(title)}</text>',
             '<path d="M85 65V535H865" fill="none" stroke="#526777"/>']
    for i in range(6):
        xx, yy = 100+150*i, 520-88*i
        parts += [f'<text x="{xx}" y="558" text-anchor="middle" font-size="12">{lo_x+dx*i/5:.2f}</text>',
                  f'<text x="77" y="{yy+4}" text-anchor="end" font-size="12">{lo_y+dy*i/5:.2f}</text>']
    for a,b,l in zip(x,y,labels):
        parts.append(f'<circle cx="{100+750*(a-lo_x)/dx:.2f}" cy="{520-440*(b-lo_y)/dy:.2f}" r="2.8" fill="{COLORS[int(l)%len(COLORS)]}" opacity="0.55"/>')
    parts += [f'<text x="470" y="595" text-anchor="middle" font-size="15">{escape(xlabel)}</text>',
              f'<text transform="translate(22 300) rotate(-90)" text-anchor="middle" font-size="15">{escape(ylabel)}</text>', '</g></svg>']
    Path(path).write_text('\n'.join(parts))


def lines(path, x, series, title, ylabel):
    vals = [v for data in series.values() for v in data]
    low, high = min(vals), max(vals)
    delta = max(high-low, 1e-10)
    parts = ['<svg xmlns="http://www.w3.org/2000/svg" width="900" height="530">',
             '<rect width="900" height="530" fill="white"/>', '<g font-family="Arial,sans-serif" fill="#172a3a">',
             f'<text x="60" y="34" font-size="20">{escape(title)}</text>',
             '<path d="M85 65V420H860" fill="none" stroke="#526777"/>']
    for i in range(5):
        v=low+delta*i/4; yy=400-310*i/4
        parts.append(f'<text x="77" y="{yy+4}" text-anchor="end" font-size="12">{v:.3f}</text>')
    for i,k in enumerate(x):
        parts.append(f'<text x="{105+735*i/max(len(x)-1,1)}" y="445" text-anchor="middle">{k}</text>')
    for j,(label,data) in enumerate(series.items()):
        color=COLORS[j]
        pts=' '.join(f'{105+735*i/max(len(x)-1,1):.1f},{400-310*(v-low)/delta:.1f}' for i,v in enumerate(data))
        parts.append(f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="3"/>')
        parts.append(f'<text x="{90+j*260}" y="505" font-size="13" fill="{color}">{escape(label)}</text>')
    parts += [f'<text transform="translate(20 260) rotate(-90)" text-anchor="middle">{escape(ylabel)}</text>',
              '<text x="470" y="475" text-anchor="middle">Number of clusters (k)</text>','</g></svg>']
    Path(path).write_text('\n'.join(parts))
