import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

sender_email = "example@gmail.com"
password = "Password"


def Function_name(receiver_email):
    message = MIMEMultipart("alternative")
    message["Subject"] = ""
    message["From"] = sender_email
    message["To"] = receiver_email

    # Create the plain-text and HTML version of your message
    text = """\
    
        Hi, There
        With a Hope that you are doing great


        Team, PassManager"""
    html = """\
        <html>
            

        <body>
            
            <nav class="navbar">
        <a href="/">
            <h1 class="title">
            Pass Manager
            </h1>
        </a>
        


        </nav>
            <div >
                
        <div class="Home">
            <div class="intro-A">
                <div class="c1">
                    <h1 class='H-title'>Hi, There</h1>
                    <hr>
                    <p>
                        With a Hope that you are doing great
                    </p>
                    



                    <h5 style='padding-top: 5vh;'>Team, PassManager</h5>
                </div>

                
        </div>


        </div>

        </body>

        </html>
        """

    # Turn these into plain/html MIMEText objects
    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")

    # Add HTML/plain-text parts to MIMEMultipart message
    # The email client will try to render the last part first
    message.attach(part1)
    message.attach(part2)

    # Create secure connection with server and send email
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(
            sender_email, receiver_email, message.as_string()
        )
