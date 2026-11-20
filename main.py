import aioble
import asyncio
import bluetooth
import ssd1306
from machine import Pin, I2C

SERVICE_UUID = bluetooth.UUID("7b100000-8a2f-4d91-b6c3-5e8f2a1d0001")
READ_OLED_UUID = bluetooth.UUID("7b100000-8a2f-4d91-b6c3-5e8f2a1d0002")
WRITE_TEXT_OLED_UUID = bluetooth.UUID("7b100000-8a2f-4d91-b6c3-5e8f2a1d0002")

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


async def handle_write(connection, data):
    global oled

    oled.fill(0)
    try:
        oled.text(data.decode(), 0, 0)
    except:
        oled.text("hello", 0, 0)
    print("Received:", data)
    oled.show()

    await asyncio.sleep_ms(0)


async def write_handler():
    while True:

        connection = await WRITE_TEXT_CHARACTERISTIC.written()

        if not connection.is_connected():
            continue

        try:
            await handle_write(connection, WRITE_TEXT_CHARACTERISTIC.read())

        except Exception as e:
            print("Write Error:", e)


async def init():
    global oled
    oled.fill(1)
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
    tasks = [
        asyncio.create_task(RunBle()), asyncio.create_task(init()), asyncio.create_task(write_handler())
    ]

    await asyncio.gather(*tasks)


asyncio.run(RunMultiply())
