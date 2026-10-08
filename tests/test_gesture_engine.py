from types import SimpleNamespace

from src.gesture_engine import detect_hand_gesture, face_reference


class Config:
    HEAD_GESTURE_DISTANCE = 0.35
    THUMB_OPEN_DISTANCE = 0.2
    KONO_FACE_RATIO = 0.8


def point(x, y):
    return SimpleNamespace(x=x, y=y)


def hand_with(index=True, middle=False, ring=False, pinky=False):
    hand = [point(0.5, 0.5) for _ in range(21)]
    # tip above PIP means extended; otherwise bent.
    for tip, pip, enabled in ((8, 6, index), (12, 10, middle),
                               (16, 14, ring), (20, 18, pinky)):
        hand[pip] = point(0.5, 0.5)
        hand[tip] = point(0.5, 0.3 if enabled else 0.7)
    hand[4] = point(0.2, 0.5)
    return hand


def test_open_palm():
    face = [point(0.5, 0.5) for _ in range(153)]
    nose, height = face_reference(face)
    assert detect_hand_gesture(hand_with(True, True, True, True), nose, height, Config) == "WRYYY"


def test_fist():
    face = [point(0.5, 0.5) for _ in range(153)]
    nose, height = face_reference(face)
    assert detect_hand_gesture(hand_with(False, False, False, False), nose, height, Config) == "MUDA"
