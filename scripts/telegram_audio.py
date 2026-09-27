#!/usr/bin/env python3
"""Telegram Audio Converter — ogg/opus → wav/mp3 for Whisper compatibility.

Telegram sends voice notes as ogg/opus. Whisper (faster-whisper) needs
wav/mp3/m4a. This module handles conversion automatically.

Uses imageio-ffmpeg (bundled ffmpeg) for zero-system-dependency conversion.

Usage:
    from telegram_audio import convert_for_whisper
    wav_path = convert_for_whisper(ogg_bytes)  # returns path to wav file
"""
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Optional, Union
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_ffmpeg_path() -> str:
    """Get ffmpeg executable path (system or bundled via imageio-ffmpeg)."""
    # Try system ffmpeg first
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
        return "ffmpeg"
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    
    # Try imageio-ffmpeg (bundled)
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        pass
    
    raise RuntimeError(
        "ffmpeg not found. Install system ffmpeg (apt-get install ffmpeg) "
        "or python package: pip install imageio-ffmpeg"
    )


def check_ffmpeg() -> bool:
    """Check if ffmpeg is available (system or bundled)."""
    try:
        get_ffmpeg_path()
        return True
    except RuntimeError:
        return False


def check_faster_whisper() -> bool:
    """Check if faster-whisper is installed."""
    try:
        import faster_whisper
        return True
    except ImportError:
        return False


