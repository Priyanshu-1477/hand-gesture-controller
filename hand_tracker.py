import cv2
import mediapipe as mp
import pyautogui
import subprocess
import time

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils
hands = mp_hands.Hands(max_num_hands=1)

cap = cv2.VideoCapture(0)

triggered_gesture = None
last_action_time = 0
cooldown = 2  # seconds

# === Utility ===
def fingers_up(hand_landmarks):
    tips_ids = [4, 8, 12, 16, 20]
    fingers = []

    # Thumb
    fingers.append(1 if hand_landmarks.landmark[tips_ids[0]].x < hand_landmarks.landmark[tips_ids[0] - 1].x else 0)

    # Fingers: Index to Pinky
    for id in range(1, 5):
        fingers.append(1 if hand_landmarks.landmark[tips_ids[id]].y < hand_landmarks.landmark[tips_ids[id] - 2].y else 0)

    return fingers

# === Feedback Text ===
def draw_feedback(img, text):
    cv2.putText(img, text, (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1.4, (0, 255, 0), 3)

while True:
    success, img = cap.read()
    if not success:
        break

    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    result = hands.process(img_rgb)
    action_text = ""

    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            mp_draw.draw_landmarks(img, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            fingers = fingers_up(hand_landmarks)
            print("Fingers up:", fingers)

            current_time = time.time()
            if current_time - last_action_time < cooldown:
                continue  # Still cooling down

            # === BASE FOUR (Do Not Change) ===
            if fingers == [0, 0, 0, 0, 1] and triggered_gesture != "terminal":
                action_text = "🖥️ Open Terminal"
                pyautogui.hotkey('ctrl', 'alt', 't')
                triggered_gesture = "terminal"

            elif fingers == [1, 1, 1, 0, 0] and triggered_gesture != "mute":
                action_text = "🔇 Mute/Unmute"
                subprocess.run(["pactl", "set-sink-mute", "@DEFAULT_SINK@", "toggle"])
                triggered_gesture = "mute"

            elif fingers.count(1) > 4 and triggered_gesture != "lock":
                action_text = "🔒 Lock Screen"
                subprocess.run(["xdg-screensaver", "lock"])
                triggered_gesture = "lock"

            elif fingers.count(1) == 0:
                action_text = "♻️ Gesture Reset"
                triggered_gesture = None

            # === Other Cool Gestures ===
            elif fingers == [0, 1, 0, 0, 0]:
                action_text = "💻 Open VSCode"
                subprocess.run(["flatpak", "run", "com.visualstudio.code"])

            elif fingers == [0, 0, 0, 1, 0]:
                action_text = "⏯️ Play/Pause"
                pyautogui.press('playpause')

            elif fingers == [0, 0, 0, 0, 1]:
                action_text = "⏭️ Next Track"
                pyautogui.press('nexttrack')

            elif fingers == [0, 1, 1, 1, 1]:
                action_text = "🎤 Voice Typing"
                subprocess.Popen(["python3", "voice_typing.py"])

            elif fingers == [1, 1, 1, 1, 0]:
                action_text = "🧠 Workspace Apps"
                pyautogui.hotkey('super')

            elif fingers == [1, 0, 0, 0, 1]:
                action_text = "🔕 Toggle DND"
                pyautogui.hotkey('super', 'n')
                time.sleep(0.5)
                pyautogui.press('tab')
                pyautogui.press('tab')
                pyautogui.press('space')

            elif fingers == [1, 0, 1, 0, 0]:
                action_text = "🧭 Next Workspace"
                pyautogui.hotkey('ctrl', 'alt', 'right')

            elif fingers == [0, 1, 1, 0, 0]:
                action_text = "🔊 Volume Up"
                pyautogui.press('volumeup')

            elif fingers == [0, 0, 1, 1, 0]:
                action_text = "🔉 Volume Down"
                pyautogui.press('volumedown')

            elif fingers == [1, 0, 1, 1, 0]:
                action_text = "☀️ Brightness Up"
                pyautogui.hotkey('brightnessup')

            elif fingers == [1, 0, 0, 1, 0]:
                action_text = "🌙 Brightness Down"
                pyautogui.hotkey('brightnessdown')

            if action_text:
                print("Action:", action_text)
                last_action_time = time.time()  # Update cooldown
                draw_feedback(img, action_text)

    else:
        triggered_gesture = None  # No hand → reset state

    cv2.imshow("Gesture Control", img)
    if cv2.waitKey(1) & 0xFF == 27:  # ESC to quit
        break

cap.release()
cv2.destroyAllWindows()

