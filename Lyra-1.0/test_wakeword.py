import time
import numpy as np
import sounddevice as sd
from openwakeword.model import Model

SAMPLE_RATE = 16000
BLOCK_SIZE = 1280  # 80 ms

model = Model(
    wakeword_models=["models/wakeword/hey_lyra.onnx"],
    inference_framework="onnx",
)

print("=" * 50)
print("        LYRA WAKE WORD TEST")
print("=" * 50)
print("Say: Hey Lyra")
print("Press Ctrl+C to stop")
print()

last_detection = 0.0


def callback(indata, frames, time_info, status):
    global last_detection

    if status:
        print("Audio status:", status)

    # Mono float32 -> int16 PCM
    audio = (indata[:, 0] * 32767).astype(np.int16)

    predictions = model.predict(audio)

    score = predictions.get("hey_lyra", 0.0)

    print(f"\rScore: {score:.3f}", end="", flush=True)

    if score >= 0.5:
        now = time.time()

        # Prevent repeated detections from one utterance
        if now - last_detection > 1.0:
            print(f"\n🔥 HEY LYRA DETECTED! score={score:.3f}")
            last_detection = now


try:
    with sd.InputStream(
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype="float32",
        blocksize=BLOCK_SIZE,
        callback=callback,
    ):
        while True:
            time.sleep(0.1)

except KeyboardInterrupt:
    print("\n\nTest stopped.")