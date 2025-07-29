from math import pi, sin, cos


def create():
    print('<svg width="164" height="164" xmlns="http://www.w3.org/2000/svg">')
    N = 20
    S = 41
    s = 20
    r = S - s // 2
    rx = r + s
    points = []
    for i in range(N):
        a = (0.15 + 1.35 * i / N) * pi
        points.append((2 * S + rx * cos(a), s + r - r * sin(a)))
    for i in range(N + 1):
        a = (0.5 - 1.35 * i / N) * pi
        points.append((2 * S + rx * cos(a), s + r + 2 * r - r * sin(a)))
    for i, (x, y) in enumerate(points):
        g = 200 - i * 40 // N
        b = 150 + i * 40 // N
        r = 150
        color = f'#{r:02X}{g:02X}{b:02X}'
        print(f' <circle cx="{x:.0f}" cy="{y:.0f}" r="{s}" fill="{color}"/>')

    print('</svg>')


if __name__ == '__main__':
    create()
