import math
import time
import shutil
import sys

width = shutil.get_terminal_size((80, 24)).columns
height = 24
cx, cy = width // 2, height // 2

sys.stdout.write('\033[2J\033[?25l')
frame = 0
try:
    while True:
        output = [[0 for _ in range(width)] for _ in range(height)]
        for i in range(200):
            t = i * 0.1 + frame * 0.05
            r = 2 + 1.5 * t
            x = int(cx + r * math.cos(t) * 1.2)
            y = int(cy + r * math.sin(t) * 0.6)
            if 0 <= x < width and 0 <= y < height:
                output[y][x] = min(255, output[y][x] + 50)
        for i in range(120):
            t = i * 0.2 - frame * 0.08
            r = 1 + 2 * t
            x = int(cx + r * math.cos(-t) * 1.5)
            y = int(cy + r * math.sin(-t) * 0.5)
            if 0 <= x < width and 0 <= y < height:
                output[y][x] = min(255, output[y][x] + 70)

        sys.stdout.write('\033[H')
        for row in output:
            line = ''
            for v in row:
                if v == 0:
                    line += ' '
                elif v < 50:
                    line += '.'
                elif v < 100:
                    line += '+'
                elif v < 150:
                    line += '*'
                elif v < 200:
                    line += '#'
                else:
                    line += '@'
            sys.stdout.write(line + '\n')
        sys.stdout.flush()
        frame += 1
        time.sleep(0.05)
except KeyboardInterrupt:
    pass
finally:
    sys.stdout.write('\033[0m\033[?25h\n')
