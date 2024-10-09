import smtplib

import smtplib

try:
    # Testing TLS
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.set_debuglevel(1)
        server.starttls()
        server.login('shoileazeez@gmail.com', 'likemerun')
        print("SMTP connection successful on port 587!")
    
    # Testing SSL
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.set_debuglevel(1)
        server.login('shoabdulazeez@gmail.com', 'alnehnrgkgxgwmmz')
        print("SMTP connection successful on port 465!")
except Exception as e:
    print(f"Failed to connect: {e}")

