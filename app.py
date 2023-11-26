import cv2
import face_recognition
import numpy as np
import speech_recognition as sr
import threading
import pyaudio
import uuid
import os
from PIL import Image

from firebase_admin import credentials, firestore, storage
import firebase_admin
from google.cloud import storage

from functions.firebase import uploadImageFromBlob, uploadImageFromPath
db = firestore.client()


# #bluetooth stuff
# import serial
# from serial import Serial
# #Define the COM port and baud rate
# com_port = 'COM9'  # Replace with the actual COM port on your system
# baud_rate = 115200
# #Create a serial object
# ser = serial.Serial(com_port, baud_rate, timeout=1)


recording_active = True

def stop_camera_recording():
    global recording_active
    recording_active = False

def start_camera_recording():
    global recording_active
    recording_active = True

def fetch_encodings_from_firestore():
    fetched_encodings = []
    fetched_names = []
    
    # Fetch data from Firestore
    docs = db.collection('people').stream()
    for doc in docs:
        data = doc.to_dict()
        if 'image_enc' in data and 'name' in data:
            fetched_encodings.append(np.array(data['image_enc']))
            fetched_names.append(data['name'])
    
    return fetched_encodings, fetched_names

def find_similar_face_key(face_encoding, faces_dict, tolerance=0.6):
    for face_key in faces_dict.keys():
        if np.linalg.norm(np.array(face_key) - face_encoding) < tolerance:
            return face_key
    return None

# Dictionary to track unrecognized faces
unrecognized_faces = {}
unrecognized_threshold = 4  # Number of frames to confirm an unrecognized face

from google.cloud.firestore import SERVER_TIMESTAMP

def camera_operations(video_capture, ser, unique_id):
    face_encodings_from_db, face_names_from_db = fetch_encodings_from_firestore()
    
    count = 0   #count of face detections

    while recording_active:
        ret, frame = video_capture.read()
        if not ret:
            break

        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_small_frame = np.ascontiguousarray(small_frame[:, :, ::-1])

        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        face_names = []

        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4

            top = max(top, 0)
            right = min(right, frame.shape[1])
            bottom = min(bottom, frame.shape[0])
            left = max(left, 0)

            face_image = frame[top:bottom, left:right]

            if face_image.size > 0:       
                matches = face_recognition.compare_faces(face_encodings_from_db, face_encoding, tolerance=0.5)

                if True in matches:
                    first_match_index = matches.index(True)
                    name = face_names_from_db[first_match_index]
                    similar_key = find_similar_face_key(face_encoding, unrecognized_faces)
                    if similar_key is not None:
                        del unrecognized_faces[similar_key]  # Remove from unrecognized as it's now recognized
                else:
                    similar_key = find_similar_face_key(face_encoding, unrecognized_faces)

                    if similar_key is not None:
                        unrecognized_faces[similar_key]['counter'] += 1
                        print(f"HERE:{unrecognized_faces[similar_key]['counter']}")
                    else:
                        print("New face detected, starting counter")
                        unrecognized_faces[tuple(face_encoding)] = {'counter': 1, 'encoding': face_encoding}

                    if similar_key is not None and unrecognized_faces[similar_key]['counter'] > unrecognized_threshold:
                        # Process new unrecognized face
                        name = "Unnamed Person"
                        face_encoding_list = unrecognized_faces[similar_key]['encoding'].tolist()
                        doc_ref = db.collection('people').document()

                        docs = db.collection('people').stream()
                        docs = list(docs)
                        
                        image_path = f"faces/{unique_id}.jpg"
                        cv2.imwrite(image_path, face_image)
                        image_url = uploadImageFromPath(image_path, image_path)

                        doc_ref = db.collection('people').document(unique_id)
                        doc_ref.set({
                            'image_enc': face_encoding_list,
                            'name': "Unnamed Person",
                            'image_url': image_url,
                            'timestamp': SERVER_TIMESTAMP 
                        })
                        os.remove(image_path)

                        # Update local encodings for real-time comparison
                        face_encodings_from_db.append(face_encoding)
                        face_names_from_db.append("Unnamed Person")

                        name = "Unnamed Person"   
                        del unrecognized_faces[similar_key]
                        
                    else:
                        name = "[Checking...]"

                if name:
                    face_names.append(name)


                # Drawing the results on the frame
                for (top, right, bottom, left), name in zip(face_locations, face_names):
                    top *= 4
                    right *= 4
                    bottom *= 4
                    left *= 4
                    cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
                    cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
                    font = cv2.FONT_HERSHEY_DUPLEX
                    cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

        if(len(face_locations) > 0):
            count += 1
            ser.write(str.encode(name + '\n'))
            if((count > 2) and (name != "[Checking...]")):
                stop_camera_recording()
        else:
            ser.write(str.encode('...' + '\n'))
        cv2.imshow('Video', frame)
            
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    video_capture.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    video_capture = cv2.VideoCapture(1+cv2.CAP_DSHOW)
    camera_operations(video_capture)