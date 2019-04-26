

import time #Import time to peform delay operations
import requests #use requests to send mail via webhooks IFTTT
from boltiot import Bolt #Import boliot to control GPIO pins through API
import smtplib
import twilio
import twilio.rest
from string import Template

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

MY_ADDRESS = 'venkat.pushpak5@gmail.com'
PASSWORD = 'gollamudi@9410!!!'
api_key = "44ba6067-0765-4dae-a638-64841a8ee998" #Get your API key from Blot Cloud Website
device_id  = "BOLT11691861" #Get your Bolt device ID form Bolt Cloud Website
mybolt = Bolt(api_key, device_id)

HIGH = '{"value": "1", "success": "1"}' #This will be returned by bolt API if digital read is high
LOW = '{"value": "0", "success": "1"}'#This will be returned by bolt API if digital read is low

alarm = 0 #Alarm is turned off by default

def get_contacts(filename):
    """
    Return two lists names, emails containing names and email addresses
    read from a file specified by filename.
    """

    names = []
    emails = []
    with open(filename, mode='r') as contacts_file:
        for a_contact in contacts_file:
            names.append(a_contact.split()[0])
            emails.append(a_contact.split()[1])
    return names, emails

def read_template(filename):
    """
    Returns a Template object comprising the contents of the
    file specified by filename.
    """

    with open(filename, 'r') as template_file:
        template_file_content = template_file.read()
    return Template(template_file_content)


def SendMail():
    names, emails = get_contacts('name1.txt') # read contacts
    message_template = read_template('message.txt')

    # set up the SMTP server
    s = smtplib.SMTP(host='smtp.gmail.com', port=587)
    print(s)
    s.starttls()
    s.login(MY_ADDRESS, PASSWORD)

    # For each contact, send the email:
    for name, email in zip(names, emails):
        msg = MIMEMultipart()       # create a message

        # add in the actual person name to the message template
        message = message_template.substitute(PERSON_NAME=name.title())

        # Prints out the message body for our sake
        print("msg is"+message)

        # setup the parameters of the message
        msg['From']=MY_ADDRESS
        msg['To']=email
        msg['Subject']="This is TEST"

        # add in the message body
        msg.attach(MIMEText(message, 'plain'))

        # send the message via the server set up earlier.
        s.send_message(msg)
        del msg

    # Terminate the SMTP session and close the connection
    s.quit()

def SendMessage():
    account_sid = 'ACc85b615ebcfeb6b24b2646f5cd883338'
    auth_token = '0deac459493fa4bfede8fd4a3fb21046'
    client = twilio.rest.Client(account_sid, auth_token)

    message = client.messages \
        .create(
             body='There has been a breach in your house.',
             from_='+12563872330',#this remains the same
             to='+16695006489' #keep your phone number here
         )


while True: #Infinite loop
    while alarm == 0: #If alarm is off
        response = mybolt.digitalRead('3') #check if it is being activated
        if (response == HIGH):
            print("Security System is activated")
            mybolt.digitalWrite('2', 'HIGH') #Turn on LED to indicate Aalarm is activated
            mybolt.digitalWrite('4', 'LOW')
            alarm = 1
        elif (response == LOW):
            print ("Waiting for Security System to be activated....")
        else:
            print ("Probelm in getting value from pin 3")
        time.sleep(5) #check once in every 5 seconds to avoid exceeding API rate lmit


    while alarm == 1: #If alarm is on
        response = mybolt.digitalRead('4') #check is it is being de-activated
        if (response == HIGH):
            print("Security System is De-activated")
            mybolt.digitalWrite('2', 'LOW')#Turn off LED to indicate Aalarm is De-activated
            mybolt.digitalWrite('3', 'LOW')
            alarm = 0
            time.sleep(5)
        elif (response == LOW):
            print ("Security System is currently active can be deactivated from google assistant")
        else:
            print ("Probelm in getting value from pin 4")

        response = mybolt.digitalRead('0') #check if hall sensor is triggered
        if (response == HIGH): #if magnet is not present
            print ("Alert! Security breach Buzzer ON")
            mybolt.digitalWrite('1', 'HIGH')
            #requests.get('https://maker.ifttt.com/trigger/Breach/with/key/oGj-rHIq8Re7g7tbmQg5Vxkbr7v5_qEd1QGOskUOtql') #webhook link to trigger mail through IFTTT
            #time.sleep(5)
            SendMail()
            SendMessage()
            mybolt.digitalWrite('1', 'LOW')
            print ("Buzzer OFF")
        elif (response == LOW):
            print ("No problem, all good!")
        else:
            print ("Problem in reading the value of button")
        time.sleep(5)
