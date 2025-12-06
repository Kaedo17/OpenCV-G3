import cv2
import face_recognition

# 1. Load known face
known_image = face_recognition.load_image_file("person1.jpg")
known_encoding = face_recognition.face_encodings(known_image)[0]

# 2. Start camera
cap = cv2.VideoCapture(0)

# Wait a bit for camera to warm up
import time
time.sleep(2)

while True:
    # Read frame
    success, frame = cap.read()
    
    if not success:
        print("Failed to grab frame")
        break
    
    # Convert to RGB
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # Find faces
    face_locations = face_recognition.face_locations(rgb_frame)
    
    # Draw rectangles around all faces
    for (top, right, bottom, left) in face_locations:
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
        cv2.putText(frame, "Face", (left, top-10), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
    
    # Show frame
    cv2.imshow('Camera', frame)
    
    # Exit on 'q'
    if cv2.waitKey(1) == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()