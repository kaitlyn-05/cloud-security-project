#################################
# name: josh ramachandran
# date: 4/12/2025
# desc: face detection program using Haar cascades
#################################

import cv2

def count_faces(frame):
    """
    Detects faces in the given frame and returns the count.
    :param frame: The input frame (image) in which to detect faces.
    :return: Number of faces detected in the frame.
    """
    # Load the pre-trained Haar Cascade classifier
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    
    # Convert the frame to grayscale
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Detect faces in the frame
    faces = face_cascade.detectMultiScale(gray_frame, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
    
    # Return the number of faces detected
    return len(faces)

# Main program to test the function
if __name__ == "__main__":
    video_capture = cv2.VideoCapture(0)

    while True:
        # Capture frame-by-frame
        ret, frame = video_capture.read()
        
        # Use the function to count faces
        face_count = count_faces(frame)
        print(f"Number of faces detected: {face_count}")

        # Draw rectangles around the faces
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray_frame, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
        
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
        
        # Display the resulting frame
        cv2.imshow('Video', frame)

        # Break the loop with 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release the webcam and close the window
    video_capture.release()
    cv2.destroyAllWindows()




# import cv2
# from time import sleep
# # Load the pre-trained Haar Cascade classifier
# face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

# # Initialize the webcam
# video_capture = cv2.VideoCapture(0)

# while True:
#     # Capture frame-by-frame
#     ret, frame = video_capture.read()
#     gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

#     # Detect faces in the frame
#     faces = face_cascade.detectMultiScale(gray_frame, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

#     # Count the number of faces detected
#     face_count = len(faces)
#     print(f"Number of faces detected: {face_count}")
#     sleep(5)
#     # Draw rectangles around the faces
#     for (x, y, w, h) in faces:
#         cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)

#     # Display the resulting frame
#     cv2.imshow('Video', frame)

#     # Break the loop with 'q'
#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break

# # Release the webcam and close the window
# video_capture.release()
# cv2.destroyAllWindows()


# import numpy as np
# import cv2

# # Load the Haar Cascade classifier for face detection
# face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# cap = cv2.VideoCapture(0)  # You can replace 0 with a video file name if needed

# while True:
#     ret, frame = cap.read()
#     if not ret:
#         break

#     # Convert frame to grayscale for face detection
#     gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

#     # Detect faces
#     faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

#     # Draw rectangles around detected faces
#     for (x, y, w, h) in faces:
#         cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

#     # Show the frame
#     cv2.imshow('Face Detection', frame)

#     if cv2.waitKey(1) == ord('q'):
#         break

# cap.release()
# cv2.destroyAllWindows()
