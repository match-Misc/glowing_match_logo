import random
import time
import shutil
import sys

# Classic Matrix rain with bright white head + green trail
width = shutil.get_terminal_size((100, 30)).columns
height = 30
# Mix of katakana, latin, digits and symbols - the authentic Matrix look
charset = (
    "ｱｲｳｴｵｶｷｸｹｺｻｼｽｾｿﾀﾁﾂﾃﾄﾅﾆﾇﾈﾉﾊﾋﾌﾍﾎﾏﾐﾑﾒﾓﾔﾕﾖﾗﾘﾙﾚﾛﾜﾝ"
    "日月火水木金土山川田中本字学生先"
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    "0123456789"
    "<>{}[]|/\\!@#$%^&*"
)

# Each column has a "head" position that moves down at its own speed
columns = []
for _ in range(width):
    columns.append({
        'y': random.randint(-height, 0),
        'speed': random.uniform(0.3, 1.2),
        'length': random.randint(5, 20),
        'chars': [random.choice(charset) for _ in range(50)],
        'last_change': 0
    })

sys.stdout.write('\033[2J\033[?25l')
frame = 0
try:
    while True:
        # Build the frame buffer: each cell stores (char, brightness) 0-255
        # Brightness fades from white(255) at the head to dark green(30) at the tail
        grid = [[None for _ in range(width)] for _ in range(height)]

        for x, col in enumerate(columns):
            head_y = int(col['y'])
            speed = col['speed']
            length = col['length']

            # Occasionally change a character mid-stream for the "morph" effect
            if frame - col['last_change'] > 4:
                idx = random.randint(0, length - 1)
                col['chars'][idx] = random.choice(charset)
                col['last_change'] = frame

            for i in range(length):
                y = head_y - i
                if 0 <= y < height:
                    if i == 0:
                        # Bright white head
                        grid[y][x] = (col['chars'][i], 255)
                    else:
                        # Trail fading to dark green
                        brightness = max(30, 220 - i * (180 // max(1, length)))
                        grid[y][x] = (col['chars'][i], brightness)

            col['y'] += speed
            if col['y'] - length > height:
                col['y'] = random.randint(-10, 0)
                col['speed'] = random.uniform(0.3, 1.2)
                col['length'] = random.randint(5, 20)
                col['chars'] = [random.choice(charset) for _ in range(50)]

        # Render
        sys.stdout.write('\033[H')
        for row in grid:
            line = ''
            for cell in row:
                if cell is None:
                    line += ' '
                else:
                    ch, b = cell
                    if b >= 240:
                        # Bright white head
                        line += '\033[97m' + ch + '\033[0m'
                    elif b >= 180:
                        # Bright green
                        line += '\033[92m' + ch + '\033[0m'
                    elif b >= 120:
                        # Medium green
                        line += '\033[32m' + ch + '\033[0m'
                    elif b >= 60:
                        # Dark green
                        line += '\033[32;2m' + ch + '\033[0m'
                    else:
                        line += ch
            sys.stdout.write(line + '\n')
        sys.stdout.flush()
        frame += 1
        time.sleep(0.04)
except KeyboardInterrupt:
    pass
finally:
    sys.stdout.write('\033[0m\033[?25h\n')