def convert_ogg_to_wav(input_path: Union[str, Path], 
                       output_path: Optional[Union[str, Path]] = None,
                       sample_rate: int = 16000) -> Path:
    """
    Convert ogg/opus to wav (16kHz mono) for Whisper.
    
    Args:
        input_path: Path to input ogg file
        output_path: Optional output path (auto-generated if None)
        sample_rate: Target sample rate (Whisper expects 16kHz)
    
    Returns:
        Path to converted wav file
    """
    input_path = Path(input_path)
    
    if output_path is None:
        output_path = input_path.with_suffix(".wav")
    else:
        output_path = Path(output_path)
    
    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Get ffmpeg path (system or bundled)
    ffmpeg = get_ffmpeg_path()
    
    # ffmpeg command: ogg/opus -> wav 16kHz mono
    cmd = [
        ffmpeg, "-y",  # overwrite
        "-i", str(input_path),
        "-ar", str(sample_rate),  # 16kHz
        "-ac", "1",  # mono
        "-c:a", "pcm_s16le",  # PCM 16-bit little-endian
        str(output_path)
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if result.returncode != 0:
            raise RuntimeError(f"ffmpeg failed: {result.stderr}")
        
        if not output_path.exists() or output_path.stat().st_size == 0:
            raise RuntimeError("Output file not created or empty")
        
        logger.info(f"Converted {input_path} -> {output_path} ({output_path.stat().st_size} bytes)")
        return output_path
        
    except subprocess.TimeoutExpired:
        raise RuntimeError("ffmpeg conversion timed out")
    except Exception as e:
        raise RuntimeError(f"Conversion failed: {e}")


def convert_for_whisper(audio_bytes: bytes, 
                        input_format: str = "ogg",
                        sample_rate: int = 16000) -> Path:
    """
    Convert audio bytes to wav file suitable for Whisper.
    
    Args:
        audio_bytes: Raw audio bytes (from Telegram)
        input_format: Input format (ogg, opus, m4a, etc.)
        sample_rate: Target sample rate
    
    Returns:
        Path to temporary wav file (caller must clean up)
    """
    # Write input to temp file
    with tempfile.NamedTemporaryFile(suffix=f".{input_format}", delete=False) as f:
        f.write(audio_bytes)
        input_path = Path(f.name)
    
    try:
        # Convert to wav
        output_path = input_path.with_suffix(".wav")
        convert_ogg_to_wav(input_path, output_path, sample_rate)
        return output_path
    finally:
        # Clean up input temp file
        try:
            input_path.unlink()
        except Exception:
            pass


def transcribe_telegram_voice(audio_bytes: bytes, 
                              model_size: str = "base",
                              language: Optional[str] = None) -> dict:
    """
    Complete pipeline: Telegram voice bytes -> text.
    
    Args:
        audio_bytes: Raw ogg/opus bytes from Telegram
        model_size: faster-whisper model (tiny, base, small, medium, large)
        language: Optional language code (auto-detect if None)
    
    Returns:
        Dict with 'text', 'language', 'segments', 'duration'
    """
    if not check_faster_whisper():
        raise RuntimeError("faster-whisper not installed. Run: pip install faster-whisper")
    
    if not check_ffmpeg():
        raise RuntimeError("ffmpeg not available. Install: apt-get install ffmpeg")
    
    from faster_whisper import WhisperModel
    
    # Convert audio
    wav_path = convert_for_whisper(audio_bytes)
    
    try:
        # Load model (cached after first load)
        model = WhisperModel(model_size, device="cpu", compute_type="int8")
        
        # Transcribe
        segments, info = model.transcribe(
            str(wav_path),
            language=language,
            beam_size=5,
            vad_filter=True,
            vad_parameters=dict(min_silence_duration_ms=500)
        )
        
        # Collect segments
        segment_list = []
        full_text = []
        for seg in segments:
            segment_list.append({
                "start": seg.start,
                "end": seg.end,
                "text": seg.text
            })
            full_text.append(seg.text)
        
        return {
            "text": " ".join(full_text).strip(),
            "language": info.language,
            "language_probability": info.language_probability,
            "duration": info.duration,
            "segments": segment_list
        }
        
    finally:
        # Clean up wav file
        try:
            wav_path.unlink()
        except Exception:
            pass


# Batch processing for multiple voice notes
def batch_transcribe(voice_files: list[Union[str, Path]], 
                     model_size: str = "base",
                     language: Optional[str] = None) -> list[dict]:
    """Transcribe multiple voice files efficiently (reuses model)."""
    if not check_faster_whisper():
        raise RuntimeError("faster-whisper not installed")
    
    if not check_ffmpeg():
        raise RuntimeError("ffmpeg not available")
    
    from faster_whisper import WhisperModel
    
    model = WhisperModel(model_size, device="cpu", compute_type="int8")
    results = []
    
    for voice_file in voice_files:
        voice_path = Path(voice_file)
        if voice_path.suffix.lower() in [".ogg", ".opus"]:
            wav_path = convert_ogg_to_wav(voice_path)
            try:
                segments, info = model.transcribe(
                    str(wav_path), language=language, beam_size=5,
                    vad_filter=True
                )
                text = " ".join(seg.text for seg in segments).strip()
                results.append({
                    "file": str(voice_path),
                    "text": text,
                    "language": info.language,
                    "duration": info.duration
                })
            finally:
                try:
                    wav_path.unlink()
                except Exception:
                    pass
        else:
            # Already compatible format
            segments, info = model.transcribe(
                str(voice_path), language=language, beam_size=5, vad_filter=True
            )
            text = " ".join(seg.text for seg in segments).strip()
            results.append({
                "file": str(voice_path),
                "text": text,
                "language": info.language,
                "duration": info.duration
            })
    
    return results


# n8n integration helper
def n8n_telegram_voice_to_text(telegram_file_id: str, 
                                bot_token: str,
                                model_size: str = "base") -> dict:
    """
    n8n-ready function: given Telegram file_id, download and transcribe.
    
    Use in n8n Code node or as sub-workflow tool.
    """
    import requests
    
    # Get file path from Telegram
    file_url = f"https://api.telegram.org/bot{bot_token}/getFile?file_id={telegram_file_id}"
    resp = requests.get(file_url, timeout=10)
    resp.raise_for_status()
    file_info = resp.json()
    
    if not file_info.get("ok"):
        raise RuntimeError(f"Telegram API error: {file_info}")
    
    file_path = file_info["result"]["file_path"]
    download_url = f"https://api.telegram.org/file/bot{bot_token}/{file_path}"
    
    # Download
    audio_resp = requests.get(download_url, timeout=30)
    audio_resp.raise_for_status()
    audio_bytes = audio_resp.content
    
    # Transcribe
    return transcribe_telegram_voice(audio_bytes, model_size=model_size)


# CLI
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python telegram_audio.py <input.ogg> [output.wav]")
        print("  python telegram_audio.py --transcribe <input.ogg> [model_size]")
        print("  python telegram_audio.py --check")
        sys.exit(1)
    
    if sys.argv[1] == "--check":
        print(f"ffmpeg: {'✓' if check_ffmpeg() else '✗'}")
        print(f"faster-whisper: {'✓' if check_faster_whisper() else '✗'}")
        sys.exit(0)
    
    if sys.argv[1] == "--transcribe":
        if len(sys.argv) < 3:
            print("Usage: --transcribe <input.ogg> [model_size]")
            sys.exit(1)
        input_file = sys.argv[2]
        model = sys.argv[3] if len(sys.argv) > 3 else "base"
        with open(input_file, "rb") as f:
            audio = f.read()
        result = transcribe_telegram_voice(audio, model_size=model)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        sys.exit(0)
    
    # Convert mode
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    try:
        out = convert_ogg_to_wav(input_file, output_file)
        print(f"✓ Converted: {out}")
    except Exception as e:
        print(f"✗ Failed: {e}")
        sys.exit(1)