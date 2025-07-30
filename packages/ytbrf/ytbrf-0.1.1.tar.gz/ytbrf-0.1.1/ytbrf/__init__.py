# ytbrf package initialization

import os
import sys
import argparse
from ytbrf.config import ConfigManager
from ytbrf.youtube import YouTubeProcessor
from rich.console import Console
from rich.progress import Progress
import yaml

__version__ = '0.1.0'


def process_audio_file(processor, audio_path, console):
    """Process a local audio file for transcription."""
    print(f"[INFO] Summarizing directly from audio file: {audio_path}")
    transcript, language = processor.transcribe_audio(audio_path)
    transcript_file_name = f"{os.path.splitext(os.path.basename(audio_path))[0]}-{language}.txt"
    with open(transcript_file_name, "w") as f:
        f.write(transcript)
    print(f"[INFO] Transcription complete. Transcript saved to {transcript_file_name}")
    metadata_title = os.path.splitext(os.path.basename(audio_path))[0]
    return transcript, language, metadata_title


def process_youtube_url(processor, url, temp_output_file_wo_ext, console):
    """Process a YouTube URL to get transcript."""
    print("[INFO] Starting video processing...")
    metadata = processor.get_video_metadata(url)
    print("[INFO] Video metadata retrieved.")
    
    if not metadata.get('has_transcript'):
        transcript, language = download_and_transcribe(processor, url, temp_output_file_wo_ext, metadata)
    else:
        transcript, language = get_existing_transcript(processor, metadata, console)
    
    # Remove temporary files
    cleanup_temp_files(temp_output_file_wo_ext, console)
    
    return transcript, language, metadata['title']


def download_and_transcribe(processor, url, temp_output_file_wo_ext, metadata):
    """Download audio from YouTube and transcribe it."""
    print("[INFO] Downloading audio and transcribing...")
    audio_path, _ = processor.download_audio(url, temp_output_file_wo_ext)
    print("[INFO] Audio downloaded to: ", audio_path)
    
    transcript, language = processor.transcribe_audio(audio_path)
    transcript_file_name = f"{metadata['title']}-{language}.txt"
    with open(transcript_file_name, "w") as f:
        f.write(transcript)
    print("[INFO] Transcription complete.")
    return transcript, language


def get_existing_transcript(processor, metadata, console):
    """Get existing transcript from YouTube."""
    transcript = processor.get_transcript(metadata['id'])
    if transcript:
        console.print("[green]Successfully got transcript![/green]")
        transcript_file_name = f"{metadata['title']}.txt"
        with open(transcript_file_name, "w") as f:
            f.write(transcript)
        console.print(f"[green]Transcript saved to {transcript_file_name}[/green]")
        return transcript, metadata.get('language', 'en')
    else:
        console.print("[red]Failed to get transcript![/red]")
        sys.exit(1)


def cleanup_temp_files(temp_output_file_wo_ext, console):
    """Remove temporary audio files."""
    for fmt in ['mp3', 'wav']:
        tmp_file_path = f"{temp_output_file_wo_ext}.{fmt}"
        if os.path.exists(tmp_file_path):
            console.print(f"Removing temp file {tmp_file_path}")
            os.remove(tmp_file_path)


def summarize_and_translate(processor, transcript, language, metadata_title, target_language):
    """Summarize transcript and translate the summary."""
    print("[INFO] Summarizing transcript...")
    summary = processor.summarize(transcript)
    print("[INFO] Summarization complete.")
    with open(f"{metadata_title}-summary", "w") as f:
        f.write(transcript)

    print(f"[INFO] Translating transcript to {target_language}...")
    translated_text = processor.translate(summary, src_lang=language, tgt_lang=target_language)
    print("[INFO] Translation complete.")

    translated_file_name = f"{metadata_title}-summary-{target_language}.txt"
    with open(translated_file_name, "w") as f:
        f.write(translated_text)
    print(f"[INFO] Translated text saved to {translated_file_name}")


