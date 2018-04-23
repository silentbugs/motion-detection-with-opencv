import os
import json
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email import Encoders

conf = json.load(open('conf.json'))

gmail_username = conf['mail']['gmail_username']
gmail_password = conf['mail']['gmail_password']


def send_email(to, subject, body, attachment=None):
    msg = MIMEMultipart()

    msg['From'] = gmail_username
    msg['To'] = to
    msg['Subject'] = subject

    msg.attach(MIMEText(body))

    if attachment:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(open(attachment, 'rb').read())
        Encoders.encode_base64(part)
        part.add_header(
            'Content-Disposition',
            'attachment; filename="%s"' % os.path.basename(attachment)
        )
        msg.attachment(part)

    server_connect = False
    try:
        smtp_server = smtplib.SMTP_SSL('smtp.gmail.com', '465')
        smtp_server.login(gmail_username, gmail_password)
        server_connect = True
    except smtplib.SMTPHeloError as e:
        print 'Server did not reply'
    except smtplib.SMTPAuthenticationError as e:
        print 'Incorrect username/password combination'
    except smtplib.SMTPException as e:
        print 'Authentication failed'

    if server_connect:
        try:
            smtp_server.sendmail(gmail_username, [to], msg.as_string())
            print 'Successfully sent email'
        except smtplib.SMTPException as e:
            print 'Error: unable to send email', e
        finally:
            smtp_server.close()
