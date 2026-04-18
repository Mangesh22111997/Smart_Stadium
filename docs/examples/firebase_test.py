#Install these
#!pip install  pyrebase4

import pyrebase

firebaseConfig = {
  'apiKey': "AIzaSyCcanmGKxtXCawn0EML0bpL6LgmI1p2CiE",
  'authDomain': "smart-stadium-system-db.firebaseapp.com",
  'databaseURL': "https://smart-stadium-system-db-default-rtdb.asia-southeast1.firebasedatabase.app",
  'projectId': "smart-stadium-system-db",
  'storageBucket': "smart-stadium-system-db.firebasestorage.app",
  'messagingSenderId': "771554077981",
  'appId': "1:771554077981:web:2b627c9f72edb53a5245f4",
  'measurementId': "G-BBJBX9TCCH"
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