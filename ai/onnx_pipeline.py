import onnxruntime as ort
import numpy as np
import librosa
import os
import io
import base64
import matplotlib
matplotlib.use('Agg') # Headless backend
import matplotlib.pyplot as plt

class VoicePipeline:
    def __init__(self):
        # Load ONNX model (uses GPU if onnxruntime-gpu is installed, else CPU)
        model_path = os.path.join(os.path.dirname(__file__), "best_model.onnx")
        self.session = ort.InferenceSession(model_path)
        
    def process_chunk(self, audio_bytes: bytes) -> float:
        # ONNX expects exactly 48,000 samples (3 seconds at 16kHz)
        y = np.frombuffer(audio_bytes, dtype=np.float32)
        
        max_len = 48000
        if len(y) > max_len:
            y = y[:max_len]
        else:
            y = np.pad(y, (0, max_len - len(y)), mode='constant')
            
        y = (y - np.mean(y)) / np.sqrt(np.var(y) + 1e-5)
        y = y.astype(np.float32).reshape(1, max_len)
        
        input_name = self.session.get_inputs()[0].name
        logits = self.session.run(None, {input_name: y})[0]
        
        probs = np.exp(logits) / np.sum(np.exp(logits), axis=1, keepdims=True)
        return float(probs[0][1]) # Spoof probability

    def process_full_audio_file(self, file_bytes: bytes) -> tuple[float, str]:
        """
        Loads a universal audio format (e.g. .mp3, .wav), converts to mono, 
        resamples to 16kHz, slides a 3-second window, and returns the maximum risk 
        score found in the entire file along with its heatmap.
        """
        import soundfile as sf
        y, sr = librosa.load(io.BytesIO(file_bytes), sr=16000, mono=True)
        
        max_score = 0.0
        best_chunk = None
        
        # Slide across the file in 48000 sample (3s) chunks
        for i in range(0, len(y), 48000):
            chunk = y[i:i+48000]
            if len(chunk) < 16000: # Skip fragments less than 1 second at the end
                continue
                
            chunk_bytes = chunk.astype(np.float32).tobytes()
            score = self.process_chunk(chunk_bytes)
            
            if score > max_score or best_chunk is None:
                max_score = score
                best_chunk = chunk_bytes
                
        if best_chunk is None:
            # Fallback if audio is super short
            best_chunk = y.astype(np.float32).tobytes()
            max_score = self.process_chunk(best_chunk)
            
        heatmap = self.generate_spectrogram(best_chunk)
        return max_score, heatmap

    def generate_spectrogram(self, audio_bytes: bytes) -> str:
        """
        Generates a Mel-spectrogram from raw PCM bytes and returns it as a base64 string.
        Used for the Explainability Layer heatmap.
        """
        y = np.frombuffer(audio_bytes, dtype=np.float32)
        S = librosa.feature.melspectrogram(y=y, sr=16000, n_mels=128)
        S_dB = librosa.power_to_db(S, ref=np.max)
        
        plt.figure(figsize=(4, 2))
        librosa.display.specshow(S_dB, sr=16000, x_axis='time', y_axis='mel', cmap='magma')
        plt.axis('off')
        plt.tight_layout(pad=0)
        
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight', pad_inches=0)
        plt.close()
        buf.seek(0)
        
        return base64.b64encode(buf.read()).decode('utf-8')
