import shortuuid
from moviepy.editor import VideoFileClip

from audio_transcription.utils import recognise_action, transcript_action


def extract_audio_from_video(video_path, audio_output_path):
    """
    Extracts the audio from a video file and saves it as a separate audio file.

    Args:
        video_path (str): The path to the video file.
        audio_output_path (str): The path and filename for the output audio file.

    Returns:
        str or None: The file path of the extracted audio if successful, or None if an error occurred.

    Raises:
        Exception: If an error occurs during audio extraction.

    Example:
        video_path = "path/to/video.mp4"
        audio_output_path = "path/to/output/audio.wav"
        extracted_audio_path = extract_audio_from_video(video_path, audio_output_path)
        if extracted_audio_path:
            print("Extracted audio saved to:", extracted_audio_path)
    """
    try:
        video = VideoFileClip(video_path)
        audio = video.audio
        audio.write_audiofile(audio_output_path)
        video.close()
        audio.close()
        print("Audio extraction successful!")
        return audio_output_path
    except Exception as e:
        print("An error occurred during audio extraction:", str(e))
        return None


def process_video(video_path):
    """
    Process a video by extracting audio, recognizing actions, and transcribing the audio.

    Args:
        video_path (str): The path to the video file.

    Returns:
        str or None: The transcript of the video's audio if successful, or None if an error occurred.

    Example:
        video_path = "path/to/video.mp4"
        transcript = process_video(video_path)
        if transcript:
            print("Transcript:", transcript)
    """
    try:
        # Generate a unique ID for the audio file
        audio_id = shortuuid.uuid()

        # Define the audio output path with the unique ID
        audio_output_path = f"path/to/output/{audio_id}.wav"

        # Extract audio from the video
        extracted_audio_path = extract_audio_from_video(video_path, audio_output_path)

        if extracted_audio_path:
            # Recognize action from the extracted audio
            recognise_action(audio_id, extracted_audio_path)

            # Transcribe the video's audio
            transcript = transcript_action(extracted_audio_path)

            return transcript
        else:
            return None
    except Exception as e:
        print("An error occurred during video processing:", str(e))
        return None
