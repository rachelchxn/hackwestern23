import cv2
import face_recognition
import numpy as np
import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Firebase
cred = credentials.Certificate('hw23-e0512-firebase-adminsdk-3ax9k-293086f6f4.json')
firebase_admin.initialize_app(cred)
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

# Fetch encodings and names at the start (or periodically refresh if needed)
face_encodings_from_db, face_names_from_db = fetch_encodings_from_firestore()

video_capture = cv2.VideoCapture(1)

while True:
    ret, frame = video_capture.read()
    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
    rgb_small_frame = np.ascontiguousarray(small_frame[:, :, ::-1])

    face_locations = face_recognition.face_locations(rgb_small_frame)
    face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

    face_names = []
    for face_encoding in face_encodings:
        matches = face_recognition.compare_faces(face_encodings_from_db, face_encoding, tolerance=0.5)
        name = "Unknown"

        if True in matches:
            first_match_index = matches.index(True)
            name = face_names_from_db[first_match_index]
        else:
            face_encoding_list = face_encoding.tolist()
            doc_ref = db.collection('people').document()
            doc_ref.set({
                'image_enc': face_encoding_list,
                'name': "Unnamed Person",
            })
            # Optionally refresh the encodings from Firestore
            face_encodings_from_db, face_names_from_db = fetch_encodings_from_firestore()

        face_names.append(name)

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
