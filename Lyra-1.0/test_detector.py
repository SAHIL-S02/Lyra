from app.wakeword.detector import WakeWordDetector


detector = WakeWordDetector()

print("================================")
print("       LYRA WAKE WORD")
print("================================")
print("Listening for: Hey Lyra")
print("Press Ctrl+C to stop\n")

try:
    while True:
        detector.listen()
        print("\n🔥 HEY LYRA DETECTED")
        print("Waiting for next activation...\n")

except KeyboardInterrupt:
    print("\nStopped.")