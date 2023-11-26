import cv2
import face_recognition
import numpy as np
import speech_recognition as sr
import threading
import pyaudio
import uuid
import io
from PIL import Image

import firebase_admin

cred = firebase_admin.credentials.Certificate('hw23-e0512-firebase-adminsdk-3ax9k-293086f6f4.json')
from firebase_admin import credentials, firestore, storage
from google.cloud import storage

from functions.firebase import uploadImageFromBlob, uploadImageFromPath
db = firestore.client()

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
unrecognized_threshold = 3  # Number of frames to confirm an unrecognized face

video_capture = cv2.VideoCapture(1)


def camera_operations(video_capture):
    face_encodings_from_db, face_names_from_db = fetch_encodings_from_firestore()

    while True:
        ret, frame = video_capture.read()
        # print(frame)
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
                else:
                    # Generate unique ID for the image and upload it
                    unique_id = str(uuid.uuid4())
                    image_path = f"faces/{unique_id}.jpg"
                    # save the frame into the images folder
                    cv2.imwrite(image_path, face_image)
                    image_url = uploadImageFromPath(image_path, image_path)
                    print(image_url)

                    # Save the encoding and image URL in Firestore
                    doc_ref = db.collection('people').document(unique_id)
                    doc_ref.set({
                        'image_enc': face_encoding.tolist(),
                        'name': "Unnamed Person",
                        'image_url': image_url,
                    })

                    # Update local encodings for real-time comparison
                    face_encodings_from_db.append(face_encoding)
                    face_names_from_db.append("Unnamed Person")

                    name = "Unnamed Person"

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

            cv2.imshow('Video', frame)
            
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    video_capture.release()
    cv2.destroyAllWindows()

# Example usage
video_capture = cv2.VideoCapture(0)

