import random
import time
import shutil
import sys

width = shutil.get_terminal_size((80, 20)).columns
height = 20
charset = "01ABCDEFGHIGKLMNOPQRSTUVWXYZ"
columns = [random.randint(-height, 0) for _ in range(width)]
sys.stdout.write('\033[2J\033[?25l')
try:
    while True:
        lines = ['' for _ in range(height)]
        for x in range(width):
            y = columns[x]
            if 0 <= y < height:
                lines[y] += '\033[92m' + random.choice(charset) + '\033[0m'
            else:
                lines[0] += ' '
            columns[x] += 1
            if columns[x] > height + 5:
                columns[x] = random.randint(-height, 0)
        sys.stdout.write('\033[H')
        for line in lines:
            sys.stdout.write(line.ljust(width)[:width] + '\n')
        sys.stdout.flush()
        time.sleep(0.06)
except KeyboardInterrupt:
    pass
finally:
    sys.stdout.write('\033[0m\033[?25h\n')
