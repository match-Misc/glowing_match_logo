import math
import time
import shutil
import sys
from datetime import datetime

width = shutil.get_terminal_size((60, 24)).columns
height = 24
R = min(width // 2 - 2, height // 2 - 2) - 1
cx, cy = width // 2, height // 2

sys.stdout.write('\033[2J\033[?25l')
try:
    while True:
        lines = [' ' * width for _ in range(height)]
        # Draw clock circle
        for a in range(0, 360, 3):
            ang = a * math.pi / 180
            x = int(cx + R * math.cos(ang))
            y = int(cy + R * math.sin(ang) * 0.5)
            if 0 <= x < width and 0 <= y < height:
                line = lines[y]
                lines[y] = line[:x] + ('.' if a % 30 else 'o') + line[x + 1:]

        now = datetime.now()
        h = (now.hour % 12) + now.minute / 60.0
        m = now.minute + now.second / 60.0
        s = now.second

        for label, val, ch in [(h, h / 12, 'H'), (m, m / 60, 'M'), (s, s / 60, 'S')]:
            ang = val * 2 * math.pi - math.pi / 2
            for r_frac in [1, 0.75, 0.5, 0.25]:
                x = int(cx + R * r_frac * math.cos(ang))
                y = int(cy + R * r_frac * math.sin(ang) * 0.5)
                if 0 <= x < width and 0 <= y < height:
                    line = lines[y]
                    lines[y] = line[:x] + ch + line[x + 1:]

        # Center dot
        line = lines[cy]
        lines[cy] = line[:cx] + '+' + line[cx + 1:]

        sys.stdout.write('\033[H')
        for line in lines:
            sys.stdout.write(line + '\n')
        sys.stdout.flush()
        time.sleep(0.1)
except KeyboardInterrupt:
    pass
finally:
    sys.stdout.write('\033[0m\033[?25h\n')
