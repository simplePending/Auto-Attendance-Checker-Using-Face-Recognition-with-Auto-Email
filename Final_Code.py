import serial
import cv2
import numpy as np
import face_recognition
import os
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from datetime import datetime

# Serial Port Configuration
serial_port = 'COM3'  # Change as needed
baud_rate = 9600
ser = serial.Serial(serial_port, baud_rate)

# Email Credentials
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
SMTP_USERNAME = 'yanmakanedez@gmail.com'  # Change email to use
SMTP_PASSWORD = 'ndag okyj jfdk ytsv'  # App password

# Student Data (UID to Name Mapping)
student_names = {
    "FC1E24": "Borja_Francine",
    "D6004": "Garcia_Leah",
    "A491422": "Kim_Sto_Domingo",
    "4B2F04": "Leinier_Rufino",
    "966D24": "Lian_Grace_D_Salonga",
    "B4B114": "Michaela_Chlouie_Mendoza",
    "E36224": "Miles_Dustin_Pingol"
}

# Parent Email Mapping
email_map = {
    "Borja_Francine": "francineborja211526@gmail.com",
    "Garcia_Leah": "ciervacharlesmarius02@gmail.com",
    "Kim_Sto_Domingo": "anedezryan@gmail.com",
    "Leinier_Rufino": "malanamaryjoy346@gmail.com",
    "Lian_Grace_D_Salonga": "anedezryanmark502@gmail.com",
    "Michaela_Chlouie_Mendoza": "malanamaryjoy346@gmail.com",
    "Miles_Dustin_Pingol": "anedezryanmark502@gmail.com"
}

# Load Training Images for Face Recognition
path = 'Training_images'
if not os.path.exists(path):
    os.makedirs(path)

encoded_faces = []
classNames = []

for person in os.listdir(path):
    person_path = os.path.join(path, person)
    if os.path.isdir(person_path):
        for filename in os.listdir(person_path):
            img_path = os.path.join(person_path, filename)
            img = face_recognition.load_image_file(img_path)
            encodings = face_recognition.face_encodings(img)
            if encodings:
                encoded_faces.append(encodings[0])
                classNames.append(person.strip())

# Function to Send Email Notification
def send_email(name):
    name_key = name.strip()
    recipient = email_map.get(name, "anedezryanmark502@gmail.com")
    subject = f"Attendance Alert: {name} is Present"
    body = f"Hello,\n\n{name} is present today.\n\nBest regards,\nAttendance System"

    message = MIMEText(body)
    message['Subject'] = subject
    message['From'] = SMTP_USERNAME
    message['To'] = recipient

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as smtp:
            smtp.starttls()
            smtp.login(SMTP_USERNAME, SMTP_PASSWORD)
            smtp.sendmail(SMTP_USERNAME, recipient, message.as_string())
        print(f"✅ Email sent to {recipient} for {name_key}")
    except Exception as e:
        print(f"Email error: {e}")

# Function to Record Attendance
def mark_attendance(name, Student_ID="Unknown"):
    filename = 'Attendance.xlsx'  # Retrieve the data
    today_date = datetime.now().strftime('%Y-%m-%d')

    if os.path.exists(filename):
        df = pd.read_excel(filename)
    else:
        df = pd.DataFrame(columns=['Name', 'Date', 'Time', 'Student_ID'])

    if not ((df['Name'] == name) & (df['Date'] == today_date)).any():
        dtString = datetime.now().strftime('%H:%M:%S')
        df = pd.concat([df, pd.DataFrame([[name, today_date, dtString, Student_ID]], columns=['Name', 'Date', 'Time', 'Student_ID'])], ignore_index=True)
        df.to_excel(filename, index=False)
        print(f"✅ Attendance marked: {name} at {dtString} with Student ID: {Student_ID}")
        send_email(name)
    else:
        print(f"⚠️ {name} already marked present today.")

# Open Webcam for Face Recognition
cap = cv2.VideoCapture(0)

print("Waiting for RFID scan or face recognition...")

while True:
    # Check for RFID Input
    if ser.in_waiting > 0:
        student_ID = ser.readline().decode('utf-8').strip().upper()
        student_Name = student_names.get(student_ID, "Unknown")
        print(f"RFID: {student_ID} | Name: {student_Name}")
        if student_Name != "Unknown":
            mark_attendance(student_Name, student_ID)

    # Capture Webcam Frame
    success, img = cap.read()
    if not success:
        continue
    
    imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)
    
    facesCurFrame = face_recognition.face_locations(imgS)
    encodesCurFrame = face_recognition.face_encodings(imgS, facesCurFrame)
    
    for encodeFace, faceLoc in zip(encodesCurFrame, facesCurFrame):
        matches = face_recognition.compare_faces(encoded_faces, encodeFace)
        faceDis = face_recognition.face_distance(encoded_faces, encodeFace)
        
        if len(faceDis) > 0:
            matchIndex = np.argmin(faceDis)
            if matches[matchIndex]:
                name = classNames[matchIndex]
                mark_attendance(name)
                y1, x2, y2, x1 = [val * 4 for val in faceLoc]
                cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(img, name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)
    
    cv2.imshow('Webcam', img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
