import math
import time
import shutil
import sys

width = shutil.get_terminal_size((80, 20)).columns
height = 20
text = "HELLO WORLD!  "
msg = "Welcome to the terminal  "

sys.stdout.write('\033[2J\033[?25l')
frame = 0
try:
    while True:
        lines = []
        for row in range(height):
            line = ''
            for x in range(width):
                ch_idx = (x + row + frame) % len(text)
                ch = text[ch_idx]
                phase = (x * 0.3) + (row * 0.2) + (frame * 0.1)
                wave = math.sin(phase) * 2
                if abs(row - height / 2 - wave) < 0.6:
                    line += ch
                else:
                    line += ' '
            lines.append(line)
        sys.stdout.write('\033[H')
        sys.stdout.write(' ' * width + '\n')
        for line in lines:
            sys.stdout.write(line + '\n')
        scroll_x = (frame * 2) % (width + len(msg))
        sub = ' ' * width
        if 0 <= scroll_x <= width:
            end = min(width, scroll_x + len(msg))
            start_disp = max(0, scroll_x)
            msg_start = max(0, -scroll_x)
            sub = (' ' * start_disp + msg[msg_start:msg_start + (end - start_disp)]).ljust(width)[:width]
        sys.stdout.write('\033[96m' + sub + '\033[0m\n')
        sys.stdout.flush()
        frame += 1
        time.sleep(0.06)
except KeyboardInterrupt:
    pass
finally:
    sys.stdout.write('\033[0m\033[?25h\n')
