import time
import shutil
import sys

width = shutil.get_terminal_size((80, 20)).columns
msg = "Hello World"
i = 0
sys.stdout.write('\033[2J')
try:
    while True:
        i = (i + 1) % (width)
        bar = '#' * i + '.' * max(0, (width - i - len(msg) - 4))
        percent = int((i / max(1, (width - len(msg) - 4))) * 100)
        line = "\r[ " + bar + " ] " + str(percent).rjust(3) + "%  " + msg
        sys.stdout.write(line)
        sys.stdout.flush()
        time.sleep(0.04)
except KeyboardInterrupt:
    pass
finally:
    sys.stdout.write('\n')
