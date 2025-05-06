from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import ssd1306
from PIL import ImageFont
import time

# Initialize I2C interface
serial = i2c(port=1, address=0x3C)

# Initialize OLED display device
device = ssd1306(serial)

# Define font
font = ImageFont.truetype("tengxun.ttf", 13)

# Function to display text
def display_hello_world():
    with canvas(device) as draw:
        draw.rectangle(device.bounding_box, outline="white", fill="black")
        draw.text((15, 25), 'Hello World', fill="white", font=font)

if __name__ == '__main__':
    display_hello_world()
    time.sleep(5)  # Keep the message on screen for 5 seconds
