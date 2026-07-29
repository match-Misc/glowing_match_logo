import math
import time
import shutil
import sys

width = shutil.get_terminal_size((80, 24)).columns
height = 24
R1 = 1
R2 = 2
K2 = 5
K1 = width * K2 * 3 / (8 * (R1 + R2))

sys.stdout.write('\033[2J\033[?25l')
A = 0
B = 0
try:
    while True:
        output = [[' ' for _ in range(width)] for _ in range(height)]
        zbuffer = [[0 for _ in range(width)] for _ in range(height)]
        cosA, sinA = math.cos(A), math.sin(A)
        cosB, sinB = math.cos(B), math.sin(B)
        for i in range(int(2 * math.pi / 0.07)):
            theta = i * 0.07
            for j in range(int(2 * math.pi / 0.04)):
                phi = j * 0.04
                cosphi = math.cos(phi)
                sinphi = math.sin(phi)
                costheta = math.cos(theta)
                sintheta = math.sin(theta)
                circlex = R2 + R1 * costheta
                circley = R1 * sintheta
                x = circlex * (cosB * cosphi + sinA * sinB * sinphi) - circley * cosA * sinB
                y = circlex * (sinB * cosphi - sinA * cosB * sinphi) + circley * cosA * cosB
                z = K2 + cosA * circlex * sinphi + circley * sinA
                ooz = 1 / z
                xp = int(width / 2 + K1 * ooz * x)
                yp = int(height / 2 - K1 * ooz * y)
                L = cosphi * costheta * sinB - cosA * costheta * sinphi - sintheta * cosB
                if 0 <= xp < width and 0 <= yp < height:
                    if ooz > zbuffer[yp][xp]:
                        zbuffer[yp][xp] = ooz
                        luminance_index = int(L * 8)
                        chars = ".,-~:;=!*#$@"
                        output[yp][xp] = chars[max(0, min(len(chars) - 1, luminance_index))]

        sys.stdout.write('\033[H')
        for line in output:
            sys.stdout.write(''.join(line) + '\n')
        sys.stdout.flush()
        A += 0.07
        B += 0.04
        time.sleep(0.05)
except KeyboardInterrupt:
    pass
finally:
    sys.stdout.write('\033[0m\033[?25h\n')
