<div align="center">

# DioMotion

**Your gestures. DIO-inspired reactions.**

A camera-based computer-vision project that maps face and hand gestures to dramatic actions and sound effects.

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![OpenCV](https://img.shields.io/badge/Vision-OpenCV%20%2B%20MediaPipe-blue)
![License](https://img.shields.io/badge/License-MIT-green)

</div>

---

## 🎬 What it does

DioMotion reads live camera frames, detects face and hand landmarks, and triggers a matching action when a configured gesture is recognized. Audio playback is optional at runtime: the application can continue if an audio device is unavailable.

## ✨ Gesture controls

| Detected gesture | Action |
|---|---|
| Mouth open | ROAD ROLLER |
| Finger near head | SAIKO NI HIGH |
| Open palm | WRYYYY |
| Fist | MUDA MUDA |
| Pointing gesture | ZA WARUDO |
| Point + thumb gesture | KONO DIO DA |

Press **Q** or **Esc** to quit.

## ⚡ Quick start

### Requirements

- Python 3.10 or newer is recommended.
- A working webcam.
- Windows, Linux, or macOS with compatible OpenCV, MediaPipe, and Pygame wheels.

### Install and run

```bash
git clone https://github.com/whiteby4e/DioMotion.git
cd DioMotion

python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux / macOS
source .venv/bin/activate

python -m pip install -r requirements.txt
python src/main.py
```

Allow camera access if your operating system asks for permission.

## ⚙️ Configuration

Edit `config.py` to adjust:

| Setting | Purpose |
|---|---|
| `CAMERA_INDEX` | Camera device index |
| `COOLDOWN` | Delay between repeated actions |
| `MOUTH_SENSITIVITY` | Mouth-open detection threshold |
| `HEAD_GESTURE_DISTANCE` | Face-relative gesture distance |
| `THUMB_OPEN_DISTANCE` | Thumb gesture threshold |
| `KONO_FACE_RATIO` | Point-and-thumb gesture threshold |
| `FRAME_WIDTH`, `FRAME_HEIGHT` | Camera capture dimensions |
| `PROCESS_SCALE` | Frame scale used for processing |

If a gesture is not recognized reliably, adjust one setting at a time and test again.

## 🧩 How it is organized

```text
DioMotion/
├── config.py
├── requirements.txt
├── src/
│   ├── main.py
│   └── gesture_engine.py
├── tests/
│   └── test_gesture_engine.py
└── assets/
    ├── models/
    └── sounds/
```

The MediaPipe task models and sound assets are included under `assets/`.

## 🧪 Tests

```bash
python -m unittest discover -s tests
```

## ⚠️ Note

DioMotion is a fan-made project inspired by *JoJo's Bizarre Adventure*. It is not affiliated with or endorsed by the rights holders. Use the camera only with the knowledge and permission of people being recorded.

## 📄 License

The repository source code is released under the MIT License. See [LICENSE](LICENSE). Check third-party asset terms before redistributing bundled models or media.
