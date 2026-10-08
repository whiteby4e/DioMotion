"""Pure gesture detection helpers for DIO Motion."""
import math


def distance(a, b):
    return math.hypot(a.x - b.x, a.y - b.y)


def finger_extended(hand, tip, pip):
    return hand[tip].y < hand[pip].y


def get_fingers(hand):
    return (
        finger_extended(hand, 8, 6),
        finger_extended(hand, 12, 10),
        finger_extended(hand, 16, 14),
        finger_extended(hand, 20, 18),
    )


def face_reference(face):
    """Return a face anchor and scale factor independent of camera size."""
    nose = face[1]
    forehead = face[10]
    chin = face[152]
    face_height = max(distance(forehead, chin), 0.001)
    return nose, face_height


def detect_hand_gesture(hand, face_reference_point, face_height, config):
    index, middle, ring, pinky = get_fingers(hand)
    index_tip = hand[8]
    thumb_tip = hand[4]
    wrist = hand[0]

    head_distance = distance(index_tip, face_reference_point)
    high_threshold = config.HEAD_GESTURE_DISTANCE * face_height
    if index and head_distance < high_threshold:
        return "HIGH"

    thumb_dist = distance(thumb_tip, wrist)
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
