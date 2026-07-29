import math
import time
import shutil
import sys

width = shutil.get_terminal_size((80, 20)).columns
height = 20
A = height // 3
omega = 0.35
k = 0.5

frame = 0
try:
    while True:
        cols = []
        for x in range(width):
            y = A * math.sin(omega * frame + k * x)
            row = int(height / 2 + y)
            row = max(0, min(height - 1, row))
            cols.append((x, row))

        output_lines = [' ' * width for _ in range(height)]
        for x, row in cols:
            line = output_lines[row]
            output_lines[row] = line[:x] + '~' + line[x + 1:]

        sys.stdout.write('\033[H')
        for line in output_lines:
            sys.stdout.write(line + '\n')
        sys.stdout.flush()
        frame += 1
        time.sleep(0.05)
except KeyboardInterrupt:
    pass
finally:
    sys.stdout.write('\033[?25h\n')
