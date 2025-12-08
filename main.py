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

    # Display "NO FACE DETECTED" if no faces are found
    if len(face_locations) == 0:
        # Display message in the center of the screen
        height, width = frame.shape[:2]
        text = "NO FACE DETECTED"
        font = cv2.FONT_HERSHEY_DUPLEX
        font_scale = 1.0
        thickness = 2
        
        # Get text size
        (text_width, text_height), baseline = cv2.getTextSize(text, font, font_scale, thickness)
        
        # Calculate position (center of screen)
        text_x = (width - text_width) // 2
        text_y = (height + text_height) // 2
        
        # Draw semi-transparent background rectangle
        padding = 10
        cv2.rectangle(frame, 
                     (text_x - padding, text_y - text_height - padding), 
                     (text_x + text_width + padding, text_y + padding), 
                     (0, 0, 0), -1)  # Black background
        cv2.rectangle(frame, 
                     (text_x - padding, text_y - text_height - padding), 
                     (text_x + text_width + padding, text_y + padding), 
                     (255, 255, 255), 2)  # White border
        
        # Draw the text
        cv2.putText(frame, text, (text_x, text_y), 
                   font, font_scale, (255, 255, 255), thickness)
        
        # Also show status in top center
        status_text = "WAITING FOR FACE..."
        status_font_scale = 0.7
        (status_width, _), _ = cv2.getTextSize(status_text, font, status_font_scale, 1)
        status_x = (width - status_width) // 2
        cv2.putText(frame, status_text, (status_x, 40), 
                   font, status_font_scale, (255, 165, 0), 1)  # Orange color
    
    # If faces are found, process them
    else:
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

    # Display system info
    info_text = f"Known Faces: {len(known_names)} | Detected: {len(face_locations)}"
    cv2.putText(frame, info_text, (10, 30), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
    
    # Display instruction
    cv2.putText(frame, "Press 'Q' to quit", (10, frame.shape[0] - 10), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

    # Display resulting image
    cv2.imshow('GateKeeper - Live Face Verification System', frame)

    # Exit on 'q'
    if cv2.waitKey(1) == ord('q'):
        break

# Release handle to the webcam
video_capture.release()
cv2.destroyAllWindows()