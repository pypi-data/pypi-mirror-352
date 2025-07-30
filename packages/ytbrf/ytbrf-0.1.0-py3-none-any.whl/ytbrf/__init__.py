# ytbrf package initialization

import os
import sys
import argparse
from ytbrf.config import ConfigManager
from ytbrf.youtube import YouTubeProcessor
from rich.console import Console
from rich.progress import Progress

__version__ = '0.1.0'


def main():
    console = Console()

    parser = argparse.ArgumentParser(description="YouTube Brief: Summarize and translate YouTube videos or audio files.")
    parser.add_argument("url", nargs="?", help="YouTube URL")
    parser.add_argument("-a", "--audio", help="Path to local audio file for direct summarization.")
    args = parser.parse_args()

    config_manager = ConfigManager()
    config = config_manager._load_config()
    processor = YouTubeProcessor(config)

    temp_output_file_wo_ext = "output"
    if args.audio:
        audio_path = args.audio
        print(f"[INFO] Summarizing directly from audio file: {audio_path}")
        transcript, language = processor.transcribe_audio(audio_path)
        transcript_file_name = f"{os.path.splitext(os.path.basename(audio_path))[0]}-{language}.txt"
        with open(transcript_file_name, "w") as f:
            f.write(transcript)
        print(f"[INFO] Transcription complete. Transcript saved to {transcript_file_name}")
        metadata_title = os.path.splitext(os.path.basename(audio_path))[0]
    elif args.url:
        url = args.url
        print("[INFO] Starting video processing...")
        metadata = processor.get_video_metadata(url)
        print("[INFO] Video metadata retrieved.")

        if not metadata.get('has_transcript'):
            print("[INFO] Downloading audio and transcribing...")
            audio_path, _ = processor.download_audio(url, temp_output_file_wo_ext)
            print("[INFO] Audio downloaded to: ", audio_path)
            
            transcript, language = processor.transcribe_audio(audio_path)
            transcript_file_name = f"{metadata['title']}-{language}.txt"
            with open(transcript_file_name, "w") as f:
                f.write(transcript)
            print("[INFO] Transcription complete.")
        else:
            transcript = processor.get_transcript(metadata['id'])
            if transcript:
                console.print("[green]Successfully got transcript![/green]")
                transcript_file_name = f"{metadata['title']}.txt"
                with open(transcript_file_name, "w") as f:
                    f.write(transcript)
                console.print(f"[green]Transcript saved to {transcript_file_name}[/green]")
            else:
                console.print("[red]Failed to get transcript![/red]")
                sys.exit(1)
            language = metadata.get('language', 'en')
        # remove temporary output.mp3 if it exists
        for fmt in ['mp3', 'wav']:
            tmp_file_path = f"{temp_output_file_wo_ext}.{fmt}"
            if os.path.exists(tmp_file_path):
                console.print(f"Removing temp file {tmp_file_path}")
                os.remove(tmp_file_path)
        metadata_title = metadata['title']
    else:
        print("Usage: ytbrf <YouTube URL> or ytbrf -a <audio file>")
        sys.exit(1)

    print("[INFO] Summarizing transcript...")
    summary = processor.summarize(transcript)
    print("[INFO] Summarization complete.")
    with open(f"{metadata_title}-summary", "w") as f:
        f.write(transcript)

    target_language = config.summary.target_language
    print(f"[INFO] Translating transcript to {target_language}...")
    translated_text = processor.translate(summary, src_lang=language, tgt_lang=target_language)
    print("[INFO] Translation complete.")

    translated_file_name = f"{metadata_title}-summary-{target_language}.txt"
    with open(translated_file_name, "w") as f:
        f.write(translated_text)
    print(f"[INFO] Translated text saved to {translated_file_name}")
    
