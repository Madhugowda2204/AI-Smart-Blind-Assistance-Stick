import cv2
import pytesseract
import pyttsx3
import os

# Optional: set Tesseract executable path manually
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def speak_text(text):
    try:
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print("🛑 Speech error:", e)

def preprocess_image(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    thresh = cv2.adaptiveThreshold(
        blur, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        11, 2
    )
    return thresh

def read_text_from_frame(frame):
    processed = preprocess_image(frame)
    custom_config = r'--oem 3 --psm 6'
    try:
        text = pytesseract.image_to_string(processed, config=custom_config, lang='eng')
        return text.strip()
    except Exception as e:
        print("🛑 OCR error:", e)
        return ""

def main():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("🛑 Error: Cannot open webcam.")
        return

    print("✅ Webcam started. Press 'r' to read text or 'q' to quit.")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("❌ Failed to capture frame.")
            break

        cv2.imshow("AI Smart Stick - Text Reader", frame)
        key = cv2.waitKey(1)

        if key == ord('r'):
            print("🔍 Reading text from frame...")
            text = read_text_from_frame(frame)
            if text:
                print("📄 Detected Text:\n", text)
                speak_text(text)
            else:
                print("⚠️ No readable text detected.")
        elif key == ord('q'):
            print("👋 Quitting...")
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
