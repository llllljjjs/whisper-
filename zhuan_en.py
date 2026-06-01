
# python zhuan__en.py

import os
import sys
import re
import argparse
import traceback

# Default local model path / 默认模型路径
DEFAULT_MODEL_DIR = r"C:\whisper"


def get_available_filename(base_path: str) -> str:
    """If the file exists, automatically generate a non-repeating filename (name(1).txt)"""
    if not os.path.exists(base_path):
        return base_path
    dirname, basename = os.path.split(base_path)
    name, ext = os.path.splitext(basename)
    i = 1
    while True:
        new_name = f"{name}({i}){ext}"
        new_path = os.path.join(dirname, new_name)
        if not os.path.exists(new_path):
            return new_path
        i += 1


def clean_english_filler(text: str) -> str:
    """Clean up common English filler words and stutters"""
    # Remove standalone filler words with punctuation boundaries
    filler_pattern = r'\b(uh|um|ah|eh|erm|y’know|you know|like|oh)\b[,\s]*'
    text = re.sub(filler_pattern, ' ', text, flags=re.IGNORECASE)
    # Clean up multiple spaces
    text = re.sub(r'[ \t]{2,}', ' ', text)
    return text.strip()


def split_sentences_en(text: str) -> list:
    """
    Split English text into sentences.
    """
    if not text.strip():
        return []
    # Split by sentence-ending punctuation followed by whitespace
    delimiter_pattern = r'(?<=[.!?])\s+'
    sentences = re.split(delimiter_pattern, text)
    sentences = [s.strip() for s in sentences if s.strip()]
    return sentences


def normalize_sentence_en(s: str) -> str:
    """Normalize sentence for duplicate comparison (lowercase and strip punctuation)"""
    s = s.strip().lower()
    s = re.sub(r'[.!?]+$', '', s)
    return s


def remove_consecutive_duplicates(sentences: list) -> list:
    """Remove consecutive duplicate sentences (keeps the first one)"""
    if not sentences:
        return sentences
    cleaned = [sentences[0]]
    last_norm = normalize_sentence_en(sentences[0])
    for i in range(1, len(sentences)):
        curr_norm = normalize_sentence_en(sentences[i])
        if curr_norm != last_norm:
            cleaned.append(sentences[i])
            last_norm = curr_norm
    return cleaned


