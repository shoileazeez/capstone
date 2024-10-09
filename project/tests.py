import smtplib
from email.mime.text import MIMEText
msg = MIMEText('Test email content.')
msg['Subject'] = 'Test Email'
msg['From'] = 'shoabdulazeez@gmail.com'
msg['To'] = 'shoileazeez@gmail.com'

server = smtplib.SMTP('smtp.mailjet.com', 587)
server.starttls()
server.login('852682e567c3e6efefd9f068e2055d05', '7b9f97f56f018f24b433228ba33738cb')
server.sendmail(msg['From'], [msg['To']], msg.as_string())
server.quit()


from django.core.mail import send_mail
from django.conf import settings

def send_test_email():
    try:
        send_mail(
            'Test Subject',  # Subject
            'Here is the message.',  # Message body
            settings.DEFAULT_FROM_EMAIL,  # From email
            ['shoileazeez.com'],  # To email
            fail_silently=False,
        )
        print("Email sent successfully!")
    except Exception as e:
        print(f"Error sending email: {e}")

if __name__ == "__main__":
    send_test_email()