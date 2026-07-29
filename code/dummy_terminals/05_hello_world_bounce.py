import time
import shutil
import sys

width = shutil.get_terminal_size((80, 20)).columns
height = 20
text = " HELLO WORLD! "
dx, dy = 1, 0
x, y = 2, height // 2
sys.stdout.write('\033[2J')
try:
    while True:
        lines = [' ' * width for _ in range(height)]
        if 0 <= y < height:
            line = lines[y]
            if 0 <= x <= width - len(text):
                lines[y] = line[:x] + text + line[x + len(text):]

        sys.stdout.write('\033[H')
        for ln in lines:
            sys.stdout.write(ln + '\n')
        sys.stdout.flush()

        # Bouncing physics with gravity on the text
        dy += 0.25
        x += dx
        y = int(y + dy)
        if y >= height - 1:
            y = height - 1
            dy = -abs(dy) * 0.7
            if abs(dy) < 0.6:
                dy = -3.5  # jump
        if x <= 0 or x + len(text) >= width:
            dx = -dx
            x = max(0, min(width - len(text), x))

        time.sleep(0.05)
except KeyboardInterrupt:
    pass
finally:
    sys.stdout.write('\033[0m\n')
