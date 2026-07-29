import random
import time
import shutil
import sys

width = shutil.get_terminal_size((80, 24)).columns
height = 24
chars = " .:-=+*#%@"

sys.stdout.write('\033[2J\033[?25l')
try:
    grid = [[0 for _ in range(width)] for _ in range(height)]
    while True:
        # Set bottom row randomly (fuel)
        for x in range(width):
            grid[height - 1][x] = random.randint(150, 255)
        # Propagate fire upward
        for y in range(height - 2, -1, -1):
            for x in range(width):
                decay = random.randint(0, 3)
                below = grid[y + 1][x]
                left = grid[y + 1][(x + 1) % width]
                right = grid[y + 1][(x - 1) % width]
                avg = (below * 2 + left + right) // 4
                grid[y][x] = max(0, avg - decay)

        sys.stdout.write('\033[H')
        for row in grid:
            line = ''
            for v in row:
                idx = min(len(chars) - 1, v * len(chars) // 256)
                if v > 200:
                    line += '\033[93m' + chars[idx] + '\033[0m'
                elif v > 100:
                    line += '\033[91m' + chars[idx] + '\033[0m'
                elif v > 30:
                    line += '\033[31m' + chars[idx] + '\033[0m'
                else:
                    line += ' '
            sys.stdout.write(line + '\n')
        sys.stdout.flush()
        time.sleep(0.05)
except KeyboardInterrupt:
    pass
finally:
    sys.stdout.write('\033[0m\033[?25h\n')