def transcribe_file(
        input_path: str,
        model_dir: str,
        device: str = "cuda",
        compute_type: str = "float16",
        beam_size: int = 5,
        out_dir: str = None,
        verbose: bool = False,
        remove_filler: bool = False,
):
    try:
        from faster_whisper import WhisperModel
        from tqdm import tqdm
    except Exception as e:
        raise RuntimeError(
            "Cannot import faster_whisper or tqdm. Please run: pip install faster-whisper tqdm"
        ) from e

    print(f"🚀 Loading model: {model_dir} (device={device}, compute_type={compute_type}) ...", flush=True)
    try:
        model = WhisperModel(model_dir, device=device, compute_type=compute_type)
    except Exception as e:
        print("❌ Model loading failed. (Please check model_dir, CUDA drivers, and VRAM).")
        raise

    print(f"🎙️ Starting transcription: {input_path}", flush=True)

    # ========== Core anti-repetition configuration for English ==========
    transcribe_kwargs = {
        "beam_size": beam_size,
        "language": "en",                       # 🔥 Force English Language
        "vad_filter": True,                     # Filter silence to reduce hallucinations
        "condition_on_previous_text": False,    # Prevent repetition loops
    }

    try:
        transcribe_kwargs["repetition_penalty"] = 1.2  # Slightly bumped for English
        transcribe_kwargs["no_repeat_ngram_size"] = 4
        transcribe_kwargs["temperature"] = 0.0
        segments, info = model.transcribe(input_path, **transcribe_kwargs)
    except TypeError:
        # Fallback for older faster-whisper versions
        transcribe_kwargs.pop("repetition_penalty", None)
        transcribe_kwargs.pop("no_repeat_ngram_size", None)
        transcribe_kwargs.pop("temperature", None)
        segments, info = model.transcribe(input_path, **transcribe_kwargs)
    except Exception:
        # Extreme fallback holding the core anti-repetition flag
        segments, info = model.transcribe(
            input_path,
            beam_size=beam_size,
            language="en",
            condition_on_previous_text=False
        )
    # ================================================================

    total_duration = round(info.duration, 2)
    pbar = tqdm(total=total_duration, unit="s", desc="Progress",
                bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]')
    last_pos = 0
    raw_texts = []

    for seg in segments:
        delta = seg.end - last_pos
        if delta > 0:
            pbar.update(delta)
        last_pos = seg.end
        t = getattr(seg, "text", None)
        if t is None:
            t = str(seg)
        t = t.strip()
        if t:
            raw_texts.append(t)
        if verbose:
            preview = t.replace("\n", " ")
            if len(preview) > 60:
                preview = preview[:60] + "..."
            pbar.write(f"[Segment] {preview}")
    pbar.close()

    full_text = " ".join(raw_texts).strip()

    # Clean filler words if requested
    if remove_filler:
        full_text = clean_english_filler(full_text)

    # Split into sentences and remove duplicates
    sentences = split_sentences_en(full_text)
    original_len = len(sentences)
    sentences = remove_consecutive_duplicates(sentences)
    removed = original_len - len(sentences)
    if removed > 0:
        print(f"🧹 Post-processing: Removed {removed} consecutive duplicate sentences.", flush=True)

    # Format output text with line breaks per sentence for readability
    output_text = "\n".join(sentences)
    output_text = re.sub(r'\n\s*\n+', '\n', output_text).strip()
    if output_text and not output_text.endswith('\n'):
        output_text += '\n'

    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
        base_name = os.path.splitext(os.path.basename(input_path))[0] + ".txt"
        out_file_candidate = os.path.join(out_dir, base_name)
    else:
        out_file_candidate = os.path.splitext(input_path)[0] + ".txt"

    out_file = get_available_filename(out_file_candidate)
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(output_text)

    try:
        lang = getattr(info, "language", None)
        prob = getattr(info, "language_probability", None)
        if lang:
            print(f"🌍 Detected Language: {lang} (Probability: {prob:.2f})", flush=True)
    except Exception:
        pass

    print(f"✅ Completed! Saved to: {os.path.abspath(out_file)}", flush=True)
    return os.path.abspath(out_file)


def main():
    parser = argparse.ArgumentParser \
        (description="English Transcription based on faster-whisper (Anti-Repetition Edition)")
    parser.add_argument("input", help="Path to the audio/video file")
    parser.add_argument("--model-dir", default=DEFAULT_MODEL_DIR, help="Path to the model directory")
    parser.add_argument("--device", default="cuda", choices=["cuda", "cpu"], help="Device to use")
    parser.add_argument("--compute-type", default="float16", help="Compute type (e.g., float16, int8)")
    parser.add_argument("--beam-size", type=int, default=5, help="Beam size")
    parser.add_argument("--out-dir", default=None, help="Output directory")
    parser.add_argument("--verbose", action="store_true", help="Print segment previews during transcription")
    parser.add_argument("--remove-filler", action="store_true", help="Remove common English filler words (uh, um, like...)")
    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"❌ Cannot find file: {args.input}")
        sys.exit(1)

    try:
        transcribe_file(
            args.input,
            model_dir=args.model_dir,
            device=args.device,
            compute_type=args.compute_type,
            beam_size=args.beam_size,
            out_dir=args.out_dir,
            verbose=args.verbose,
            remove_filler=args.remove_filler,
        )
    except Exception:
        print("❌ Exception occurred during transcription:")
        traceback.print_exc()
        sys.exit(1)

    print("🎉 Task Finished.")


if __name__ == "__main__":
    main()