import pytest
from unittest.mock import Mock, patch
from ytbrf.youtube import YouTubeProcessor
from ytbrf.config import Config, YouTubeConfig, ConfigManager
from ytbrf.youtube import VideoUnavailableError

@pytest.fixture
def config():
    return Config(
        summary=Mock(ratio=0.2, target_language=""),
        transcription=Mock(whisper_path="whisper", model="base", force_language=""),
        output=Mock(directory=".", filename_pattern="{title}-{lang}.txt"),
        youtube=YouTubeConfig(api_key="test_key", audio_quality="best", audio_format="mp3"),
        translation=Mock(model="Helsinki-NLP/opus-mt-{src}-{tgt}", translate_full=False)
    )

@pytest.fixture
def processor(config):
    config_manager = ConfigManager()
    config = config_manager._load_config()
    return YouTubeProcessor(config)

def test_get_video_info(processor):
    with patch('yt_dlp.YoutubeDL') as mock_ydl:
        mock_info = {
            'id': 'test_id',
            'title': 'Test Video',
            'duration': 120,
            'uploader': 'Test User',
            'description': 'Test Description',
            'thumbnail': 'http://example.com/thumb.jpg',
            'view_count': 1000,
            'like_count': 100,
            'upload_date': '20240101'
        }
        mock_ydl.return_value.__enter__.return_value.extract_info.return_value = mock_info
        
        result = processor.get_video_info('https://youtube.com/watch?v=test_id')
        
        assert result == mock_info
        mock_ydl.return_value.__enter__.return_value.extract_info.assert_called_once()

def test_get_transcript_no_api_key(processor):
    processor.youtube = None
    assert processor.get_transcript('test_id') is None

# def test_get_transcript_with_api_key(processor):
#     with patch('googleapiclient.discovery.build') as mock_build:
#         mock_youtube = Mock()
#         mock_build.return_value = mock_youtube
        
#         mock_captions = Mock()
#         mock_youtube.captions.return_value = mock_captions
        
#         mock_list = Mock()
#         mock_captions.list.return_value = mock_list
#         mock_list.execute.return_value = {'items': [{'id': 'caption_id'}]}
        
#         mock_download = Mock()
#         mock_captions.download.return_value = mock_download
#         mock_download.execute.return_value = b'test transcript'
        
#         result = processor.get_transcript('test_id')
        
#         assert result == 'test transcript'
#         mock_captions.list.assert_called_once()
#         mock_captions.download.assert_called_once()

def test_download_audio(processor):
    with patch('yt_dlp.YoutubeDL') as mock_ydl:
        mock_ydl.return_value.__enter__.return_value.download.return_value = None
        
        result = processor.download_audio('https://youtube.com/watch?v=test_id', 'test.mp3')
        
        assert result[0] == 'test.mp3'
        assert result[1] == 'mp3'
        mock_ydl.return_value.__enter__.return_value.download.assert_called_once()

def test_check_video_availability(processor):
    with patch('yt_dlp.YoutubeDL') as mock_ydl:
        # Test available video
        mock_ydl.return_value.__enter__.return_value.extract_info.return_value = {'id': 'test_id'}
        assert processor.check_video_availability('https://youtube.com/watch?v=test_id') is True
        
        # Test unavailable video
        mock_ydl.return_value.__enter__.return_value.extract_info.side_effect = Exception('Video unavailable')
        assert processor.check_video_availability('https://youtube.com/watch?v=test_id') is False

def test_get_video_metadata(processor):
    with patch.object(processor, 'check_video_availability', return_value=True), \
         patch.object(processor, 'get_video_info', return_value={'id': 'test_id'}), \
         patch.object(processor, 'get_transcript', return_value='test transcript'):
        
        result = processor.get_video_metadata('https://youtube.com/watch?v=test_id')
        
        assert result['id'] == 'test_id'
        assert result['has_transcript'] is True
        assert result['needs_local_transcription'] is False

def test_get_video_metadata_unavailable(processor):
    with patch.object(processor, 'check_video_availability', return_value=False):
        with pytest.raises(VideoUnavailableError, match="Video is not available or restricted"):
            processor.get_video_metadata('https://youtube.com/watch?v=test_id')

def test_whisper_fallback_transcription(processor):
    # Simulate no transcript from YouTube API
    url = "https://www.youtube.com/watch?v=FAyKDaXEAgc"
    audio_path, format = processor.download_audio(url, "output.mp3")
    transcript, language = processor.transcribe_audio(audio_path)
    assert transcript is not None
    assert language is not None
    print(f"Transcription: {transcript}")  # Print the transcription
    assert "Hey buddy how was school? " in transcript  # Assert the expected string is in the transcript
    
def test_transcribe_audio(processor):
    result, language = processor.transcribe_audio()
    assert result == 'test transcript'
    assert language == 'en'
