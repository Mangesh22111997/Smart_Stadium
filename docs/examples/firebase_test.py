#Install these
#!pip install  pyrebase4

import pyrebase

import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

firebaseConfig = {
  'apiKey': os.getenv("FIREBASE_API_KEY"),
  'authDomain': os.getenv("FIREBASE_AUTH_DOMAIN"),
  'databaseURL': os.getenv("FIREBASE_DATABASE_URL"),
  'projectId': os.getenv("FIREBASE_PROJECT_ID"),
  'storageBucket': os.getenv("FIREBASE_STORAGE_BUCKET"),
  'messagingSenderId': os.getenv("FIREBASE_MESSAGING_SENDER_ID"),
  'appId': os.getenv("FIREBASE_APP_ID"),
  'measurementId': os.getenv("FIREBASE_MEASUREMENT_ID")
}

firebase = pyrebase.initialize_app(firebaseConfig)

# Now you can use:
db = firebase.database()
auth = firebase.auth()
storage = firebase.storage()

# Example: Write data
data = {"name": "Test User", "email": "test@example.com"}
db.child("users").push(data)

# Example: Read data
users = db.child("users").get()
for user in users.each():
    print(user.val())