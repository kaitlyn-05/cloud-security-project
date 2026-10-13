#Imports
import requests
from time import sleep
from picamera2 import Picamera2
import os
#Debug variable
DEBUG = False

# Specify the Flask server URL(has it be changed each tile server is initalized)
url = "http://138.47.249.76:8000/update-room/IESB%20111"  

# Initialize the Pi Camera
camera = Picamera2()
camera.start()

#Try to send the photo to the server with out throwing an error
try:
    while True:
        # Capture an image
        temp_filename = "temp_photo.jpg"
        camera.capture_file(temp_filename)  # Capture image and save to temporary file that is deleteted when teh program stops running
        

        # Open the file and send it in a POST request and receives info about the time until the next picture and room data for debug purposes 
        with open(temp_filename, "rb") as file:
            files = {"photo": file}
            response = requests.post(url, files=files)
            resp = dict(response.json())
        #Debugging if statement
        if DEBUG:
            print(resp)
            runm = input('press enter to run again or enter "q" to exit')
            if runm == "q":
                break
        else:
            # Pause for a few seconds before capturing the next photo
            sleep(resp['sleeptime'])  # Adjust the delay based for server response from the photo

finally:
    # close the camera and delete the image
    camera.close()
    if os.path.exists(temp_filename):
        os.remove(temp_filename)  # Remove the temporary file