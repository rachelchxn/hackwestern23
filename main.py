import threading
import uuid
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

api_key = "AIzaSyBN197RE1Jgm3F_oQ8OkRIXg9RB6xPXL3g"

shared_data = {
    'person_id': None
}


def handle_transcription(shared_data):
    transcript_parts = transcribe(api_key)
    full_transcript = "".join(transcript_parts)
    print("here is full transcript:")
    print(full_transcript)

    docs = db.collection('conversations').stream()
    docs = list(docs)
    summary = summarize(full_transcript).choices[0].message.content

    name_line = summary.split("\n")[0]
    location_line = summary.split("\n")[1]
    points_lines = summary.split("\n")[3:]

    #Formatting the information into separate variables
    name = name_line.split(": ")[1]
    location = location_line.split(": ")[1]
    points = [line.split("- ")[1] for line in points_lines if line.startswith("-")]

    doc_ref = db.collection('people').document(shared_data['person_id'])
    doc = doc_ref.get()
    if doc.exists:
        doc_ref.update({
        "name": name,
        "location": location,
        "transcript": full_transcript,
        "points": firestore.ArrayUnion(points)
    })
    else:
        doc_ref.set({
            "name": name,
            "location": location,
            "transcript": full_transcript,
            "points": points
        })
    print(summary)
    # upload transcript
    ser.write(str.encode(full_transcript + '\n'))

unique_id = str(uuid.uuid4())

video_capture = cv2.VideoCapture(1) 

def main():
    while True:
        
        camera_thread = threading.Thread(target=lambda: camera_operations(video_capture, ser, unique_id))
        transcription_thread = threading.Thread(target=lambda: handle_transcription(person_id))

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