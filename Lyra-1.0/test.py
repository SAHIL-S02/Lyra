from openwakeword.model import Model

model = Model(
    wakeword_models=["models/wakeword/hey_lyra.onnx"],
    inference_framework="onnx",
)

print("Model loaded successfully!")
print("Models:", model.models)