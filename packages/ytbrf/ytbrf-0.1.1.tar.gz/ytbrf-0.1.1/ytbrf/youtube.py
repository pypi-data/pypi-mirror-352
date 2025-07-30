import os
import shutil

import googleapiclient.discovery
from typing import Optional, Dict, Any, Tuple
import yt_dlp
import time
from functools import wraps
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from rich.console import Console
from rich.progress import Progress
import platform
import subprocess
from openai import OpenAI
import requests

from .config import Config
import whisper
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from huggingface_hub.utils import EntryNotFoundError
from huggingface_hub import try_to_load_from_cache, _CACHED_NO_EXIST

console = Console()

WHISPER_CPP_REQUIRED_AUDIO_RATE = 16000

class YouTubeAPIError(Exception):
    """Base exception for YouTube API errors"""
    pass

class APIQuotaExceededError(YouTubeAPIError):
    """Raised when YouTube API quota is exhausted"""
    pass

class VideoUnavailableError(YouTubeAPIError):
    """Raised when video is unavailable or restricted"""
    pass

def retry(retries: int = 3, delay: int = 5, exceptions: tuple = (Exception,)):
    """Decorator for retrying API calls"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            attempts = 0
            while attempts < retries:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    attempts += 1
                    if attempts >= retries:
                        raise
                    time.sleep(delay)
            return func(*args, **kwargs)
        return wrapper
    return decorator

class YouTubeProcessor:
    def __init__(self, config: Config):
        self.config = config
        self.youtube = None
        
        # Make API key optional
        if config.youtube.api_key:
            try:
                self.youtube = build('youtube', 'v3', developerKey=config.youtube.api_key)
            except HttpError as e:
                if e.resp.status == 403:
                    raise APIQuotaExceededError("YouTube API quota exceeded") from e
                raise YouTubeAPIError(f"YouTube API connection failed: {str(e)}") from e
        else:
            print("Warning: YouTube API key is missing. Some features will be limited.")

    def get_video_info(self, url: str) -> Dict[str, Any]:
        """Extract video information using yt-dlp."""
        try:
            with yt_dlp.YoutubeDL() as ydl:
                info = ydl.extract_info(url, download=False)
                return {
                    'id': info['id'],
                    'title': info['title'],
                    'duration': info.get('duration', 0),
                    'uploader': info.get('uploader', ''),
                    'description': info.get('description', ''),
                    'thumbnail': info.get('thumbnail', ''),
                    'view_count': info.get('view_count', 0),
                    'like_count': info.get('like_count', 0),
                    'upload_date': info.get('upload_date', ''),
                }
        except Exception as e:
            console.print(f"[red]Error extracting video info: {str(e)}[/red]")
            raise

    @retry(retries=3, delay=5, exceptions=(APIQuotaExceededError, HttpError))
    def get_transcript(self, video_id: str) -> Optional[str]:
        """Try to get transcript from YouTube API."""
        if not self.youtube:
            console.print("[yellow]Cannot get transcript: YouTube API not available[/yellow]")
            return None

        try:
            transcript_list = self.youtube.captions().list(
                part="snippet",
                videoId=video_id
            ).execute()
            
            if not transcript_list['items']:
                return None
                
            # Get the first available transcript
            caption_id = transcript_list['items'][0]['id']
            transcript = self.youtube.captions().download(
                id=caption_id,
                tfmt='srt'
            ).execute()
            
            return transcript.decode('utf-8')
        except HttpError as e:
            console.print(f"[yellow]Could not get transcript from YouTube: {str(e)}[/yellow]")
            return None

    def download_audio(self, url: str, output_filename_wo_ext: str = None) -> Tuple[str, str]:
        """Download audio from YouTube video.
        
        Returns:
            Tuple[str, str]: (audio_path, format)
        """
        video_info = self.get_video_info(url)
        if output_filename_wo_ext is None:
            output_filename_wo_ext = video_info['title']
        try:
            # First try with audio extraction
            ydl_opts = {
                'format': 'bestaudio/best',
                'postprocessor_args': [
                    '-ar', str(WHISPER_CPP_REQUIRED_AUDIO_RATE)  # Set audio sampling rate to 16000 Hz
                ],
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': self.config.youtube.audio_format,
                    'preferredquality': self.config.youtube.audio_quality,
                }],
                'outtmpl': output_filename_wo_ext,
            }
            
            with Progress() as progress:
                task = progress.add_task("[cyan]Downloading audio...", total=None)
                try:
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        ydl.download([url])
                    
                    # Get the actual output path (yt-dlp might modify it)
                    base_path = os.path.splitext(output_filename_wo_ext)[0]
                    audio_path = f"{base_path}.{self.config.youtube.audio_format}"
                    
                    return audio_path, self.config.youtube.audio_format
                except Exception as e:
                    if "ffprobe and ffmpeg not found" in str(e):
                        console.print("[yellow]ffmpeg not found. Falling back to direct download without audio extraction.[/yellow]")
                        # Fall back to direct download without audio extraction
                        ydl_opts = {
                            'format': 'bestaudio/best',
                            'outtmpl': output_filename_wo_ext,
                        }
                        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                            ydl.download([url])
                        
                        # The format will be whatever yt-dlp downloaded
                        # We need to find the actual file that was created
                        for ext in ['mp4', 'webm', 'm4a', 'mp3']:
                            possible_path = f"{output_filename_wo_ext}.{ext}"
                            if os.path.exists(possible_path):
                                return possible_path, ext
                        
                        # If we can't find the file, raise the original error
                        raise
                    else:
                        raise
        except Exception as e:
            console.print(f"[red]Error downloading audio: {str(e)}[/red]")
            raise

    def check_video_availability(self, url: str) -> bool:
        """Check if the video is available and accessible."""
        try:
            with yt_dlp.YoutubeDL() as ydl:
                ydl.extract_info(url, download=False)
            return True
        except Exception as e:
            console.print(f"[red]Video is not available: {str(e)}[/red]")
            return False

    def get_video_metadata(self, url: str) -> Dict[str, Any]:
        """Get comprehensive video metadata including availability and transcript status."""
        if not self.check_video_availability(url):
            raise VideoUnavailableError("Video is not available or restricted")

        info = self.get_video_info(url)
        
        # Only check for transcript if YouTube API is available
        has_transcript = False
        if self.youtube:
            has_transcript = bool(self.get_transcript(info['id']))

        return {
            **info,
            'has_transcript': has_transcript,
            'needs_local_transcription': not has_transcript,
        }

    def _ensure_model_downloaded(self, model_name: str):
        # Check if model is cached locally, if not, download it
        try:
            _ = try_to_load_from_cache(model_name, 'config.json')
        except EntryNotFoundError:
            # Download model and tokenizer
            AutoTokenizer.from_pretrained(model_name)
            AutoModelForSeq2SeqLM.from_pretrained(model_name)

    def summarize(self, text: str, model_name: str = None) -> str:
        summary_cfg = self.config.summary
        model_name = getattr(summary_cfg, "model", "gpt-3.5-turbo")
        console.print(f"[yellow]Summarization model selected: {model_name}[/yellow]")                 

        if getattr(summary_cfg, "type", None) == "openai":
            headers = {"Authorization": f"Bearer {summary_cfg.api_key}", "Content-Type": "application/json"}
            system_prompt = f'''
You are a highly advanced AI summarization tool.Below is a transcript with timestamps provided by the user. Your task is to extract the key points and summarize the content while retaining the original language style, tone, and context. The summary should be concise, capturing the essential ideas and information in approximately {float(summary_cfg.ratio)*100}% of the original length. 

**Instructions:** 

1.Read through the entire transcript carefully, paying close attention to the timestamps to ensure you capture the flow of conversation. 

2.Identify the main ideas, themes, and important details conveyed in the transcript. 

3.Write a summary that reflects the original language and maintains the same tone and context of the content. 

4.Ensure that the final summary is around {float(summary_cfg.ratio)*100}% of the original transcript length.
'''

            user_prompt = f'''
Summarize this text in approximately {float(summary_cfg.ratio)*100}% of the original length:

{text.strip()}
'''
            payload = {
                "model": model_name,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": text.strip()}
                ],
                "temperature": 0.2
            }
            from tenacity import retry, retry_if_exception, stop_after_attempt, wait_exponential
            
            @retry(
                retry=retry_if_exception(lambda e: isinstance(e, requests.exceptions.HTTPError) 
                                        and 400 <= e.response.status_code < 500),
                stop=stop_after_attempt(3),
                wait=wait_exponential(multiplier=1, min=2, max=10)
            )
            def _retry_openai_request():
                response = requests.post(f"{summary_cfg.server_url}/chat/completions", 
                                       json=payload, headers=headers)
                response.raise_for_status()
                return response
            
            response = _retry_openai_request()
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"].strip()

        self._ensure_model_downloaded(model_name)
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
        input_text = f"summarize: {text.strip()}"
        inputs = tokenizer(input_text, return_tensors="pt", max_length=2048, truncation=True)
        summary_ids = model.generate(**inputs, max_length=256, num_beams=4, early_stopping=True)
        summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
        return summary

    def translate(self, text: str, src_lang: str, tgt_lang: str, model_name: str = None) -> str:
        summary_cfg = self.config.summary
        if getattr(summary_cfg, "type", None) == "openai":
            import requests
            headers = {"Authorization": f"Bearer {summary_cfg.api_key}", "Content-Type": "application/json"}
            model_name = getattr(summary_cfg, "model", "gpt-3.5-turbo")
            payload = {
                "model": model_name,
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant that translates text."},
                    {"role": "user", "content": f"Translate the following text from {src_lang} to {tgt_lang}: {text.strip()}"}
                ],
                "temperature": 0.2
            }
            response = requests.post(f"{summary_cfg.server_url}/chat/completions", json=payload, headers=headers)
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"].strip()
        # Default: HuggingFace Transformers
        if model_name is None:
            console.print("[yellow]No translation model specified. Using default model: t5-base[/yellow]")
            model_name = "t5-base"
        self._ensure_model_downloaded(model_name)
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
        if "mt5" in model_name.lower():
            translate_input = f"{text.strip()}"
            forced_bos_token_id = None
            if hasattr(tokenizer, "lang_code_to_id") and tgt_lang in tokenizer.lang_code_to_id:
                forced_bos_token_id = tokenizer.lang_code_to_id[tgt_lang]
            inputs = tokenizer(translate_input, return_tensors="pt", max_length=512, truncation=True)
            gen_kwargs = {"max_length": 256, "num_beams": 4, "early_stopping": True}
            if forced_bos_token_id is not None:
                gen_kwargs["forced_bos_token_id"] = forced_bos_token_id
            translated_ids = model.generate(**inputs, **gen_kwargs)
            translated = tokenizer.decode(translated_ids[0], skip_special_tokens=True)
            import re
            translated = re.sub(r"<extra_id_\\d+>", "", translated).strip()
        elif "nllb" in model_name.lower():
            tokenizer.src_lang = src_lang
            translate_input = text.strip()
            forced_bos_token_id = None
            if hasattr(tokenizer, "lang_code_to_id") and tgt_lang in tokenizer.lang_code_to_id:
                forced_bos_token_id = tokenizer.lang_code_to_id[tgt_lang]
            inputs = tokenizer(translate_input, return_tensors="pt", max_length=512, truncation=True)
            gen_kwargs = {"max_length": 256, "num_beams": 4, "early_stopping": True}
            if forced_bos_token_id is not None:
                gen_kwargs["forced_bos_token_id"] = forced_bos_token_id
            translated_ids = model.generate(**inputs, **gen_kwargs)
            translated = tokenizer.batch_decode(translated_ids, skip_special_tokens=True)[0]
        else:
            translate_input = f"translate {src_lang} to {tgt_lang}: {text.strip()}"
            inputs = tokenizer(translate_input, return_tensors="pt", max_length=512, truncation=True)
            translated_ids = model.generate(**inputs, max_length=256, num_beams=4, early_stopping=True)
            translated = tokenizer.decode(translated_ids[0], skip_special_tokens=True)
        return translated

    def transcribe_audio(self, audio_path: str) -> tuple[str, str]:
        if self.config.transcription.method == "whisper-cpp":
            return self._transcribe_whisper_cpp(audio_path)
        elif self.config.transcription.method == "whisper-python":
            return self._transcribe_whisper_python(audio_path)
        elif self.config.transcription.method == "faster-whisper":
            return self._transcribe_faster_whisper(audio_path)
            
    def _subprocess_stream(self, command):
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        for line in process.stdout:
            print(line, end="")
        process.wait()
        
    def _transcribe_whisper_cpp(self, audio_path: str) -> tuple[str, str]:
        # call whisper-cpp CLI locally to transcribe audio file into text
        
        # convert given audio file to wave format 16kHz using ffmpeg. Do this using local ffmpeg executable
        # and use the same ffmpeg executable that is used by yt-dlp

        # if audio_path is not a wave file, convert it to wave file
        if audio_path.endswith(".wav"):
            wave_file_path = audio_path
        else:
            console.print(f"ytbrf Converting {audio_path} to wave file")
            
            # detect if ffmpeg is installed and if not, raise an error
            if shutil.which("ffmpeg") is None:
                raise ValueError("ffmpeg not found. Please install ffmpeg or provide the path to ffmpeg in the config file.")

            # Construct the output wave file path
            wave_file_path = audio_path.rsplit('.', 1)[0] + ".wav"
            # Run the ffmpeg command
            command = ['ffmpeg', '-i', audio_path, '-ar', '16000', wave_file_path]
            # run the command and stream the stdout and stderr to the console
            console.print(f"Converting {audio_path} to {wave_file_path} with ffmpeg")
            result = subprocess.run(command, check=True, capture_output=False, text=True)
            if result.returncode != 0:
                console.print(f"Error converting file {audio_path} to wave")
                os.exit(1)
            audio_path = wave_file_path
        
        # Construct the output wave file path
        output_file_path_wo_ext = audio_path.rsplit('.', 1)[0]
        txt_file_path = output_file_path_wo_ext + ".txt"

        # check if txt_file_path exists and if it does, delete it
        if os.path.exists(output_file_path_wo_ext):
            os.remove(output_file_path_wo_ext)

        # Run the whisper-cpp command
        model_path = self.config.transcription.models_dir + "/ggml-" + self.config.transcription.model + ".bin"
        source_lang = self.config.transcription.force_language
        if source_lang is None:
            source_lang = "auto"
        command = ["whisper-cpp", '-f', wave_file_path, '-otxt', '-m', model_path, '-l', source_lang, '-of', output_file_path_wo_ext, '-nt']
        result = subprocess.run(command, check=True, capture_output=False, text=True)
        # Read the transcript from the output file
        with open(txt_file_path, 'r') as f:
            transcript = f.read()

        # Delete the txt file
        os.remove(txt_file_path)

        if self.config.transcription.delete_intermediate_files:
            # Delete the wave file
            os.remove(wave_file_path)
        # Return the transcript, and the language detected from whisper-cpp
        return transcript, "auto"
        
    def _transcribe_faster_whisper(self, audio_path: str) -> tuple[str, str]:
        import faster_whisper
        model = faster_whisper.WhisperModel(self.config.transcription.model, device=self.device, compute_type="float16")
        segments, info = model.transcribe(audio_path)
        
        transcript = ""
        for segment in segments:
            transcript += segment.text + " "

        detected_lang = info.language
        return transcript, detected_lang        

    def _transcribe_whisper_python(self, audio_path: str) -> tuple[str, str]:     
        console.print(f"[green]Loading Whisper model: {self.config.transcription.model}[/green]")
        model = whisper.load_model(self.config.transcription.model)
        console.print(f"[green]Transcribing audio file: {audio_path}[/green]")
        result = model.transcribe(audio_path)
        transcript = result["text"]
        detected_lang = result["language"]
    
        console.print(f"[green]Transcription complete. Detected language: {detected_lang}[/green]")
    
        # Derive video title from audio file name
        video_title = os.path.splitext(os.path.basename(audio_path))[0]
    
        # Save transcript to a local file with video title and detected language
        output_path = f"{video_title}-{detected_lang}.txt"
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(transcript)
    
        return transcript, detected_lang

    def process_video(self, url: str) -> Dict[str, Any]:
        """Process video to get transcript and metadata."""
        metadata = self.get_video_metadata(url)
        transcript = metadata.get('has_transcript')

        if not transcript:
            audio_path, _ = self.download_audio(url, "output")
            transcript, language = self.transcribe_audio(audio_path)
            metadata['transcript'] = transcript
            metadata['language'] = language

        return metadata

    def get_transcript_or_audio(self, url: str) -> Optional[str]:
        """Download subtitles with the smallest audio file using yt-dlp."""
        try:
            with yt_dlp.YoutubeDL({'writesubtitles': True, 'writeautomaticsub': True, 'format': 'worstaudio'}) as ydl:
                ydl.download([url])
                return 'Subtitles and audio downloaded'
        except Exception as e:
            console.print(f"[red]Error downloading subtitles and audio: {str(e)}[/red]")
            return None
