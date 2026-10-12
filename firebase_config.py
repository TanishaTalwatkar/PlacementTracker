import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

# Load Firebase private key
cred = credentials.Certificate("firebase_key.json")

# Connect Python with Firebase
firebase_admin.initialize_app(cred)

# Create Firestore database connection
db = firestore.client()