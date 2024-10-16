# import smtplib
# from email.mime.text import MIMEText
# msg = MIMEText('Test email content.')
# msg['Subject'] = 'Test Email'
# msg['From'] = 'shoabdulazeez@gmail.com'
# msg['To'] = 'shoileazeez@gmail.com'

# server = smtplib.SMTP('smtp.mailjet.com', 587)
# server.starttls()
# server.login('852682e567c3e6efefd9f068e2055d05', '7b9f97f56f018f24b433228ba33738cb')
# server.sendmail(msg['From'], [msg['To']], msg.as_string())
# server.quit()


# from django.core.mail import send_mail
# from django.conf import settings

# def send_test_email():
#     try:
#         send_mail(
#             'Test Subject',  # Subject
#             'Here is the message.',  # Message body
#             settings.DEFAULT_FROM_EMAIL,  # From email
#             ['shoileazeez.com'],  # To email
#             fail_silently=False,
#         )
#         print("Email sent successfully!")
#     except Exception as e:
#         print(f"Error sending email: {e}")

# if __name__ == "__main__":
#     send_test_email()




# import boto3                                                          
# from django.conf import settings

# import boto3

# s3 = boto3.client('s3', 
#                   aws_access_key_id=settings.AWS_ACCESS_KEY_ID, 
#                   aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
#                   region_name=settings.AWS_S3_REGION_NAME)
# response = s3.list_buckets()

# for bucket in response['Buckets']:
#     print(bucket['Name'])

# import boto3
# from botocore.exceptions import NoCredentialsError, ClientError

# # AWS S3 configuration
# bucket_name = 'elasticbeanstalk-eu-north-1-445567114681'
# file_name = 'media/uploads/test.txt'   # Replace with the path to your local file
# s3_file_name = 'me'    # The name of the file when it will be uploaded to S3

# # Initialize S3 client
# s3 = boto3.client('s3')

# # Function to upload file
# def upload_file_to_s3(file_name, bucket, s3_file_name):
#     try:
#         # Upload the file
#         s3.upload_file(file_name, bucket, s3_file_name)
#         print(f"File '{file_name}' uploaded to S3 bucket '{bucket}' as '{s3_file_name}'")
#     except FileNotFoundError:
#         print("The file was not found")
#     except NoCredentialsError:
#         print("Credentials not available")
#     except ClientError as e:
#         print(f"Error: {e}")

# # Upload the file
# upload_file_to_s3(file_name, bucket_name, s3_file_name)


# import os
# import sys

# # Add the project directory to the Python path
# sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# import django
# import boto3

# # Set the DJANGO_SETTINGS_MODULE environment variable
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'commerce_api.settings')

# # Set up Django
# django.setup()

# # Import settings
# from django.conf import settings

# # Initialize the S3 client
# s3 = boto3.client(
#     's3',
#     aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
#     aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
#     region_name=settings.AWS_S3_REGION_NAME
# )

# # File upload details
# file_name = 'media/uploads/test.txt'  # Path to your local file
# bucket_name = settings.AWS_STORAGE_BUCKET_NAME  # Your S3 bucket name
# s3_file_name = 'uploads/test.txt'  # Desired S3 file name

# # Upload file to S3
# try:
#     s3.upload_file(file_name, bucket_name, s3_file_name)
#     print("File uploaded successfully.")
# except Exception as e:
#     print(f"Failed to upload file: {e}")
