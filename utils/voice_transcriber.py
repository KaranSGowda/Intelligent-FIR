import whisper
import os

class VoiceTranscriber:
    def __init__(self, model_name='base'):
        self.model = whisper.load_model(model_name)

    def transcribe(self, audio_path, language=None):
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        result = self.model.transcribe(audio_path, language=language)
        return result['text']

# Example usage:
# transcriber = VoiceTranscriber(model_name='small')
# text = transcriber.transcribe('path/to/audio.wav', language='en')
# print(text)
