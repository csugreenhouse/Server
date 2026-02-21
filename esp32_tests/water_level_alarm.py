import requests

from email.parser import Parser
from email.policy import default

headers = Parser(policy=default).parsestr(
        'From: Foo Bar <gre.com>\n'
        'To: <someone_else@example.com>\n'
        'Subject: Test message\n'
        '\n'
        'Body would go here\n')

print('To: {}'.format(headers['to']))
print('From: {}'.format(headers['from']))
print('Subject: {}'.format(headers['subject']))

# You can also access the parts of the addresses:
print('Recipient username: {}'.format(headers['to'].addresses[0].username))
print('Sender name: {}'.format(headers['from'].addresses[0].display_name))


url = "http://192.168.0.50:8123/api/states/binary_sensor.water_level_sensor"
headers = {
"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiIwMzYwZTc0ODMwNTQ0ZDU4OTgzM2RhZmJjMmRiN2NmMSIsImlhdCI6MTc3MDIzNjE3MSwiZXhwIjoyMDg1NTk2MTcxfQ.Vpa3tkUpx7loaFfCqHiGTbbo68-OdiiSmjOiJpwbxdo",
"Content-Type": "application/json",
}

resp = requests.get(url, headers=headers)


print(resp.json())