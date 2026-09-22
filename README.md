# DioMotion

Camera-based motion tracking that turns your movements into DIO-inspired actions and sound effects.

## Features

- Real-time camera input with OpenCV
- Face landmark detection with MediaPipe
- Two-hand landmark detection with MediaPipe
- Gesture-based DIO actions
- Sound effects triggered by detected gestures
- Continues running if the audio device is unavailable
- Configurable camera, cooldown, and gesture sensitivity
- Local model and sound assets included in the repository

## Gesture controls

| Gesture | Action |
|---|---|
| Mouth open | ROAD ROLLER |
| Finger near head | SAIKO NI HIGH |
| Open palm | WRYYYY |
| Fist | MUDA MUDA |
| Pointing gesture | ZA WARUDO |
| Point + thumb gesture | KONO DIO DA |

Press **Q** or **Esc** to quit.

## Project structure

```text
DioMotion/
├── README.md
├── LICENSE
├── .gitignore
├── requirements.txt
├── config.py
├── src/
│   └── main.py
└── assets/
    ├── models/
    │   ├── face_landmarker.task
    │   └── hand_landmarker.task
    └── sounds/
        ├── high.mp3
        ├── kono_dio_da.mp3
        ├── muda.mp3
        ├── roadroller.wav
        ├── wryy.wav
        └── za_warudo.mp3
```

## Setup

Python 3.10+ is recommended.

Install the dependencies:

```bash
pip install -r requirements.txt
```

Run:

```bash
python src/main.py
```

Make sure your camera is available before starting the program.

## Configuration

Edit `config.py` to change:

- Camera index
- Gesture cooldown
- Mouth sensitivity
- Hand/gesture thresholds

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE).

## Disclaimer

DioMotion is a fan-made project inspired by *JoJo's Bizarre Adventure*. It is not affiliated with or endorsed by the rights holders.
