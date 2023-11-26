import threading
import cv2
from transcribe import transcribe, stop_recording
from app import camera_operations
import time

def main():
    api_key = "AIzaSyBN197RE1Jgm3F_oQ8OkRIXg9RB6xPXL3g"

    def handle_transcription():
        transcript_parts = transcribe(api_key)
        full_transcript = "".join(transcript_parts)
        print(full_transcript)

    # Transcription thread
    transcription_thread = threading.Thread(target=handle_transcription)
    transcription_thread.start()

    # Camera operations thread
    video_capture = cv2.VideoCapture(1) 
    camera_thread = threading.Thread(target=lambda: camera_operations(video_capture))
    camera_thread.start()

    try:
        # For demonstration, let's wait for 10 seconds and then stop recording
        time.sleep(10)
        stop_recording()
    except Exception as e:
        print(f"An error occurred: {e}")

    # Wait for both threads to finish
    transcription_thread.join()
    camera_thread.join()
    video_capture.release()

if __name__ == "__main__":
    main()