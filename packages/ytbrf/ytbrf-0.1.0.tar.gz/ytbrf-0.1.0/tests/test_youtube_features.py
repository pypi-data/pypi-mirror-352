#!/usr/bin/env python3

import os
import shutil
from ytbrf.config import ConfigManager
from ytbrf.youtube import YouTubeProcessor
from rich.console import Console

console = Console()

def test_youtube_features():
    # Load configuration
    config_manager = ConfigManager()
    config = config_manager.get_config()
    
    # Create YouTube processor
    processor = YouTubeProcessor(config)
    
    # Test video URL (a short video with captions)
    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # Rick Astley - Never Gonna Give You Up
    
    try:
        # 1. Get video metadata using yt-dlp (no API key needed)
        console.print("\n[bold cyan]1. Getting video metadata using yt-dlp...[/bold cyan]")
        metadata = processor.get_video_metadata(test_url)
        console.print(f"Title: {metadata['title']}")
        console.print(f"Duration: {metadata['duration']} seconds")
        console.print(f"Has transcript: {metadata['has_transcript']}")
        
        # 2. Try to get transcript (requires API key)
        if config.youtube.api_key:
            console.print("\n[bold cyan]2. Getting transcript using YouTube API...[/bold cyan]")
            transcript = processor.get_transcript(metadata['id'])
            if transcript:
                console.print("[green]Successfully got transcript![/green]")
                # Save transcript for inspection
                with open("test_transcript.srt", "w", encoding="utf-8") as f:
                    f.write(transcript)
                console.print("Transcript saved to test_transcript.srt")
            else:
                console.print("[yellow]No transcript available from YouTube API[/yellow]")
        else:
            console.print("\n[yellow]Skipping transcript download - YouTube API key not configured[/yellow]")
        
        # 3. Check if ffmpeg is available
        ffmpeg_available = shutil.which('ffmpeg') is not None
        
        # 3. Download audio using yt-dlp (no API key needed)
        if ffmpeg_available:
            console.print("\n[bold cyan]3. Downloading audio using yt-dlp...[/bold cyan]")
            output_path = "test_audio"
            try:
                audio_path, format = processor.download_audio(test_url, output_path)
                console.print(f"[green]Successfully downloaded audio to {audio_path}[/green]")
                
                # Clean up test files
                if os.path.exists(audio_path):
                    os.remove(audio_path)
            except Exception as e:
                console.print(f"[red]Error downloading audio: {str(e)}[/red]")
        else:
            console.print("\n[yellow]Skipping audio download - ffmpeg not found in PATH[/yellow]")
            console.print("[yellow]To enable audio download, please install ffmpeg and make sure it's in your PATH[/yellow]")
        
        # Clean up transcript file if it exists
        if os.path.exists("test_transcript.srt"):
            os.remove("test_transcript.srt")
            
    except Exception as e:
        console.print(f"[red]Error during testing: {str(e)}[/red]")
        raise

def test_transcribe_summarize_translate_with_testdata():
    from ytbrf.config import ConfigManager
    from ytbrf.youtube import YouTubeProcessor
    import os
    # Prepare config and processor
    config_manager = ConfigManager()
    config = config_manager.get_config()
    print(f"Config: {config}\n")
    processor = YouTubeProcessor(config)
    # Use testdata/output.mp3
    audio_path = os.path.join(os.path.dirname(__file__), '../testdata/output2.mp3')
    transcript, lang = processor.transcribe_audio(audio_path)
    print(f"Transcript: {transcript}\n")
    expected_phrases = [
        "Large Language Models",
        "transformer",
        "intelligent"
    ]
    for phrase in expected_phrases:
        assert phrase.lower() in transcript.lower()
    summary = processor.summarize(transcript)
    assert summary and isinstance(summary, str)
    assert len(summary) < len(transcript) * 0.3
    assert len(summary) > len(transcript) * 0.1
    # Translate summary to Chinese
    translated = processor.translate(summary, src_lang=lang, tgt_lang='zh-cn')
    assert translated and isinstance(translated, str)
    print(f"Transcript: {transcript}\nSummary: {summary}\nTranslated: {translated}")
    assert any(word in translated for word in ['大型语言模型', '基础模型', '潜力', '上下文'])

if __name__ == "__main__":
    test_youtube_features()