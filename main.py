import cv2
import time
import os
import winsound
import threading
from eye_movement import process_eye_movement
from head_pose import process_head_pose
from mobile_detection import process_mobile_detection

# 🔔 Beep control
beep_running = False

def continuous_beep():
    global beep_running
    while beep_running:
        winsound.Beep(1000, 300)  # smooth continuous beep

# Initialize webcam
cap = cv2.VideoCapture(0)

# Create a log directory for screenshots
log_dir = "log"
os.makedirs(log_dir, exist_ok=True)

# Calibration for head pose
calibrated_angles = None
start_time = time.time()

# Timers for each functionality
head_misalignment_start_time = None
eye_misalignment_start_time = None
mobile_detection_start_time = None

# Initialize head_direction
head_direction = "Looking at Screen"

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # 👁️ Eye movement
    frame, gaze_direction = process_eye_movement(frame)
    cv2.putText(frame, f"Gaze: {gaze_direction}", (20, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    # 🧠 Head pose
    if time.time() - start_time <= 5:
        cv2.putText(frame, "Calibrating... Keep head straight", (50, 200),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
        if calibrated_angles is None:
            _, calibrated_angles = process_head_pose(frame, None)
    else:
        frame, head_direction = process_head_pose(frame, calibrated_angles)
        cv2.putText(frame, f"Head: {head_direction}", (20, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    # 📱 Mobile detection
    frame, mobile_detected = process_mobile_detection(frame)
    cv2.putText(frame, f"Mobile: {mobile_detected}", (20, 90),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    # 🔴 HEAD ALERT
    if head_direction != "Looking at Screen":
        if head_misalignment_start_time is None:
            head_misalignment_start_time = time.time()
        elif time.time() - head_misalignment_start_time >= 3:
            filename = os.path.join(log_dir, f"head_{int(time.time())}.png")
            cv2.imwrite(filename, frame)
            print(f"Head alert saved: {filename}")
            head_misalignment_start_time = None
    else:
        head_misalignment_start_time = None

    # 🔴 EYE ALERT
    if gaze_direction != "Looking at Screen":
        if eye_misalignment_start_time is None:
            eye_misalignment_start_time = time.time()
        elif time.time() - eye_misalignment_start_time >= 3:
            filename = os.path.join(log_dir, f"eye_{int(time.time())}.png")
            cv2.imwrite(filename, frame)
            print(f"Eye alert saved: {filename}")
            eye_misalignment_start_time = None
    else:
        eye_misalignment_start_time = None

    # 🚨 MOBILE ALERT + CONTINUOUS BEEP
    if mobile_detected:
        if mobile_detection_start_time is None:
            mobile_detection_start_time = time.time()

            # 🔔 Start continuous beep
            if not beep_running:
                beep_running = True
                threading.Thread(target=continuous_beep, daemon=True).start()

        elif time.time() - mobile_detection_start_time >= 3:
            filename = os.path.join(log_dir, f"mobile_{int(time.time())}.png")
            cv2.imwrite(filename, frame)
            print(f"Mobile alert saved: {filename}")
            mobile_detection_start_time = None
    else:
        mobile_detection_start_time = None

        # 🔕 Stop beep
        beep_running = False

    # Display output
    cv2.imshow("Cheating Detection System", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()