def cmd_all(args, processor, config, console):
    """Run the complete process (default)."""
    temp_output_file_wo_ext = "output"
    
    if args.audio:
        transcript, language, metadata_title = process_audio_file(processor, args.audio, console)
    elif args.url:
        transcript, language, metadata_title = process_youtube_url(processor, args.url, temp_output_file_wo_ext, console)
    else:
        print("Usage: ytbrf all <YouTube URL> or ytbrf all -a <audio file>")
        sys.exit(1)
    
    summarize_and_translate(processor, transcript, language, metadata_title, config.summary.target_language)


def cmd_audio(args, processor, console):
    """Download audio only from YouTube URL."""
    url = args.url
    output_path = args.output
    print(f"[INFO] Downloading audio from {url}...")
    audio_path, _ = processor.download_audio(url, output_path)
    print(f"[INFO] Audio downloaded to {audio_path}")


def cmd_transcribe(args, processor, console):
    """Transcribe from audio file and output text file."""
    audio_path = args.audio_path
    output_path = args.output or f"{os.path.splitext(os.path.basename(audio_path))[0]}-transcript.txt"
    print(f"[INFO] Transcribing audio file {audio_path}...")
    transcript, language = processor.transcribe_audio(audio_path)
    with open(output_path, "w") as f:
        f.write(transcript)
    print(f"[INFO] Transcription complete. Transcript saved to {output_path}")


def cmd_translate(args, processor, console):
    """Translate a text file from one language to another."""
    input_file = args.input_file
    src_lang = args.src_lang
    tgt_lang = args.tgt_lang
    output_path = args.output or f"{os.path.splitext(os.path.basename(input_file))[0]}-translated-{tgt_lang}.txt"
    print(f"[INFO] Translating {input_file} from {src_lang} to {tgt_lang}...")
    with open(input_file, "r") as f:
        text = f.read()
    translated_text = processor.translate(text, src_lang=src_lang, tgt_lang=tgt_lang)
    with open(output_path, "w") as f:
        f.write(translated_text)
    print(f"[INFO] Translation complete. Translated text saved to {output_path}")


def cmd_summarize(args, processor, console):
    """Summarize given text in its original language."""
    input_file = args.input_file
    ratio = args.ratio
    output_path = args.output or f"{os.path.splitext(os.path.basename(input_file))[0]}-summary.txt"
    print(f"[INFO] Summarizing {input_file} with ratio {ratio}...")
    with open(input_file, "r") as f:
        text = f.read()
    summary = processor.summarize(text, ratio=ratio)
    with open(output_path, "w") as f:
        f.write(summary)
    print(f"[INFO] Summarization complete. Summary saved to {output_path}")


def cmd_transcript(args, processor, config, console):
    """Get transcript directly from YouTube or transcribe if not available."""
    url = args.url
    output_path = args.output
    temp_output_file_wo_ext = "output"
    
    print(f"[INFO] Getting transcript for {url}...")
    metadata = processor.get_video_metadata(url)
    
    if metadata.get('has_transcript'):
        # Get transcript directly from YouTube
        transcript = processor.get_transcript(metadata['id'])
        language = metadata.get('language', 'en')
        print("[INFO] Successfully retrieved transcript from YouTube.")
    else:
        # Download and transcribe if no transcript is available
        print("[INFO] No transcript available on YouTube. Downloading audio and transcribing...")
        audio_path, _ = processor.download_audio(url, temp_output_file_wo_ext)
        print(f"[INFO] Audio downloaded to: {audio_path}")
        
        transcript, language = processor.transcribe_audio(audio_path)
        print("[INFO] Transcription complete.")
        
        # Clean up temporary files
        cleanup_temp_files(temp_output_file_wo_ext, console)
    
    # Save transcript to file
    if output_path is None:
        output_path = f"{metadata['title']}-{language}.txt"
    
    with open(output_path, "w") as f:
        f.write(transcript)
    
    print(f"[INFO] Transcript saved to {output_path}")
    return transcript, language, metadata['title']


