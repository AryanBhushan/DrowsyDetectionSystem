import streamlit as st
import cv2
import numpy as np
import imutils
from imutils import face_utils
import dlib
from datetime import datetime
import pandas as pd
import pygame
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import threading
from passlib.hash import pbkdf2_sha256
import sqlite3
import os


# Set the title of the browser tab
st.set_page_config(page_title="Driver Drowsiness Watch", page_icon="🚀")

# Initialize SQLite database
conn = sqlite3.connect("user_data.db")
cursor = conn.cursor()

# Create a table for user data
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL
    )
''')
conn.commit()

def create_user_table():
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS feedback_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL,
        feedback TEXT NOT NULL
    )
''')
conn.commit()

def add_feedback(name, email, feedback):
    cursor.execute('''
        INSERT INTO feedback_data (name, email, feedback) VALUES (?, ?, ?)
    ''', (name, email, feedback))
    conn.commit()

# Feedback Page
def feedback():
    st.title("Feedback Page")
    st.write(
        "We'd love to hear your feedback! Please fill out the form below:"
    )

    # Feedback form
    feedback_name = st.text_input("Your Name:")
    feedback_email = st.text_input("Your Email:")
    feedback_message = st.text_area("Feedback Message:")

    if st.button("Submit Feedback"):
        if feedback_name and feedback_email and feedback_message:
            add_feedback(feedback_name, feedback_email, feedback_message)
            st.success("Thank you for your feedback! It has been submitted successfully.")
        else:
            st.warning("Please fill in all fields before submitting feedback.")

# Creator Page
def creator():

    # Creator details
    creator_name =  "Aryan Bhushan" 
    creator_name1="Suyash Singh " 
    creator_name2="Shubham Paul "
    creator_name3="Palash Agarwal"
    creator_name4="Sarthak Sangral"     
    creator_email = "myprojects172@gmail.com"
    creator_github = "https://github.com/yourusername"
    creator_linkedin = "https://www.linkedin.com/in/yourusername"

    # Display creator details
    st.subheader("🌈 Creator Details:")
    st.text(f"👤 Name: {creator_name},{creator_name1},{creator_name2},{creator_name3},{creator_name4}")
    st.text(f"✉️ Email: {creator_email}")
   # st.text(f"🚀 GitHub: [GitHub/{creator_name}](creator_github)")
   # st.text(f"💼 LinkedIn: [LinkedIn/{creator_name}](creator_linkedin)")
    
    # Add a creative image or GIF
    st.image("data:image/jpeg;base64,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", use_column_width=True)

    # Add interactive buttons or links
    st.markdown("### 🌐 Connect with the Creator:")
    st.button("📧 Send an Email", on_click=email_creator)
   # st.button("🐦 Follow on Twitter", on_click=twitter_creator)

# Function to handle email button click
def email_creator():
    st.success("✉️ Email sent to the creator!")

# Function to handle Twitter button click
def twitter_creator():
    st.success("🐦 Followed the creator on Twitter!")

def add_user(username, password):
    hashed_password = pbkdf2_sha256.hash(password)
    cursor.execute('''
        INSERT INTO users (username, password) VALUES (?, ?)
    ''', (username, hashed_password))
    conn.commit()

def verify_user(username, password):
    cursor.execute('''
        SELECT password FROM users WHERE username=?
    ''', (username,))
    stored_password = cursor.fetchone()
    if stored_password and pbkdf2_sha256.verify(password, stored_password[0]):
        return True
    return False

def signup():
    st.title("Sign Up")
    username = st.text_input("Enter your username:")
    password = st.text_input("Enter your password:", type="password")
    confirm_password = st.text_input("Confirm your password:", type="password")

    if st.button("Sign Up"):
        if password == confirm_password:
            create_user_table()
            add_user(username, password)
            st.success("Successfully signed up. Please proceed to login.")
        else:
            st.error("Passwords do not match. Please try again.")


def login():
    st.title("Log In")
    username = st.text_input("Enter your username:")
    password = st.text_input("Enter your password:", type="password")

    if st.button("Log In"):
        create_user_table()
        if verify_user(username, password):
            # st.success("Successfully log in.")
            st.experimental_set_query_params(login_status=True)
            # st.experimental_rerun()

            return True
        else:
            st.error("Invalid username or password. Please try again.")
            return False


