import firebase_admin

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

# upload image to storage
print(uploadImageFromPath('images/james.jpg', "test"))
