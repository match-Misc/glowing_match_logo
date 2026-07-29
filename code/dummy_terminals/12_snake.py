import time
import random
import shutil
import sys

width = shutil.get_terminal_size((60, 20)).columns
height = 20
head_x, head_y = width // 2, height // 2
snake = [(head_x, head_y) for _ in range(5)]
food = None
direction = (1, 0)
score = 0

sys.stdout.write('\033[2J\033[?25l')
try:
    while True:
        # Place food
        if food is None or random.random() < 0.02:
            while True:
                fx = random.randint(0, width - 1)
                fy = random.randint(0, height - 1)
                if (fx, fy) not in snake:
                    food = (fx, fy)
                    break

        # Auto-change direction randomly
        if random.random() < 0.08:
            options = [(1, 0), (-1, 0), (0, 1), (0, -1)]
            options = [o for o in options if o != (-direction[0], -direction[1])]
            direction = random.choice(options)

        # Move snake
        head_x, head_y = snake[0]
        new_head = ((head_x + direction[0]) % width, (head_y + direction[1]) % height)
        snake.insert(0, new_head)
        if new_head == food:
            score += 1
            food = None
        else:
            snake.pop()

        # Draw
        lines = [' ' * width for _ in range(height)]
        # Food
        if food:
            fx, fy = food
            line = lines[fy]
            lines[fy] = line[:fx] + '*' + line[fx + 1:]
        # Snake
        for i, (sx, sy) in enumerate(snake):
            if 0 <= sy < height and 0 <= sx < width:
                ch = '@' if i == 0 else 'o'
                line = lines[sy]
                lines[sy] = line[:sx] + ch + line[sx + 1:]

        sys.stdout.write('\033[H')
        sys.stdout.write('Score: ' + str(score) + '\n')
        for line in lines:
            sys.stdout.write(line + '\n')
        sys.stdout.flush()
        time.sleep(0.1)
except KeyboardInterrupt:
    pass
finally:
    sys.stdout.write('\033[0m\033[?25h\n')