# Initialize pygame mixer
pygame.mixer.init()

# Load the alarm sound
alarm_sound = pygame.mixer.Sound('alert_sound.mp3')

# Load the shape predictor model
shape_predictor_path = "shape_predictor_68_face_landmarks.dat"
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(shape_predictor_path)

# Facial landmarks indices
(lstart, lend) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
(rstart, rend) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]
(mstart, mend) = face_utils.FACIAL_LANDMARKS_IDXS["mouth"]

# Constants for drowsiness detection
EAR_THRESHOLD = 0.3
CONSECUTIVE_FRAMES = 20
MAR_THRESHOLD = 14
ALARM_DURATION_THRESHOLD = 5  # Set the duration threshold for the alarm (in seconds)

ear_list = []  
mar_list = []
ts = []
count_sleep = 0
count_yawn = 0
FRAME_COUNT = 0
start_time = None  # Initialize start_time outside the loop

# Locks for thread safety
alarm_lock = threading.Lock()
email_lock = threading.Lock()

# Function to send email
def send_email():
    sender_email = "aryanbhushan20@gmail.com"  # Replace with your email address
    receiver_email = "myprojects172@gmail.com"  # Replace with the recipient's email address (palash.ag2003@gmail.com)
    password = "jbrm cnen cxtl thlc"  # Replace with your email password

    subject = "Drowsiness Alert!"
    body = f"The driver is drowsy. Please check immediately."

    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(sender_email, password)
        text = message.as_string()
        server.sendmail(sender_email, receiver_email, text)

# Function to play alarm sound
def play_alarm_sound():
    with alarm_lock:
        if not pygame.mixer.get_busy():
            alarm_sound.play()

def eye_aspect_ratio(eye):
    A = np.linalg.norm(eye[1] - eye[5])
    B = np.linalg.norm(eye[2] - eye[4])
    C = np.linalg.norm(eye[0] - eye[3])
    ear = (A + B) / (2.0 * C)
    return ear

def mouth_aspect_ratio(mouth):
    A = np.linalg.norm(mouth[13] - mouth[19])
    B = np.linalg.norm(mouth[14] - mouth[18])
    C = np.linalg.norm(mouth[15] - mouth[17])
    mar = (A + B + C) / 3.0
    return mar

# Function to get the script's directory
def get_script_directory():
    return os.path.dirname(os.path.realpath(__file__))