def main():
    console = Console()

    # Check and create default config if missing
    user_config_path = os.path.expanduser("~/.config/ytbrf/config.yaml")
    if not os.path.exists(user_config_path):
        os.makedirs(os.path.dirname(user_config_path), exist_ok=True)
        default_config = ConfigManager()._get_default_config()
        with open(user_config_path, "w") as f:
            yaml.dump(default_config, f, default_flow_style=False)
        console.print(f"[yellow]Default config created at {user_config_path}. Please review and update it as needed.[/yellow]")

    # Check if the last argument is 'help' to handle cases like 'ytbrf transcribe help'
    if len(sys.argv) > 2 and sys.argv[-1] == 'help':
        # Reconstruct the arguments to use --help instead
        sys.argv[-1] = '--help'

    # Check if no arguments were provided
    if len(sys.argv) == 1:
        # Add --help to show the help message
        sys.argv.append('--help')

    parser = argparse.ArgumentParser(
        prog="ytbrf",  # Set the program name explicitly
        description="YouTube Brief: Summarize and translate YouTube videos or audio files."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # all: run the complete process
    parser_all = subparsers.add_parser("all", help="Run the complete process (default)")
    parser_all.add_argument("url", nargs="?", help="YouTube URL")
    parser_all.add_argument("-a", "--audio", help="Path to local audio file for direct summarization.")

    # audio: download audio only
    parser_audio = subparsers.add_parser("audio", help="Download audio only from YouTube URL")
    parser_audio.add_argument("url", help="YouTube URL")
    parser_audio.add_argument("-o", "--output", help="Output audio file path", default="output.mp3")

    # transcribe: transcribe from audio file path
    parser_transcribe = subparsers.add_parser("transcribe", help="Transcribe from audio file and output text file")
    parser_transcribe.add_argument("audio_path", help="Path to audio file")
    parser_transcribe.add_argument("-o", "--output", help="Output transcript file path")

    # translate: translate a text file
    parser_translate = subparsers.add_parser("translate", help="Translate a text file from one language to another")
    parser_translate.add_argument("input_file", help="Input text file path")
    parser_translate.add_argument("-s", "--src-lang", help="Source language", default="auto")
    parser_translate.add_argument("-t", "--tgt-lang", help="Target language", required=True)
    parser_translate.add_argument("-o", "--output", help="Output translated file path")

    # summarize: summarize given text
    parser_summarize = subparsers.add_parser("summarize", help="Summarize given text in its original language")
    parser_summarize.add_argument("input_file", help="Input text file path")
    parser_summarize.add_argument("-r", "--ratio", type=float, help="Approximate summary length ratio (0-1)", default=0.2)
    parser_summarize.add_argument("-o", "--output", help="Output summary file path")

    # transcript: get transcript directly from YouTube or transcribe if not available
    parser_transcript = subparsers.add_parser("transcript", help="Get transcript directly from YouTube or transcribe if not available")
    parser_transcript.add_argument("url", help="YouTube URL")
    parser_transcript.add_argument("-o", "--output", help="Output transcript file path")

    # help: display help for a specific command
    parser_help = subparsers.add_parser("help", help="Display help information for commands")
    parser_help.add_argument("help_command", nargs="?", help="Command to get help for")

    # Parse arguments
    args = parser.parse_args()
    
    # Handle help command
    if args.command == "help":
        if args.help_command:
            # Show help for specific command
            parser.parse_args([args.help_command, "--help"])
        else:
            # Show general help
            parser.parse_args(["--help"])
        return  # Exit after showing help
    
    config_manager = ConfigManager()
    config = config_manager._load_config()
    processor = YouTubeProcessor(config)

    # Command dispatcher
    command_handlers = {
        "all": cmd_all,
        "audio": cmd_audio,
        "transcribe": cmd_transcribe,
        "translate": cmd_translate,
        "summarize": cmd_summarize,
        "transcript": cmd_transcript
    }
    
    # Execute the selected command
    command_handlers[args.command](args, processor, config, console)
    
