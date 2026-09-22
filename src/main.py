import cv2
import mediapipe as mp
import pygame
import time
import os
import math
import sys


# =========================================================
# DIO ENGINE v2
# =========================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(BASE_DIR)

if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

import config

ASSETS_DIR = os.path.join(PROJECT_DIR, "assets")
MODELS_DIR = os.path.join(ASSETS_DIR, "models")
SOUNDS_DIR = os.path.join(ASSETS_DIR, "sounds")

FACE_MODEL = os.path.join(MODELS_DIR, "face_landmarker.task")
HAND_MODEL = os.path.join(MODELS_DIR, "hand_landmarker.task")

SOUNDS = {
    "ROAD_ROLLER": os.path.join(SOUNDS_DIR, "roadroller.wav"),
    "HIGH": os.path.join(SOUNDS_DIR, "high.mp3"),
    "WRYYY": os.path.join(SOUNDS_DIR, "wryy.wav"),
    "MUDA": os.path.join(SOUNDS_DIR, "muda.mp3"),
    "ZA_WARUDO": os.path.join(SOUNDS_DIR, "za_warudo.mp3"),
    "KONO_DIO_DA": os.path.join(SOUNDS_DIR, "kono_dio_da.mp3")
}

print()
print("Checking files...")

if not os.path.exists(FACE_MODEL):
    print("Missing:", FACE_MODEL)
    raise SystemExit

if not os.path.exists(HAND_MODEL):
    print("Missing:", HAND_MODEL)
    raise SystemExit

for name, filename in SOUNDS.items():
    if not os.path.exists(filename):
        print("Missing sound:", filename)
        raise SystemExit

print("All files OK!")

# =========================================================
# AUDIO
# =========================================================

AUDIO_AVAILABLE = False

try:
    pygame.mixer.init()
    AUDIO_AVAILABLE = True
except pygame.error as e:
    print("Audio unavailable:", e)
    print("DIO ENGINE will continue without sound.")

last_sound_time = 0
COOLDOWN = config.COOLDOWN


def play_sound(name):
    global last_sound_time

    if not AUDIO_AVAILABLE:
        return

    now = time.time()

    if now - last_sound_time < COOLDOWN:
        return

    try:
        pygame.mixer.music.stop()
        pygame.mixer.music.load(SOUNDS[name])
        pygame.mixer.music.play()
        last_sound_time = now
        print(">>>", name)
    except pygame.error as e:
        print("Audio error:", e)


# =========================================================
# MEDIAPIPE
# =========================================================

print("Loading MediaPipe...")

BaseOptions = mp.tasks.BaseOptions
VisionRunningMode = mp.tasks.vision.RunningMode
FaceLandmarker = mp.tasks.vision.FaceLandmarker
FaceLandmarkerOptions = mp.tasks.vision.FaceLandmarkerOptions
HandLandmarker = mp.tasks.vision.HandLandmarker
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions

face_options = FaceLandmarkerOptions(
    base_options=BaseOptions(model_asset_path=FACE_MODEL),
    running_mode=VisionRunningMode.IMAGE,
    num_faces=1,
    min_face_detection_confidence=0.5,
    min_face_presence_confidence=0.5,
    min_tracking_confidence=0.5
)

face_landmarker = FaceLandmarker.create_from_options(face_options)

hand_options = HandLandmarkerOptions(
    base_options=BaseOptions(model_asset_path=HAND_MODEL),
    running_mode=VisionRunningMode.IMAGE,
    num_hands=2,
    min_hand_detection_confidence=0.5,
    min_hand_presence_confidence=0.5,
    min_tracking_confidence=0.5
)

hand_landmarker = HandLandmarker.create_from_options(hand_options)

print("MediaPipe ready!")

# =========================================================
# CAMERA
# =========================================================

camera = cv2.VideoCapture(config.CAMERA_INDEX)

if not camera.isOpened():
    print("Camera error!")
    face_landmarker.close()
    hand_landmarker.close()
    pygame.quit()
    raise SystemExit

# Reduce capture resolution for weak PCs.
camera.set(cv2.CAP_PROP_FRAME_WIDTH, config.FRAME_WIDTH)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, config.FRAME_HEIGHT)

print()
print("==============================")
print("       DIO ENGINE v2")
print("==============================")
print()
print("Mouth open       = ROAD ROLLER")
print("Finger near head = HIGH")
print("Open palm        = WRYYY")
print("Fist             = MUDA MUDA")
print("Pointing         = ZA WARUDO")
print("Point + thumb    = KONO DIO DA")
print()
print("Press Q or Esc to quit.")
print()

previous_gesture = "NONE"


def distance(a, b):
    return math.hypot(a.x - b.x, a.y - b.y)


def finger_extended(hand, tip, pip):
    return hand[tip].y < hand[pip].y


def get_fingers(hand):
    return (
        finger_extended(hand, 8, 6),
        finger_extended(hand, 12, 10),
        finger_extended(hand, 16, 14),
        finger_extended(hand, 20, 18)
    )


def face_reference(face):
    # Nose/face center and face height give us a position and scale
    # that move with the user's actual head instead of the camera frame.
    nose = face[1]
    forehead = face[10]
    chin = face[152]
    face_height = max(distance(forehead, chin), 0.001)
    return nose, face_height


