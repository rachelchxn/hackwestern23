import threading
import cv2
from transcribe import transcribe, stop_audio_recording, start_audio_recording, summarize
from app import camera_operations, stop_camera_recording, start_camera_recording
import time
from firebase_admin import firestore

db = firestore.client()

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
            print("here is full transcript:")
            print(full_transcript)

            docs = db.collection('conversations').stream()
            # unique_id = str(uuid.uuid4())
            docs = list(docs)
            unique_id = str(len(docs)) + 'voice'
            summary = summarize(full_transcript).choices[0].message.content

            # name_line = summary.split("\n")[0]
            # location_line = summary.split("\n")[1]
            # points_lines = summary.split("\n")[3:]

            # # Formatting the information into separate variables
            # name = name_line.split(": ")[1]
            # location = location_line.split(": ")[1]
            # points = [line.split("- ")[1] for line in points_lines if line.startswith("-")]

            doc_ref = db.collection('conversations').document(unique_id)
            doc_ref.set({
                "dialogue": summary
            })
            print(summary)
            # upload transcript
            ser.write(str.encode(full_transcript + '\n'))



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


if __name__ == "__main__":
    print("ready")
    main()