import random
import time
import shutil
import sys

width = shutil.get_terminal_size((80, 20)).columns
height = 20

drops = [random.randint(0, height) for _ in range(width)]
chars = ['|', ':', ';', '`', '.', ',']

sys.stdout.write('\033[2J')
try:
    while True:
        lines = [' ' * width for _ in range(height)]
        for x in range(width):
            y = drops[x]
            head = max(0, y)
            tail = max(0, y - 3)
            for row in range(tail, head + 1):
                if 0 <= row < height:
                    ch = '|' if row == head else random.choice(chars)
                    line = lines[row]
                    lines[row] = line[:x] + ch + line[x + 1:]
            drops[x] += 1
            if drops[x] > height + 5:
                drops[x] = random.randint(-3, 0)

        sys.stdout.write('\033[H')
        for line in lines:
            sys.stdout.write(line + '\n')
        sys.stdout.flush()
        time.sleep(0.08)
except KeyboardInterrupt:
    pass
finally:
    sys.stdout.write('\033[0m\n')
