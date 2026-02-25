import smtplib, ssl
from email.message import EmailMessage
import requests
import requests

from email.parser import Parser
from email.policy import default
import time
# Email credentials and content

# send the email in form of html to make it fancy and colorful, with the water level state in red if low and green if high




url = "http://192.168.0.50:8123/api/states/binary_sensor.water_level_sensor"

headers = {
"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiIwMzYwZTc0ODMwNTQ0ZDU4OTgzM2RhZmJjMmRiN2NmMSIsImlhdCI6MTc3MDIzNjE3MSwiZXhwIjoyMDg1NTk2MTcxfQ.Vpa3tkUpx7loaFfCqHiGTbbo68-OdiiSmjOiJpwbxdo",
"Content-Type": "application/json",
}

leak_detected = False

print(f"Starting to monitor water level sensor...")

while not leak_detected:
    resp = requests.get(url, headers=headers)
    if resp.json()['state'] == 'on':
        leak_detected = True
        break
    wait_time_seconds = 60
    time.sleep(1)

smtp_server = "smtp.gmail.com"
port = 465  # For SSL
sender_email = "csugreenhouse@gmail.com"  # Enter your address
receiver_email = "carv@colostate.edu, kai.brennan@colostate.edu, chuck@media-systems.com"  # Enter receiver address
app_password = "ssrl ohkt qvjt huhe" # Use the password you copied from Google
subject = "TEST EMAIL"

# if wate4r level sensor is low, send an email with red letters of LOW
# if water level sensor is high, send an email with green letters of HIGH  
# send red letter in an email

body = f"Hello! This is the water level sensor email \n \
Water level sensor state: {resp.json()['state']} \n \
This means that water level is {'LOW' if resp.json()['state'] == 'on' else 'HIGH'} \n \
This email was sent because the water level sensor in the greenhouse detected a low state \n \
From now on, if you see this email, it means that the water level is low"

# Create a secure SSL context
context = ssl.create_default_context()

# Create the email message
msg = EmailMessage()
msg.set_content(body)
msg['Subject'] = subject
msg['From'] = sender_email
msg['To'] = receiver_email




#print(resp.json())

try:
    # Connect to the server and send the email
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(sender_email, app_password)
        server.send_message(msg)
    print("Email sent successfully!")

except Exception as e:
    print(f"An error occurred: {e}")
