#!/usr/bin/env python3
"""
Model Weight Fetcher for AvC (Audio Deepfake & Synthesis Detector)

Downloads the required AASIST-v2 ONNX model checkpoint from Hugging Face
and pre-caches the Wav2Vec2-base feature extractor.
"""

import os
import sys
import urllib.request
import shutil

HF_ONNX_URL = "https://huggingface.co/ayush2635/Dhwani-Multilingual-Deepfake-Audio-Detection-Model/resolve/main/best_model.onnx"
TARGET_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "ai")
TARGET_FILE = os.path.join(TARGET_DIR, "best_model.onnx")

def download_with_progress(url: str, output_path: str):
    print(f"Downloading model from: {url}")
    print(f"Destination: {output_path}")

    class DownloadProgressBar:
        def __init__(self):
            self.last_reported = -1

        def __call__(self, block_num, block_size, total_size):
            if total_size <= 0:
                return
            downloaded = block_num * block_size
            percent = int(downloaded * 100 / total_size)
            if percent != self.last_reported and percent % 5 == 0:
                mb_downloaded = downloaded / (1024 * 1024)
                mb_total = total_size / (1024 * 1024)
                print(f"Progress: {percent}% ({mb_downloaded:.1f} MB / {mb_total:.1f} MB)", end="\r")
                self.last_reported = percent

    urllib.request.urlretrieve(url, output_path, reporthook=DownloadProgressBar())
    print("\nDownload complete!")

def main():
    os.makedirs(TARGET_DIR, exist_ok=True)

    print("=" * 60)
    print("AvC Model & Asset Initializer")
    print("=" * 60)

    # 1. Check or download ONNX model
    if os.path.exists(TARGET_FILE):
        size_mb = os.path.getsize(TARGET_FILE) / (1024 * 1024)
        print(f"✓ ONNX model found at {TARGET_FILE} ({size_mb:.1f} MB)")
    else:
        print(f"ONNX model missing. Initiating download (~1.2 GB)...")
        try:
            download_with_progress(HF_ONNX_URL, TARGET_FILE)
        except Exception as e:
            print(f"\n[ERROR] Failed to download ONNX model: {e}")
            print("You can manually download the model from:")
            print(f"  {HF_ONNX_URL}")
            print(f"and place it at: {TARGET_FILE}")
            sys.exit(1)

    # 2. Cache Wav2Vec2 base model
    try:
        from transformers import Wav2Vec2Processor, Wav2Vec2Model
        print("\nChecking Wav2Vec2-base feature extractor...")
        Wav2Vec2Processor.from_pretrained("facebook/wav2vec2-base")
        Wav2Vec2Model.from_pretrained("facebook/wav2vec2-base")
        print("✓ Wav2Vec2-base cached locally.")
    except ImportError:
        print("Note: transformers library not installed in this environment; skipping Wav2Vec2 cache.")
    except Exception as e:
        print(f"Note: Could not pre-cache Wav2Vec2: {e}")

    print("\nAll weights and assets are ready.")

if __name__ == "__main__":
    main()
