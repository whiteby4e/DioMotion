"""DioMotion configuration."""

CAMERA_INDEX = 0

# Audio
COOLDOWN = 1.5

# Gesture sensitivity
# Mouth threshold is normalized by detected face height.
MOUTH_SENSITIVITY = 0.035

# HIGH threshold is a fraction of face height.
HEAD_GESTURE_DISTANCE = 0.45

# Thumb distance from wrist, in normalized image coordinates.
THUMB_OPEN_DISTANCE = 0.18

# KONO DIO DA thumb-to-face ratio.
KONO_FACE_RATIO = 0.85

# Performance
# Lower values reduce MediaPipe workload on weak PCs.
FRAME_WIDTH = 640
FRAME_HEIGHT = 480
PROCESS_SCALE = 0.75
