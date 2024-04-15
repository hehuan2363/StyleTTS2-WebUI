import torch
from TTS.api import TTS

text = ''' fully integrated professional services and project management company with offices around the world, today introduced the latest reactor design—the CANDU MONARK reactor'''
# Get device
device = "cuda" if torch.cuda.is_available() else "cpu"

# List available 🐸TTS models
print(TTS().list_models())

# Init TTS
# Init TTS with the target model name
tts = TTS(model_name="tts_models/de/thorsten/tacotron2-DDC", progress_bar=False)
OUTPUT_PATH = "output2.wav"
tts.tts_to_file(text=text, file_path=OUTPUT_PATH)
