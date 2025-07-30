"""Configuration of default global parameters of the app"""

SAMPLING_RATE = 44100
TEMP_RESULTS_DIR = "data/temp_results"
PATH_TO_ONNX_MODEL = "models/segmentation-3.0.onnx"

# Real-time transcription defaults
RTT_URL = "wss://api.openai.com/v1/realtime?intent=transcription"
PING_INTERVAL = 5
PING_TIMEOUT = 20
SEND_INTERVAL = 0.01
FRAMES_PER_BUFFER = 3200
CHANNELS = 1
RATE = 16000
