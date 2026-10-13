#Imports 
from flask import Flask, request, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from detectionTest import count_faces
import os
import cv2
from werkzeug.utils import secure_filename
from time import sleep, time
app = Flask(__name__, template_folder = "templetes")

#Align app with CORS regulations
CORS(app)


# Configure database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define the table structure
class RoomData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    room_number = db.Column(db.String(100), nullable=False)
    available = db.Column(db.String(100), nullable=False)
    checkcount = db.Column(db.Integer)

# Create the database table
with app.app_context():
    db.create_all()

# Route to handle form submission
@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        room_number = request.form["roomNumber"]
        available = request.form["available"]

        # Create a new record
        new_data = RoomData(room_number=room_number, available=available, checkcount=0)
        db.session.add(new_data)
        db.session.commit()

        return "Data added to database!"

    return render_template("index.html")
#Route to handle sumisiion of room data
@app.route("/submit", methods=["POST"])
def submit_data():
    room_number = request.form.get("roomNumber")
    available = request.form.get("available")

    if room_number and available:
        try:
            new_entry = RoomData(room_number=room_number, available=available, checkcount=0)
            db.session.add(new_entry)
            db.session.commit()
            return render_template("submit.html", success=True)
        except Exception as e:
            print(f"Error: {e}")
            return render_template("submit.html", success=False)
    else:
        return render_template("submit.html", success=False)

#Route that handles the Wytr room's availablility
@app.route("/wyly-room")
def wyly_room():
    # Filter records where room_number starts with 'WYTR'
    filtered_data = RoomData.query.filter(RoomData.room_number.like("WYTR%")).all()
    return render_template("wyly_room.html", data=filtered_data)

# Route to display submitted data
@app.route("/view-data")
def view_data():
    # Filter records where room_number starts with 'IESB'
    filtered_data = RoomData.query.filter(RoomData.room_number.like("IESB%")).all()
    return render_template("view_data.html", data=filtered_data)

#route to clear data if large amount of rooms have changed
@app.route("/clear-data")
def clear_data():
    try:
        # Delete all records in the RoomData table
        num_deleted = RoomData.query.delete()
        db.session.commit()
        return render_template("clear_data.html", success=True, num_deleted=num_deleted)
    except Exception as e:
        return render_template("clear_data.html", success=False, error=str(e))

#route to handle if room becomes avalible or not based off if it sees a person and when it last saw one and required constants
UPLOAD_FOLDER = 'uploads'  # Directory where uploaded images are stored
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/update-room/<room_number>", methods=["POST"])
def update_room(room_number=None):
    room = RoomData.query.filter_by(room_number=room_number).first()

    if not room:
        return jsonify({"success": False, "error_message": f"No room found with room number {room_number}."}), 404

    # Check if the file is in the request
    if "photo" not in request.files:
        return jsonify({"success": False, "error_message": "No file uploaded."}), 400

    file = request.files["photo"]

    if file.filename == '':
        return jsonify({"success": False, "error_message": "No file selected."}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Process the uploaded image
        frame = cv2.imread(filepath)
        face_count = count_faces(frame)
        is_available = "Not Available" if face_count > 0 else "Available"
        
        #updating database based off previous update and last tim eit got that same response 
        if is_available == "Available":
            if room.available == "Not Available" and room.checkcount < 3:
                room.checkcount += 1
                db.session.commit()
                return jsonify({"sleeptime" : 30, "Current DB" : room.available, "see me" : is_available})
            else:
                room.checkcount = 0
                room.available = str(is_available)
                db.session.commit()
                return jsonify({"sleeptime" : 5, "CurrentDB" : room.available, "see me" : is_available})
        
        if is_available == "Not Available":
            if room.available == "Available" and room.checkcount < 3:
                room.checkcount += 1
                db.session.commit()
                return jsonify({"sleeptime" : 1, "CurrentDB" : room.available, "see me" : is_available})
            else:
                room.checkcount = 0
                room.available = str(is_available)
                db.session.commit()
                return jsonify({"sleeptime" : 120, "CurrentDB" : room.available, "see me" : is_available})
                
            
    return jsonify({"success": False, "error_message": "Invalid file type. Please upload a PNG, JPG, or JPEG file."}), 400

#ruote that renders home template
@app.route("/sudo")
def sudo():
    return render_template("home.html")

#defines server host and accesible ips
if __name__ == '__main__':
    app.run(debug=False, host = "0.0.0.0", port = "8000")