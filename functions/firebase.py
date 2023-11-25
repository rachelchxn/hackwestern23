import firebase_admin
import cv2
from PIL import Image
import io
import numpy as np

cred = firebase_admin.credentials.Certificate('hw23-e0512-firebase-adminsdk-3ax9k-293086f6f4.json')
firebase_admin.initialize_app(cred)

from firebase_admin import firestore, storage

# Get a reference to the Firestore service
db = firestore.client()

# write into the people collection
def create_document(data, document_name = None, collection_name = 'people'):
    if document_name is None:
        doc_ref = db.collection(collection_name).document()
    else:
        doc_ref = db.collection(collection_name).document(document_name)
    doc_ref.set(data)
    return doc_ref.id

def read_document(document_id, collection_name = 'people'):
    doc_ref = db.collection(collection_name).document(document_id)
    doc = doc_ref.get()
    return doc.to_dict()

# upload image to storage
def uploadImageFromPath(path, image_name):
    print("uploading image...")
    
    bucket = storage.bucket("hw23-e0512.appspot.com")
    blob = bucket.blob(image_name)
    blob.upload_from_filename(path)

    return blob.public_url

def uploadImageFromBlob(blob, image_name):
    print("uploading image...")
    
    bucket = storage.bucket("hw23-e0512.appspot.com")
    blob = bucket.blob(image_name)
    image = blob[0].transpose(1, 2, 0)  # Convert from (channels, height, width) to (height, width, channels)
    image = np.uint8(image)  # Convert to unsigned byte format

    # Convert to PIL Image
    pil_image = Image.fromarray(image)

    # Convert to Byte Stream for uploading
    byte_stream = io.BytesIO()
    pil_image.save(byte_stream, format='JPEG')
    byte_stream.seek(0)

    blob.upload_from_file(byte_stream, content_type='image/jpeg')

    return blob.public_url

# upload image to storage
print(uploadImageFromPath('images/james.jpg', "test"))

