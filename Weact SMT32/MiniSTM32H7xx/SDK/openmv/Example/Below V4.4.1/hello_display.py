# Hello World - Display Example
#
# Draws "Hello World" on the 0.96'' LCD (no camera needed).
#
# WeAct Studio STM32H7xx

import lcd, image, time

lcd.init(type=2)  # Initialize the lcd screen.

img = image.Image(160, 120, image.RGB565)

while(True):
    img.clear()
    img.draw_string(30, 55, "Hello World!", color=(255, 255, 255), scale=2)
    lcd.display(img)
    time.sleep_ms(100)
