import cv2
import mediapipe as mp
import pygame
import time
import os
import math


# =========================================================
# DIO ENGINE v2
# =========================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODELS_DIR = os.path.join(BASE_DIR, "models")
SOUNDS_DIR = os.path.join(BASE_DIR, "sounds")


FACE_MODEL = os.path.join(
    MODELS_DIR,
    "face_landmarker.task"
)

HAND_MODEL = os.path.join(
    MODELS_DIR,
    "hand_landmarker.task"
)


# =========================================================
# SOUNDS
# =========================================================

SOUNDS = {
    "ROAD_ROLLER": os.path.join(SOUNDS_DIR, "roadroller.wav"),
    "HIGH": os.path.join(SOUNDS_DIR, "high.mp3"),
    "WRYYY": os.path.join(SOUNDS_DIR, "wryy.wav"),
    "MUDA": os.path.join(SOUNDS_DIR, "muda.mp3"),
    "ZA_WARUDO": os.path.join(SOUNDS_DIR, "za_warudo.mp3"),
    "KONO_DIO_DA": os.path.join(SOUNDS_DIR, "kono_dio_da.mp3")
}

# =========================================================
# CHECK FILES
# =========================================================

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

        print()
        print("Missing sound:", filename)
        print()

        raise SystemExit


print("All files OK!")


# =========================================================
# AUDIO
# =========================================================

pygame.mixer.init()

last_sound_time = 0

COOLDOWN = 1.5


def play_sound(name):

    global last_sound_time

    now = time.time()

    if now - last_sound_time < COOLDOWN:
        return

    filename = SOUNDS[name]

    try:

        pygame.mixer.music.stop()

        pygame.mixer.music.load(filename)

        pygame.mixer.music.play()

        last_sound_time = now

        print(">>>", name)

    except Exception as e:

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


# =========================================================
# FACE
# =========================================================

face_options = FaceLandmarkerOptions(

    base_options=BaseOptions(
        model_asset_path=FACE_MODEL
    ),

    running_mode=VisionRunningMode.IMAGE,

    num_faces=1,

    min_face_detection_confidence=0.5,

    min_face_presence_confidence=0.5,

    min_tracking_confidence=0.5
)


face_landmarker = FaceLandmarker.create_from_options(
    face_options
)


# =========================================================
# HAND
# =========================================================

hand_options = HandLandmarkerOptions(

    base_options=BaseOptions(
        model_asset_path=HAND_MODEL
    ),

    running_mode=VisionRunningMode.IMAGE,

    num_hands=2,

    min_hand_detection_confidence=0.5,

    min_hand_presence_confidence=0.5,

    min_tracking_confidence=0.5
)


hand_landmarker = HandLandmarker.create_from_options(
    hand_options
)


print("MediaPipe ready!")


# =========================================================
# CAMERA
# =========================================================

camera = cv2.VideoCapture(0)

if not camera.isOpened():

    print("Camera error!")

    raise SystemExit


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
print("Press Q to quit.")
print()


# =========================================================
# STATES
# =========================================================

previous_gesture = "NONE"


# =========================================================
# DISTANCE
# =========================================================

def distance(a, b):

    return math.sqrt(

        (a.x - b.x) ** 2 +
        (a.y - b.y) ** 2

    )


# =========================================================
# FINGER STATES
# =========================================================

def finger_extended(hand, tip, pip):

    return hand[tip].y < hand[pip].y


def get_fingers(hand):

    index = finger_extended(hand, 8, 6)

    middle = finger_extended(hand, 12, 10)

    ring = finger_extended(hand, 16, 14)

    pinky = finger_extended(hand, 20, 18)

    return index, middle, ring, pinky


# =========================================================
# MAIN LOOP
# =========================================================

