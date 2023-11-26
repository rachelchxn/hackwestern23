import threading
import cv2
from transcribe import transcribe, stop_audio_recording, start_audio_recording
from app import camera_operations, stop_camera_recording, start_camera_recording
import time

#bluetooth stuff
import serial
from serial import Serial
#Define the COM port and baud rate
com_port = 'COM9'  # Replace with the actual COM port on your system
baud_rate = 115200
#Create a serial object
ser = serial.Serial(com_port, baud_rate, timeout=1)

def main():
    while True:
        api_key = "AIzaSyBN197RE1Jgm3F_oQ8OkRIXg9RB6xPXL3g"

        def handle_transcription():
            transcript_parts = transcribe(api_key)
            full_transcript = "".join(transcript_parts)
            print("here is full transcript:" + '\n')
            print(full_transcript)

        video_capture = cv2.VideoCapture(1) 
        camera_thread = threading.Thread(target=lambda: camera_operations(video_capture, ser))
        transcription_thread = threading.Thread(target=handle_transcription)

        while True:
            if ser.in_waiting > 0:
                res = ser.readline().decode()
                if(res == "on"):
                    start_camera_recording()
                    start_audio_recording()

                    # Camera operations thread
                    camera_thread.start()

                    # Transcription thread
                    transcription_thread.start()

                elif(res == "off"):
                    stop_audio_recording()
                    stop_camera_recording()
                    break

        # Wait for both threads to finish
        transcription_thread.join()
        camera_thread.join()
        video_capture.release()

        # camera_thread = None
        # transcription_thread = None

if __name__ == "__main__":
    print("ready")
    main()