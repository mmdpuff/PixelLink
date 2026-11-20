import aioble
import asyncio
import bluetooth
import ssd1306
from machine import Pin, I2C

SERVICE_UUID = bluetooth.UUID("7b100000-8a2f-4d91-b6c3-5e8f2a1d0001")
READ_OLED_UUID = bluetooth.UUID("7b100000-8a2f-4d91-b6c3-5e8f2a1d0002")
WRITE_TEXT_OLED_UUID = bluetooth.UUID("7b100000-8a2f-4d91-b6c3-5e8f2a1d0003")

# ================= COMMANDS =================

ADD_TEXT = 0x01

# Vertical alignment
TOP = 0x00
CENTER_V = 0x01
BOTTOM = 0x02

# Horizontal alignment
LEFT = 0x00
CENTER_H = 0x01
RIGHT = 0x02

Service = aioble.Service(SERVICE_UUID)

READ_CHARACTERISTIC = aioble.Characteristic(Service, READ_OLED_UUID, read=True)
WRITE_TEXT_CHARACTERISTIC = aioble.Characteristic(Service, WRITE_TEXT_OLED_UUID, write=True)

aioble.register_services(Service)

i2c = I2C(
    0,
    scl=Pin(22),
    sda=Pin(21),
    freq=100000
)

oled = ssd1306.SSD1306_I2C(128, 64, i2c)
oled.contrast(100)


# دریافت ماتریس وضعیت OLED
def compress_rle(data):
    result = bytearray()

    i = 0

    while i < len(data):
        value = data[i]
        count = 1

        while (
                i + count < len(data)
                and data[i + count] == value
                and count < 255
        ):
            count += 1

        result.append(count)
        result.append(value)

        i += count

    return result


def compress_oled(oled):
    # Original OLED buffer
    raw = oled.buffer

    # RLE compression
    compressed = compress_rle(raw)

    # Select smallest
    if len(compressed) < len(raw):

        # Header 1 = RLE
        return bytes([1]) + compressed

    else:

        # Header 0 = RAW
        return bytes([0]) + raw


# data = compress_oled(oled)
READ_CHARACTERISTIC.write(compress_oled(oled))


async def draw_text(text, vertical, horizontal):
    oled.fill(0)
    text_width = len(text) * 8
    text_height = 8

    # Horizontal position
    if horizontal == LEFT:
        x = 0

    elif horizontal == CENTER_H:
        x = (128 - text_width) // 2

    elif horizontal == RIGHT:
        x = 128 - text_width

    else:
        return

    # Vertical position
    if vertical == TOP:
        y = 0

    elif vertical == CENTER_V:
        y = (64 - text_height) // 2

    elif vertical == BOTTOM:
        y = 64 - text_height

    else:
        return

    oled.text(text, x, y)
    oled.show()
    await asyncio.sleep_ms(0)


async def handle_packet(data):
    try:

        # Minimum header size = 4 bytes
        if len(data) < 4:
            print("Invalid packet")
            return

        command = data[0]
        vertical = data[1]
        horizontal = data[2]
        text_length = data[3]

        # Validate command
        if command != ADD_TEXT:
            print("Unknown command")
            return

        # Validate alignment
        if vertical not in (TOP, CENTER_V, BOTTOM):
            print("Invalid vertical alignment")
            return

        if horizontal not in (LEFT, CENTER_H, RIGHT):
            print("Invalid horizontal alignment")
            return

        # Validate packet length
        if len(data) != 4 + text_length:
            print("Invalid text length")
            return

        # Extract UTF-8 text
        text = data[4:].decode("utf-8")

        # Draw
        await draw_text(text, vertical, horizontal)

        print("Text:", text)
        print("Position:", vertical, horizontal)

    except Exception as e:
        print("Packet error:", e)


async def write_handler():
    while True:

        connection = await WRITE_TEXT_CHARACTERISTIC.written()

        if not connection.is_connected():
            continue

        try:

            await handle_packet(WRITE_TEXT_CHARACTERISTIC.read())

        except Exception as e:
            print("Write Error:", e)


async def init():
    oled.fill(0)
    oled.text("App Running", 0, 0)
    oled.show()


async def RunBle():
    print("starting ble...")
    while True:
        print("Advertiseing runing")
        async with await aioble.advertise(250_000, name="ESP32", services=[SERVICE_UUID]) as connection:
            print("connect seccesfully")

            await connection.disconnected()
            print("disconnect")


async def RunMultiply():
    await init()

    tasks = [
        asyncio.create_task(RunBle()),
        asyncio.create_task(write_handler())
    ]

    await asyncio.gather(*tasks)


asyncio.run(RunMultiply())
