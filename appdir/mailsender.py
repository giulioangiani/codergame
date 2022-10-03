## protection by login
from functools import wraps
import hashlib
import traceback
from config import mail_sender_config

def sendEmail(subject, message_body, receiver_address, cc=[], bcc=[], attachments=[]):

	from smtplib import SMTP
	from email.mime.multipart import MIMEMultipart
	from email.mime.text import MIMEText
	from email.mime.base import MIMEBase
	from email import encoders
	
	#The mail addresses and password
	
	sender_address = mail_sender_config["sender_address"]
	sender_pass = mail_sender_config["sender_pass"]
	

	#Setup the MIME
	message = MIMEMultipart()
	message['From'] = sender_address
	message['To'] = receiver_address
	addresses = [receiver_address]
	if cc:
		message['Cc'] = ",".join(cc)
		addresses += cc
	if bcc:
		message['Bcc'] = ",".join(bcc)
		addresses += bcc
	message['Subject'] = subject
	#The body and the attachments for the mail
	message.attach(MIMEText(message_body, 'plain'))
	
	for a in attachments:

		payload = MIMEBase('application', 'octate-stream', Name=a["filename"])
		payload.set_payload(a["content"])
		# enconding the binary into base64
		encoders.encode_base64(payload)
		# add header with pdf name
		payload.add_header('Content-Decomposition', 'attachment', filename=a["filename"])
		message.attach(payload)
		
	#Create SMTP session for sending the mail
	session = SMTP('smtp.gmail.com', 587) #use gmail with port
	session.starttls() #enable security
	session.login(sender_address, sender_pass) #login with mail_id and password
	text = message.as_string()
	try:
		session.sendmail(sender_address, addresses, text)
		result = True
	except:
		print(traceback.format_exc())
		result = False
	session.quit()
	return result


if __name__ == '__main__':
	sendEmail("test", "prova di messaggio", "giulio.angiani@gmail.com", cc=['giulio.angiani@iispascal.it'], attachments=[])

