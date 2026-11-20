# ⚡ PixelLink

### Lightweight OLED Communication over Bluetooth Low Energy

A lightweight BLE-based communication system built with **ESP32 + MicroPython**, designed to transfer text and OLED framebuffer data wirelessly.

PixelLink provides a simple way to communicate with an SSD1306 OLED display through Bluetooth Low Energy, with adaptive framebuffer compression to reduce data transmission size.

<p align="center">
  <img src="https://img.shields.io/badge/Platform-ESP32-blue?style=for-the-badge&logo=espressif" />
  <img src="https://img.shields.io/badge/Language-MicroPython-yellow?style=for-the-badge&logo=python" />
  <img src="https://img.shields.io/badge/Protocol-BLE-0082FC?style=for-the-badge&logo=bluetooth" />
  <img src="https://img.shields.io/badge/Display-SSD1306-black?style=for-the-badge" />
</p>

---

## ✨ Features

- 🔵 **Bluetooth Low Energy:** Wireless communication using BLE GATT services.
- 📝 **Text Transmission:** Send text messages directly to the OLED display.
- 🖥️ **Framebuffer Reading:** Access the raw OLED framebuffer.
- 📦 **Adaptive Compression:** Automatically selects the smallest representation between RAW and RLE.
- ⚡ **Lightweight:** Designed for resource-constrained ESP32 devices.
- 🔄 **Asynchronous Architecture:** Uses `asyncio` and `aioble` for concurrent BLE operations.

## 🧠 How It Works

PixelLink uses a custom BLE GATT service with dedicated characteristics for reading OLED data and writing text.

```text
           Client Device
          (Android / Python)
                 |
                 | Bluetooth LE
                 |
        +--------------------+
        |     ESP32 Board    |
        |                    |
        |    PixelLink       |
        |                    |
        |  +--------------+  |
        |  |  BLE GATT    |  |
        |  +--------------+  |
        |         |          |
        |  +--------------+  |
        |  | SSD1306 OLED |  |
        |  +--------------+  |
        +--------------------+
```

## 📡 BLE Architecture

PixelLink uses a custom UUID structure:

| Component | UUID |
|---|---|
| Service | `7b100000-8a2f-4d91-b6c3-5e8f2a1d0001` |
| OLED Read | `7b100000-8a2f-4d91-b6c3-5e8f2a1d0002` |

The OLED framebuffer characteristic provides access to the display's raw pixel data.

The text characteristic accepts incoming text and renders it on the OLED display.

## 📦 Adaptive Compression

One of PixelLink's key features is its adaptive framebuffer compression system.

Instead of always using a compression algorithm, PixelLink compares the compressed and original data sizes and automatically selects the smaller one.

### Supported Modes

| Mode | Header | Description |
|---|---|---|
| RAW | `0x00` | Original framebuffer data |
| RLE | `0x01` | Run-Length Encoded framebuffer |

### RLE Example

Original data:

```text
00 00 00 00 00 FF FF FF 01 01
```

Compressed data:

```text
05 00 03 FF 02 01
```

Each pair represents:

```text
[COUNT] [VALUE]
```

This approach is particularly useful for monochrome displays containing large areas of identical pixel values.

### Adaptive Selection

```python
compressed = compress_rle(raw)

if len(compressed) < len(raw):
    return bytes([1]) + compressed
else:
    return bytes([0]) + raw
```

The first byte identifies the selected encoding mode.

## 🛠️ Hardware Requirements

- ESP32 development board
- SSD1306 OLED display (128 × 64)
- Jumper wires

### OLED Wiring

| OLED | ESP32 |
|---|---|
| VCC | 3.3V |
| GND | GND |
| SCL | GPIO 22 |
| SDA | GPIO 21 |

## 📚 Dependencies

Install or include the following MicroPython modules:

- `aioble`
- `bluetooth`
- `asyncio`
- `ssd1306`

## 🚀 Getting Started

1. Flash MicroPython firmware onto your ESP32.
2. Connect the SSD1306 OLED display using the wiring table.
3. Install the required libraries.
4. Upload the project script to your ESP32.
5. Run the script.

```bash
mpremote connect auto run main.py
```

6. Open a BLE client such as nRF Connect.
7. Connect to the device named `ESP32`.
8. Discover the PixelLink GATT service and interact with its characteristics.

## 🔧 Technical Details

| Property | Value |
|---|---|
| MCU | ESP32 |
| Display | SSD1306 |
| Resolution | 128 × 64 |
| Framebuffer Size | 1024 bytes |
| Communication | Bluetooth Low Energy |
| BLE Library | aioble |
| Runtime | MicroPython |
| Concurrency | asyncio |
| Compression | Adaptive RAW / RLE |

## 🗺️ Roadmap

- [x] BLE GATT service implementation
- [x] OLED text transmission
- [x] OLED framebuffer reading
- [x] RLE compression
- [x] Adaptive RAW/RLE selection
- [ ] Android client implementation
- [ ] Framebuffer decompression on Android
- [ ] Full-screen image transmission
- [ ] Animation streaming
- [ ] Multiple display support
- [ ] Transfer performance optimization

## 🤝 Contributing

Contributions, ideas, bug reports, and improvements are welcome!

Feel free to fork the repository and submit a pull request.

## 📄 License

This project is open-source. Add your preferred license to the repository.

---

<p align="center">
  **PixelLink** — Every pixel has a connection. ⚡
</p>