while True:

    success, frame = camera.read()

    if not success:
        break


    frame = cv2.flip(frame, 1)

    height, width, _ = frame.shape


    # =====================================================
    # RGB
    # =====================================================

    rgb = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2RGB
    )


    mp_image = mp.Image(
        image_format=mp.ImageFormat.SRGB,
        data=rgb
    )


    # =====================================================
    # FACE
    # =====================================================

    face_result = face_landmarker.detect(
        mp_image
    )


    mouth_open = False


    if face_result.face_landmarks:

        face = face_result.face_landmarks[0]

        upper_lip = face[13]
        lower_lip = face[14]

        mouth_distance = abs(
            lower_lip.y - upper_lip.y
        )

        if mouth_distance > 0.035:

            mouth_open = True


        # Draw mouth

        ux = int(upper_lip.x * width)
        uy = int(upper_lip.y * height)

        lx = int(lower_lip.x * width)
        ly = int(lower_lip.y * height)

        cv2.circle(
            frame,
            (ux, uy),
            4,
            (255, 255, 255),
            -1
        )

        cv2.circle(
            frame,
            (lx, ly),
            4,
            (255, 255, 255),
            -1
        )


    # =====================================================
    # HAND
    # =====================================================

    hand_result = hand_landmarker.detect(
        mp_image
    )


    detected_gesture = "NONE"


    if hand_result.hand_landmarks:

        for hand in hand_result.hand_landmarks:

            # ---------------------------------------------
            # Draw hand
            # ---------------------------------------------

            for point in hand:

                x = int(point.x * width)
                y = int(point.y * height)

                cv2.circle(
                    frame,
                    (x, y),
                    3,
                    (255, 255, 255),
                    -1
                )


            # ---------------------------------------------
            # Fingers
            # ---------------------------------------------

            index, middle, ring, pinky = get_fingers(hand)


            # ---------------------------------------------
            # Finger positions
            # ---------------------------------------------

            index_tip = hand[8]

            thumb_tip = hand[4]

            wrist = hand[0]


            # =================================================
            # 1. FINGER NEAR HEAD
            # =================================================

            head_x = 0.50
            head_y = 0.35


            head_distance = math.sqrt(

                (index_tip.x - head_x) ** 2 +

                (index_tip.y - head_y) ** 2

            )


            if index and head_distance < 0.18:

                detected_gesture = "HIGH"


           # =================================================
# GESTURE DETECTION
# =================================================

index, middle, ring, pinky = get_fingers(hand)

index_tip = hand[8]
thumb_tip = hand[4]
wrist = hand[0]

# فاصله انگشت‌ها از مچ
index_dist = distance(index_tip, wrist)
thumb_dist = distance(thumb_tip, wrist)

# =================================================
# 1. HIGH
# =================================================

if index and head_distance < 0.18:

    detected_gesture = "HIGH"


# =================================================
# 2. KONO DIO DA
# =================================================

elif (
    index
    and not middle
    and not ring
    and not pinky
):

    # شست باید واقعاً باز باشد
    thumb_open = thumb_dist > 0.18

    if thumb_open:

        # مرکز تقریبی صورت
        face_x = 0.50
        face_y = 0.40

        # فاصله شست تا صورت
        thumb_to_face = math.sqrt(
            (thumb_tip.x - face_x) ** 2 +
            (thumb_tip.y - face_y) ** 2
        )

        # فاصله نوک اشاره تا صورت
        index_to_face = math.sqrt(
            (index_tip.x - face_x) ** 2 +
            (index_tip.y - face_y) ** 2
        )

        # برای KONO، شست باید نسبتاً به خودت نزدیک‌تر باشد
        if thumb_to_face < index_to_face * 0.85:

            detected_gesture = "KONO_DIO_DA"

        else:

            detected_gesture = "ZA_WARUDO"

    else:

        detected_gesture = "ZA_WARUDO"


# =================================================
# 3. OPEN PALM
# =================================================

elif (
    index
    and middle
    and ring
    and pinky
):

    detected_gesture = "WRYYY"


# =================================================
# 4. FIST
# =================================================

elif (
    not index
    and not middle
    and not ring
    and not pinky
):

    detected_gesture = "MUDA"

    # =====================================================
    # MOUTH HAS HIGHEST PRIORITY
    # =====================================================

    if mouth_open:

        detected_gesture = "ROAD_ROLLER"


    # =====================================================
    # TRIGGER
    # =====================================================

    if detected_gesture != previous_gesture:

        if detected_gesture != "NONE":

            play_sound(
                detected_gesture
            )

        previous_gesture = detected_gesture


    # =====================================================
    # UI
    # =====================================================

    if detected_gesture == "ROAD_ROLLER":

        display_text = "ROAD ROLLER!"

    elif detected_gesture == "HIGH":

        display_text = "SAIKO NI HIGH!"

    elif detected_gesture == "WRYYY":

        display_text = "WRYYYYY!"

    elif detected_gesture == "MUDA":

        display_text = "MUDA MUDA MUDA!"

    elif detected_gesture == "ZA_WARUDO":

        display_text = "ZA WARUDO!"

    elif detected_gesture == "KONO_DIO_DA":

        display_text = "KONO DIO DA!"

    else:

        display_text = "DIO ENGINE"


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


    # =====================================================
    # DISPLAY
    # =====================================================

    cv2.imshow(
        "DIO ENGINE v2",
        frame
    )


    key = cv2.waitKey(1) & 0xFF


    if key == ord("q"):

        print("mi bombo")


# =========================================================
# CLEANUP
# =========================================================

camera.release()

cv2.destroyAllWindows()

face_landmarker.close()

hand_landmarker.close()

pygame.mixer.music.stop()

pygame.quit()

print("DIO ENGINE OFF")