def detect_hand_gesture(hand, face_reference_point, face_height):
    index, middle, ring, pinky = get_fingers(hand)

    index_tip = hand[8]
    thumb_tip = hand[4]
    wrist = hand[0]

    # HIGH follows the detected face instead of a fixed screen coordinate.
    head_distance = distance(index_tip, face_reference_point)
    high_threshold = config.HEAD_GESTURE_DISTANCE * face_height

    if index and head_distance < high_threshold:
        return "HIGH"

    thumb_dist = distance(thumb_tip, wrist)

    # Pointing / KONO DIO DA
    if index and not middle and not ring and not pinky:
        thumb_open = thumb_dist > config.THUMB_OPEN_DISTANCE

        if thumb_open:
            thumb_to_face = distance(thumb_tip, face_reference_point)
            index_to_face = max(distance(index_tip, face_reference_point), 0.001)

            if thumb_to_face < index_to_face * config.KONO_FACE_RATIO:
                return "KONO_DIO_DA"

        return "ZA_WARUDO"

    if index and middle and ring and pinky:
        return "WRYYY"

    if not index and not middle and not ring and not pinky:
        return "MUDA"

    return "NONE"


# =========================================================
# MAIN LOOP
# =========================================================

while True:
    success, frame = camera.read()

    if not success:
        break

    frame = cv2.flip(frame, 1)
    height, width, _ = frame.shape

    # Keep processing light on weak PCs.
    if config.PROCESS_SCALE < 1.0:
        small_width = max(1, int(width * config.PROCESS_SCALE))
        small_height = max(1, int(height * config.PROCESS_SCALE))
        processing_frame = cv2.resize(
            frame,
            (small_width, small_height),
            interpolation=cv2.INTER_AREA
        )
    else:
        processing_frame = frame

    rgb = cv2.cvtColor(processing_frame, cv2.COLOR_BGR2RGB)

    mp_image = mp.Image(
        image_format=mp.ImageFormat.SRGB,
        data=rgb
    )

    # =====================================================
    # FACE
    # =====================================================

    face_result = face_landmarker.detect(mp_image)

    mouth_open = False
    face_ref = None
    face_height = 0.0

    if face_result.face_landmarks:
        face = face_result.face_landmarks[0]
        face_ref, face_height = face_reference(face)

        upper_lip = face[13]
        lower_lip = face[14]

        mouth_distance = abs(lower_lip.y - upper_lip.y)

        # Normalize mouth opening by face size.
        normalized_mouth = mouth_distance / face_height
        mouth_open = normalized_mouth > config.MOUTH_SENSITIVITY

        ux = int(upper_lip.x * width)
        uy = int(upper_lip.y * height)
        lx = int(lower_lip.x * width)
        ly = int(lower_lip.y * height)

        cv2.circle(frame, (ux, uy), 4, (255, 255, 255), -1)
        cv2.circle(frame, (lx, ly), 4, (255, 255, 255), -1)

    # =====================================================
    # HAND
    # =====================================================

    hand_result = hand_landmarker.detect(mp_image)
    detected_gesture = "NONE"

    if hand_result.hand_landmarks:
        candidates = []

        for hand in hand_result.hand_landmarks:
            # Draw only the key landmarks to reduce rendering work.
            for index in (0, 4, 8, 12, 16, 20):
                point = hand[index]
                x = int(point.x * width)
                y = int(point.y * height)
                cv2.circle(frame, (x, y), 3, (255, 255, 255), -1)

            if face_ref is not None:
                gesture = detect_hand_gesture(hand, face_ref, face_height)
            else:
                gesture = "NONE"

            if gesture != "NONE":
                candidates.append(gesture)

        # Explicit priority prevents the second detected hand from
        # accidentally overwriting a stronger gesture.
        priority = {
            "HIGH": 5,
            "KONO_DIO_DA": 4,
            "ZA_WARUDO": 3,
            "WRYYY": 2,
            "MUDA": 1
        }

        if candidates:
            detected_gesture = max(
                candidates,
                key=lambda gesture: priority[gesture]
            )

    # Mouth has highest priority.
    if mouth_open:
        detected_gesture = "ROAD_ROLLER"

    # =====================================================
    # TRIGGER
    # =====================================================

    if detected_gesture != previous_gesture:
        if detected_gesture != "NONE":
            play_sound(detected_gesture)

        previous_gesture = detected_gesture

    # =====================================================
    # UI
    # =====================================================

    display_text = {
        "ROAD_ROLLER": "ROAD ROLLER!",
        "HIGH": "SAIKO NI HIGH!",
        "WRYYY": "WRYYYYY!",
        "MUDA": "MUDA MUDA MUDA!",
        "ZA_WARUDO": "ZA WARUDO!",
        "KONO_DIO_DA": "KONO DIO DA!"
    }.get(detected_gesture, "DIO ENGINE")

    cv2.putText(
        frame,
        display_text,
        (20, 50),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.9,
        (255, 255, 255),
        3
    )

    cv2.putText(
        frame,
        "Gesture: " + detected_gesture,
        (20, 90),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.65,
        (255, 255, 255),
        2
    )

    cv2.imshow("DIO ENGINE v2", frame)

    key = cv2.waitKey(1) & 0xFF

    if key in (ord("q"), 27):
        print("DIO ENGINE: stopping...")
        break

camera.release()
cv2.destroyAllWindows()
face_landmarker.close()
hand_landmarker.close()

if AUDIO_AVAILABLE:
    pygame.mixer.music.stop()

pygame.quit()

print("DIO ENGINE OFF")
