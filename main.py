import cv2
import face_recognition
import os
import numpy as np

# Load the reference database
folder_path = "images"
known_faces = []
known_names = []

print(f"--- 📂 LOADING REFERENCE IMAGES FROM '{folder_path}' ---")

# If folder is not located
if not os.path.exists(folder_path):
    print(f"CRITICAL ERROR: Folder '{folder_path}' does not exist.")
    exit()

# Loop through all the files in the folder
for filename in os.listdir(folder_path):
    full_path = os.path.join(folder_path, filename)

    # Verify if files are images
    if not filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
        continue

    # Load the image
    image = face_recognition.load_image_file(full_path)

    # Try block to encode the face
    try:
        encoding = face_recognition.face_encodings(image)[0]

        # Add to known faces
        known_faces.append(encoding)

        # Use filename without image extension for names
        name = os.path.splitext(filename)[0]
        known_names.append(name)

        print(f"\n✅ Learned Face: {name}")
    except IndexError:
        print(f"⚠️ Warning: No face found in {filename}. Skipping.")

print(f"\n--- DATABASE LOADED {len(known_names)} PEOPLE ---")
print(f"\nStarting Camera...")

# Start of camera verification
video_capture = cv2.VideoCapture(0)

while True:
    # Grab a single frame of video
    ret, frame = video_capture.read()
    if not ret:
        print(f"Error: Camera not found.")
        break

    # Resize frame of video for optimization
    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

    # Convert image from BGR to RGB
    rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

    # Find all the faces and face encodings in the current frame
    face_locations = face_recognition.face_locations(rgb_small_frame)
    face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

    face_names = []

    # Loop through each face found in the camera
    for face_encoding in face_encodings:
        
        # Default name
        name = "Unknown"
        
        # Calculate distances to known faces to find the BEST match
        # (This logic was missing in your original code)
        if len(known_faces) > 0:
            face_distances = face_recognition.face_distance(known_faces, face_encoding)
            best_match_index = np.argmin(face_distances)
            
            # If the distance is close enough (optional threshold logic), use the name
            matches = face_recognition.compare_faces(known_faces, face_encoding)
            if matches[best_match_index]:
                name = known_names[best_match_index]

        face_names.append(name)

    # Display the results
    for (top, right, bottom, left), name in zip(face_locations, face_names):

        # Scale up face locations
        top *= 4
        right *= 4
        bottom *= 4
        left *= 4

        # Access Text
        if name != "Unknown":
            # If it IS a known person
            status_text = f"ACCESS GRANTED"
            color = (0, 255, 0) # Green
        else:
            # If it is NOT known
            status_text = "ACCESS DENIED"
            color = (0, 0, 255) # Red
        
        # Draw the box around the face
        cv2.rectangle(frame, (left, top), (right, bottom), color, 2)

        # Draw the Status Text ABOVE the head
        cv2.putText(frame, status_text, (left - 20, top - 20), 
                    cv2.FONT_HERSHEY_DUPLEX, 0.7, color, 2)

        # Draw the Name Label BELOW the face
        cv2.rectangle(frame, (left, bottom - 35), (right, bottom), color, cv2.FILLED)
        cv2.putText(frame, name, (left + 6, bottom - 6), 
                    cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 255, 255), 1)


    # Display resulting image
    cv2.imshow('Live Verification System', frame)

    # Exit on 'q'
    if cv2.waitKey(1) == ord('q'):
        break

# Release handle to the webcam
video_capture.release()
cv2.destroyAllWindows()