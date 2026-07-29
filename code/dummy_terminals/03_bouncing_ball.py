import time
import shutil
import sys

width = shutil.get_terminal_size((60, 20)).columns
height = 20

# Ball position and velocity
x, y = width // 2, height // 2
vx, vy = 1.2, 0.9
gravity = 0.25
bounce = -0.85
trail = []

sys.stdout.write('\033[2J')
try:
    while True:
        lines = [' ' * width for _ in range(height)]
        # Draw trail
        for i, (tx, ty) in enumerate(trail):
            if 0 <= ty < height and 0 <= tx < width:
                ch = '.' if i < len(trail) - 2 else 'o'
                line = lines[ty]
                lines[ty] = line[:tx] + ch + line[tx + 1:]
        # Draw ball
        bx, by = int(x), int(y)
        if 0 <= by < height and 0 <= bx < width:
            line = lines[by]
            lines[by] = line[:bx] + 'O' + line[bx + 1:]

        sys.stdout.write('\033[H')
        for line in lines:
            sys.stdout.write(line + '\n')
        sys.stdout.flush()

        # Physics
        vy += gravity
        x += vx
        y += vy
        if y >= height - 1:
            y = height - 1
            vy *= bounce
        if x >= width - 1:
            x = width - 1
            vx = -abs(vx)
        elif x <= 0:
            x = 0
            vx = abs(vx)

        trail.append((int(x), int(y)))
        if len(trail) > 6:
            trail.pop(0)
        time.sleep(0.05)
except KeyboardInterrupt:
    pass
finally:
    sys.stdout.write('\033[0m\n')
