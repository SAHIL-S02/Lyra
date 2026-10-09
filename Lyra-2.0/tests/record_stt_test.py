import sounddevice as sd
from scipy.io.wavfile import write

SAMPLE_RATE = 16000
DURATION = 5
DEVICE = 2

print("Using:", sd.query_devices(DEVICE)["name"])
print("Speak now for 5 seconds...")

audio = sd.rec(
    int(DURATION * SAMPLE_RATE),
    samplerate=SAMPLE_RATE,
    channels=1,
    dtype="int16",
    device=DEVICE,
)
sd.wait()

write("data/stt_test.wav", SAMPLE_RATE, audio)

print("Saved: data/stt_test.wav")