# Main video processing function
def process_video(video_option):
    global count_sleep, count_yawn, FRAME_COUNT, start_time
    if video_option == "Webcam":
        cap = cv2.VideoCapture(0)
    else:

        # Create a folder to store uploaded videos locally
        upload_folder = os.path.join(get_script_directory(), "uploaded_videos")
        os.makedirs(upload_folder, exist_ok=True)

        # File uploader
        uploaded_file = st.file_uploader("Upload a video file", type=["mp4", "avi", "mkv", "mov"])
        if uploaded_file is not None:
            # Save the uploaded file locally
            video_path = os.path.join(upload_folder, uploaded_file.name)
            with open(video_path, 'wb') as f:
                f.write(uploaded_file.read())

            # Read the video using OpenCV
            cap = cv2.VideoCapture(video_path)
        else:
            st.warning("Please upload a video file.")
            return

    button_key = "stop_button_" + str(hash(video_option))  
    video_placeholder = st.empty()
    stop_button = st.button("Stop Alarm", key=button_key)

    while True:
        ret, frame = cap.read()

        if ret:
            frame = imutils.resize(frame, width=500)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            rects = detector(gray, 1)

            for (i, rect) in enumerate(rects):
                shape = predictor(gray, rect)
                shape = face_utils.shape_to_np(shape)

                leftEye = shape[lstart:lend]
                rightEye = shape[rstart:rend]
                mouth = shape[mstart:mend]

                EAR = eye_aspect_ratio(leftEye + rightEye)
                MAR = mouth_aspect_ratio(mouth)

                ear_list.append(EAR)
                mar_list.append(MAR)
                ts.append(datetime.now().strftime('%H:%M:%S.%f'))

                if EAR < EAR_THRESHOLD:
                    FRAME_COUNT += 1
                    if FRAME_COUNT >= CONSECUTIVE_FRAMES:
                        if start_time is None:
                            start_time = datetime.now()
                        count_sleep += 1
                        cv2.putText(frame, "DROWSINESS ALERT!", (270, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

                        # Check if the threshold duration has been exceeded
                        if (datetime.now() - start_time).total_seconds() > ALARM_DURATION_THRESHOLD:
                            # location = get_location()  # Get current location
                            # timestamp = start_time.strftime('%Y-%m-%d %H:%M:%S.%f')
                            send_email()  # Send email when drowsiness is detected
                            play_alarm_sound()  # Play alarm sound when drowsiness is detected
                else:
                    FRAME_COUNT = 0
                    start_time = None

                if MAR > MAR_THRESHOLD:
                    count_yawn += 1
                    cv2.putText(frame, "DROWSINESS ALERT!", (270, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                    # play_alarm_sound()  # Play alarm sound when yawning is detected

                cv2.polylines(frame, [leftEye], True, (0, 255, 0), 1)
                cv2.polylines(frame, [rightEye], True, (0, 255, 0), 1)
                cv2.polylines(frame, [mouth], True, (0, 0, 255), 1)
                (x, y, w, h) = face_utils.rect_to_bb(rect)
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            video_placeholder.image(frame, channels="BGR", use_column_width=True)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            pygame.mixer.stop()  # Stop the sound when quitting
            break

        if start_time is not None and (datetime.now() - start_time).total_seconds() > ALARM_DURATION_THRESHOLD:
            # Ask user whether to close the sound
            # if st.button("Stop Alarm", key=button_key):
            if stop_button:
                pygame.mixer.stop()  # Stop the sound
            else:
                play_alarm_sound()  # Play the sound again
                start_time = datetime.now()

    cap.release()
    # df = pd.DataFrame({"EAR": ear_list, "MAR": mar_list, "TIME": ts})
    # st.line_chart(df.set_index("TIME"))

# if __name__ == '__main__':
#     video_option = st.sidebar.selectbox("Select video source", ["Webcam", "Video Upload"])
#     process_video(video_option)


def main():
    st.title("Driver Drowsiness Detection System")

    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Home", "Sign Up", "Log In", "Prediction", "Feedback", "Creator"])

    if page == "Home":
  
        st.write(
    "Welcome to the Driver Drowsiness Detection System!\n\n"
    "This system uses computer vision to monitor and detect driver drowsiness in real-time. It analyzes facial landmarks to identify signs of drowsiness, such as eye closure and yawning.\n\n"
    "### Key Features:\n"
    "- Real-time Drowsiness Detection\n"
    "- Email Notifications on Drowsiness Alert\n"
    "- Sound Alerts for Continuous Drowsiness\n"
    "- Send Alert Email\n"
    "- Drowsiness Analytics Dashboard\n\n"
    "### How it Works:\n"
    "The system continuously captures video frames, processes facial landmarks, and checks for drowsiness indicators. When drowsiness is detected, an alert is triggered. The system also provides detailed analytics on drowsiness events.\n\n"
    "### Get Started:\n"
    "To use the system, select your video source (Webcam or Video Upload) from the sidebar. The system will start monitoring for drowsiness, and you can view real-time alerts and analytics on the main screen.\n\n"
    "Ensure that you have the necessary dependencies installed before running the system."
    )

    elif page == "Sign Up":
        signup()
    elif page == "Log In":
        if login():
            st.success("You are now logged in.")
            st.experimental_set_query_params(login_status=True)
    elif page == "Prediction":
        if st.experimental_get_query_params().get('login_status'):
          
            video_option = st.sidebar.selectbox("Select video source", ["Video Upload", "Webcam"])
            process_video(video_option)
        else:
            st.warning("Please log in first to access the prediction page.")
    elif page == "Feedback":
        feedback()
    elif page == "Creator":
        creator()

if __name__ == '__main__':
    main()

