import re
import imaplib,email
import smtplib
import os
from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
from http.client import HTTPResponse
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from email.message import EmailMessage
from playsound import playsound
import docx2txt

# Local Files
from .models import Details
from .models import Compose
from .TalkandListen import talk
from .TalkandListen import listen
from .TalkandListen import save_audio

#User Email Address
email_address = ''
#User Email Password
email_password = ''

#Address To Send Email To
to_addresses = ''
#Subject to send to user
subject = ''
#Body to send to user
body = ''

#Gmail Server Connection Object
server = smtplib.SMTP('smtp.gmail.com', 587)
#Start The Server TLS For Security
server.starttls()
#Mail pointer of gmail to read the emails
mail = imaplib.IMAP4_SSL('imap.gmail.com')

#Convert Special Characters In String
def convert_special_char(text):
    temp = text
    special_chars = ['at', 'dot','underscore','dollar','hash','star','plus','minus','space','dash']
    for character in special_chars:
        while(True):
            pos=temp.find(character)
            if pos == -1:
                break
            else :
                if character == 'at':
                    temp=temp.replace('at','@')
                elif character == 'dot':
                    temp=temp.replace('dot','.')
                elif character == 'underscore':
                    temp=temp.replace('underscore','_')
                elif character == 'dollar':
                    temp=temp.replace('dollar','$')
                elif character == 'hash':
                    temp=temp.replace('hash','#')
                elif character == 'star':
                    temp=temp.replace('star','*')
                elif character == 'plus':
                    temp=temp.replace('plus','+')
                elif character == 'minus':
                    temp=temp.replace('minus','-')
                elif character == 'space':
                    temp = temp.replace('space', '')
                elif character == 'dash':
                    temp=temp.replace('dash','-')
    return temp

#Login Page Code
def login_view(request):
    global email_address, email_password, server, mail

    if request.method == 'POST':
        text1 = "Welcome to our Voice Based Email...... Login with your email account in order to continue. "
        talk(text1)
        flag = True
        while (flag):
            talk("Enter your Email")
            #email_address = 'voicebasedemailtest@gmail.com'
            if email_address != 'N':
                talk("You meant " + email_address + " say yes to confirm or no to enter again")
                say = listen()
                if say == 'yes' or say == 'Yes':
                    flag = False
            else:
                talk("could not understand what you meant:")
        email_address = email_address.strip()
        email_address = email_address.replace(' ', '')
        email_address = email_address.lower()
        email_address = convert_special_char(email_address)
        print(email_address)
        request.email = email_address

        flag = True
        while (flag):
            talk("Enter your password")
            #email_password = 'plqkmwoqcnfyswgq'
            if email_address != 'N':
                talk("You meant " + email_password + " say yes to confirm or no to enter again")
                say = listen()
                if say == 'yes' or say == 'Yes':
                    flag = False
            else:
                talk("could not understand what you meant:")
        email_password = email_password.strip()
        email_password = email_password.replace(' ', '')
        email_password = email_password.lower()
        email_password = convert_special_char(email_password)
        print(email_password)

        try:
            mail.login(email_address, email_password)
            server.login(email_address, email_password)
            talk("Congratulations. You have logged in successfully. You will now be redirected to the menu page.")
            return JsonResponse({'result' : 'success'})
        except Exception as e:
            print(e)
            talk("Invalid Login Details. Please try again.")
            return JsonResponse({'result': 'failure'})

    detail  = Details()
    detail.email = email_address
    detail.password = email_password
    return render(request, 'login.html', {'detail' : detail})

#Menu Page Code
def menu_view(request):
    global email_address, email_password
    if request.method == "POST":
        text1 = "Welcome To The Email Menu " + email_address + ". What Would You Like To Do ?"
        talk(text1)
        flag = True
        while(flag):
            talk("To compose an email say compose. To open Inbox folder say Inbox. To open Sent folder say Sent. To open trash folder say trash. To Logout say Logout. Do you want me to repeat?")
            say = listen()
            if say == "No" or say == "no":
                flag = False
            talk("What Do You Want To Do ?")
            action = listen()
            action = action.lower()
            if action == 'compose':
                return JsonResponse({'result' : 'compose'})
            elif action == 'inbox':
                return JsonResponse({'result' : 'inbox'})
            elif action == 'sent' or action == 'send':
                return JsonResponse({'result' : 'sent'})
            elif action == 'trash':
                return JsonResponse({'result' : 'trash'})
            elif action == 'logout':
                email_address = ""
                email_password = ""
                talk("You have been logged out of your account and now will be redirected back to the login page.")
                return JsonResponse({'result': 'logout'})
            else:
                talk("Invalid action. Please try again.")
                return JsonResponse({'result': 'failure'})
    return render(request, 'menu.html')

#Compose Page Code
def compose_view(request):
    global email_address, email_password, to_addresses, subject, body, server
    if request.method == "POST":
        text1 = "You have reached the Compose Email Page, where you can Compose and Send an Email"
        talk(text1)
        flag = True
        flag1 = True
        from_address = email_address
        to_address = list()
        while flag1:
            while flag:
                # Get Receiver
                talk('Hey ' + email_address +' ! To Whom You Want To Send An Email?')
                to = listen()
                if to != 'N':
                    print(to)
                    talk("You have said : " + to + ". Are you sure of this recipient ?")
                    say = 'yes'
                    if say == "Yes" or say == "yes":
                        to_address.append(to)
                        flag = False
                    else:
                        talk("Could Not Understand What You Meant")
            talk("Do you want to enter more recipients ?  Say yes or no.")
            say1 = 'no'
            if say1 == 'No' or say1 == 'no':
                flag1 = False
            flag = True

        new_to_addresses = list()
        for item in to_address:
            item = item.strip()
            item = item.replace(' ', '')
            item = item.lower()
            item = convert_special_char(item)
            new_to_addresses.append(item)
            print(item)

        # Get Subject
        flag = True
        while (flag):
            talk('What Is The Subject Of Your Email ?')
            subject = listen()
            if subject == 'N':
                talk("could not understand what you meant")
            else:
                talk("You have said : " + str(subject) + " Are you sure of this subject ?")
                say = listen()
                if say == "yes" or say == "Yes":
                    flag = False

        #Get Email Body
        flag = True
        while flag:
            talk("Tell Me The Text")
            body = listen()
            if body == "N":
                talk("Could Not Understand What You Meant")
            else:
                talk("This is your message." + body + "Are You Sure You Want To Send This?")
                say = listen()
                if say == "Yes" or say == "yes":
                    flag = False
        email = MIMEMultipart()
        email['From'] = email_address
        email['To'] = ",".join(new_to_addresses)
        email['Subject'] = subject
        email.attach(MIMEText(body, 'plain'))

        # Get Attachment
        talk('Any Attachment ? Say Yes or No')
        attach = listen()
        if attach == 'yes':
            talk("Do You Want To Record An Audio And Send As An Attachment ?")
            choice = 'yes'
            choice = choice.lower()
            if choice == 'yes':
                talk("Enter Filename.")
                filename = listen()
                filename = filename.lower()
                filename = filename + '.mp3'
                filename = filename.replace(' ', '')
                print(filename)
                talk("Enter Your Audio Message.")
                audio_msg = listen()
                flagconf = True
                while flagconf:
                    try:
                        save_audio(audio_msg, filename)
                        print("SAVED AUDIO")
                        flagconf = False
                    except:
                        print('Trying Again')
                attachment = open(filename, "rb")
                p = MIMEBase('application', 'octet-stream')
                p.set_payload((attachment).read())
                encoders.encode_base64(p)
                p.add_header('Content-Disposition', "attachment; filename= %s" % filename)
                email.attach(p)

            elif choice == 'no':
                talk("Enter Filename With Extension")
                filename = listen()
                filename = filename.strip()
                filename = filename.replace(' ', '')
                filename = filename.lower()
                filename = convert_special_char(filename)

                attachment = open(filename, "rb")
                p = MIMEBase('application', 'octet-stream')
                p.set_payload((attachment).read())
                encoders.encode_base64(p)
                p.add_header('Content-Disposition', "attachment; filename= %s" % filename)
                email.attach(p)

        try:
            server.sendmail(from_address, new_to_addresses, email.as_string())  # sender  to receiver via server.
            talk("Your email has been sent successfully. You will now be redirected to the menu page.")
        except Exception as e:
            print(e)
            talk("Sorry. We couldn't send your email. You will now be redirected to the menu page.")
            return JsonResponse({'result': 'failure'})
        server.quit()
        return JsonResponse({'result' : 'success'})

    compose  = Compose()
    compose.recipient = to_addresses
    compose.subject = subject
    compose.body = body
    return render(request, 'compose.html', {'compose' : compose})

#Function To get Body From The Email
def get_body(msg):
    if msg.is_multipart():
        return get_body(msg.get_payload(0))
    else:
        return msg.get_payload(None, True)

#Function To Reply To Mail
def reply_to_email(msg_id, message):
    global server
    TO_ADDRESS = message['From']
    FROM_ADDRESS = email_address
    msg = email.mime.multipart.MIMEMultipart()
    msg['to'] = TO_ADDRESS
    msg['from'] = FROM_ADDRESS
    msg['subject'] = message['Subject']
    msg.add_header('In-Reply-To', msg_id)
    flag = True
    while(flag):
        talk("Enter body.")
        body = listen()
        print(body)
        try:
            msg.attach(MIMEText(body, 'plain'))
            server.sendmail(msg['from'], msg['to'], msg.as_string())
            talk("Your reply has been sent successfully.")
            flag = False
        except:
            talk("Your reply could not be sent. Do you want to try again? Say yes or no.")
            act = talk()
            act = act.lower()
            if act != 'yes':
                flag = False

#Function To Forward The Mail
def forward_email(item, message):
    global server
    flag1 = True
    flag = True
    new_to_address = list()
    while flag:
        while flag1:
            while True:
                talk("Enter receiver's email address")
                to = listen()
                talk("You meant " + to + " say yes to confirm or no to enter again")
                yn = listen()
                yn = yn.lower()
                if yn == 'yes':
                    to = to.strip()
                    to = to.replace(' ', '')
                    to = to.lower()
                    print(to)
                    new_to_address.append(to)
                    break
            talk("Do you want to add more recipients?")
            ans1 = listen()
            ans1 = ans1.lower()
            print(ans1)
            if ans1 == "no" :
                flag1 = False

        message['From'] = email_address
        message['To'] = ",".join(new_to_address)
        try:
            server.sendmail(email_address, new_to_address, message.as_string())
            talk("Your mail has been forwarded successfully.")
            flag = False
        except:
            talk("Your mail could not be forwarded. Do you want to try again? Say yes or no.")
            act = listen()
            act = act.lower()
            if act != 'yes':
                flag = False

#Get Attachment From Email
def get_attachment(msg):
    for part in msg.walk():
        if part.get_content_maintype() == 'multipart':
            continue
        if part.get('Content-Disposition') is None:
            continue
        filename = part.get_filename()
        if bool(filename):
            # attachment_dir = listen()
            attachment_dir = 'C:/Users/hasna/Desktop'
            filepath = os.path.join(attachment_dir, filename)
            with open(filepath, "wb") as f:
                f.write(part.get_payload(decode=True))
                talk("Attachment has been downloaded")
                path = 'C:/Users/hasna/Desktop/'
                files = os.listdir(path)
                paths = [os.path.join(path, basename) for basename in files]
                file_name = max(paths, key=os.path.getctime)
            with open(file_name, "rb") as f:
                if file_name.find('.mp3') != -1:
                    talk("The Attachment Is a Audio File. Playing the downloaded audio file.")
                    playsound(file_name)
                if file_name.find('.txt') != -1:
                    talk("The Attachment Is A Text File. Opening the downloaded text file.")
                    talk(f.read())
                if file_name.find('.pdf') != -1:
                    talk("The Attachment is a PDF.")
                if file_name.find('.docx') != -1 or file_name.find('doc') != -1:
                    talk("The Attachment is a Document File. Opening the downloaded Document File.")
                    talk(docx2txt.process(f))
                if file_name.find('.jpg') != -1 or file_name.find('png') != -1:
                    talk("The Attachment Is An Image.")

#Function To Read All The Mails
def read_mails(mail_list, folder):
    global server
    #Reverse The Mail List from Latest To Oldest
    mail_list.reverse()
    mail_count = 0
    to_read_list = list()
    # To Read The To and Subjects of The Email
    for item in mail_list:
        #RFC822 defines an electronic message format
        result, email_data = mail.fetch(item, '(RFC822)')
        raw_email = email_data[0][1].decode()
        message = email.message_from_string(raw_email)
        To = message['To']
        From = message['From']
        Subject = message['Subject']
        Msg_id = message['Message-ID']
        talk("Email number " + str(mail_count + 1) + "    .The mail is from " + From + " to " + To + "  . The subject of the mail is " + Subject)
        print('message id= ', Msg_id)
        print('From :', From)
        print('To :', To)
        print('Subject :', Subject)
        print("\n")
        to_read_list.append(Msg_id)
        mail_count = mail_count + 1

    flag = True
    while flag :
        mail_number = 0
        flag1 = True
        while flag1:
            talk("Enter the email number of mail you want to read.")
            mail_number = listen()
            print(mail_number)
            talk("You meant " + str(mail_number) + ". Say yes or no.")
            say = listen()
            say = say.lower()
            if say == 'yes':
                flag1 = False
        mail_number = int(mail_number)
        msgid = to_read_list[mail_number - 1]
        print("message id is =", msgid)
        typ, data = mail.search(None, '(HEADER Message-ID "%s")' % msgid)
        data = data[0]
        result, email_data = mail.fetch(data, '(RFC822)')
        raw_email = email_data[0][1].decode()
        message = email.message_from_string(raw_email)
        To = message['To']
        From = message['From']
        Subject = message['Subject']
        Msg_id = message['Message-ID']
        print('From :', From)
        print('To :', To)
        print('Subject :', Subject)
        talk("The mail is from " + From + " to " + To + "  . The subject of the mail is " + Subject)
        Body = get_body(message)
        Body = Body.decode()
        Body = re.sub('<.*?>', '', Body)
        Body = os.linesep.join([s for s in Body.splitlines() if s])
        if Body != '':
            talk(Body)
        else:
            talk("Body is empty.")

        #Get Attachment If Any
        get_attachment(message)

        if folder == 'inbox':
            talk("Do you want to reply to this mail? Say yes or no. ")
            ans = listen()
            ans = ans.lower()
            print(ans)
            if ans == "yes":
                reply_to_email(Msg_id, message)

        if folder == 'inbox' or folder == 'sent':
            talk("Do you want to forward this mail to anyone? Say yes or no. ")
            ans = listen()
            ans = ans.lower()
            print(ans)
            if ans == "yes":
                forward_email(Msg_id, message)


        if folder == 'inbox' or folder == 'sent':
            talk("Do you want to delete this mail? Say yes or no. ")
            ans = listen()
            ans = ans.lower()
            print(ans)
            if ans == "yes":
                try:
                    mail.store(data, '+X-GM-LABELS', '\\Trash')
                    mail.expunge()
                    talk("The mail has been deleted successfully.")
                    print("mail deleted")
                except:
                    talk("Sorry, could not delete this mail. Please try again later.")

        if folder == 'trash':
            talk("Do you want to delete this mail? Say yes or no. ")
            ans = listen()
            ans = ans.lower()
            print(ans)
            if ans == "yes":
                try:
                    mail.store(data, '+FLAGS', '\\Deleted')
                    mail.expunge()
                    talk("The mail has been deleted permanently.")
                    print("mail deleted")
                except:
                    talk("Sorry, could not delete this mail. Please try again later.")

        talk("Email ends here.")
        talk("Do you want to read more mails?")
        ans = listen()
        ans = ans.lower()
        if ans == "no":
            flag = False

#Function To Search Specific Mail from a user
def search_specific_mail(folder, key, value, foldername):
    global mail
    mail.select(folder)
    result, data = mail.search(None,key,'"{}"'.format(value))
    mail_list=data[0].split()
    if len(mail_list) != 0:
        talk("There are " + str(len(mail_list)) + " emails with this email ID.")
    if len(mail_list) == 0:
        talk("There are no emails with this email ID.")
    else:
        read_mails(mail_list, foldername)

#Inbox Page Code
def inbox_view(request):
    global email_address ,email_password, mail
    if request.method == "POST":
        mail.login(email_address, email_password)
        mail.select('"INBOX"')
        result, data = mail.search(None, '(UNSEEN)')
        unread_list = data[0].split()
        unread_emailnum = len(unread_list)
        result1, data1 = mail.search(None, "ALL")
        total_mail_list = data1[0].split()
        text = "You have reached your inbox. There are " + str(len(total_mail_list)) + " total mails in your inbox. You have " + str(unread_emailnum) + " unread emails"
        talk(text)
        talk("What Would You Like To Do ?. 1. To Read Unread Emails Say Read. 2. To Search Email Say Search. 3. To Go To Menu Page Sat Go Back. 4. To Logout Say Logout.")
        flag = True
        while flag:
            action = listen()
            action = action.lower()
            if action == "read":
                flag = False
                if unread_emailnum != 0:
                    read_mails(unread_list, 'inbox') # Read mail function
                else:
                    talk("You Have No New or Unread Emails. Reading Old Emails")
                    read_mails(total_mail_list, 'inbox')
            elif action == "search":
                flag = False
                talk("If you Want To Search Using Recipient Say Recipient or If you want to search using Subject Say Subject")
                say = listen()
                say = say.lower()
                if say == "recipient":
                    talk("Enter Email ID of Person You Want to Search For")
                    email_id = listen()
                    talk("Did You Mean" + email_id + "Say Yes to Confirm and No to Enter Again")
                    op = listen()
                    op = op.lower()
                    if op == "yes":
                        break
                email_id = email_id.strip()
                email_id = email_id.replace(' ', '')
                email_id = email_id.lower()
                search_specific_mail('INBOX', 'FROM', email_id, 'inbox')

            elif action == "go back":
                talk("You will no be redirected to the Menu Page")
                mail.logout()
                return JsonResponse({'result': 'success'})
            elif action == 'log out':
                email_address = ""
                email_password = ""
                talk("You have been logged out of your account and now will be redirected back to the login page.")
                return JsonResponse({'result': 'logout'})
            else:
                talk("Invalid Action. Please Try Again")

            talk("If you wish to do anything else in the inbox of your mail say yes or to bo back say no.")
            ans = listen()
            ans = ans.lower()
            if ans == 'yes':
                flag = True
                talk("Enter your desired action. Say Read, Search, Go Back or Logout. ")
        talk("You will now be redirected to the menu page.")
        mail.logout()
        return JsonResponse({'result': 'success'})
    return render(request, 'inbox.html')

#Sent Page Code
def sent_view(request):
    global email_address, email_password, mail
    if request.method == 'POST':
        imap_url = 'imap.gmail.com'
        mail = imaplib.IMAP4_SSL(imap_url)
        mail.login(email_address, email_password)
        mail.select('"[Gmail]/Sent Mail"')
        result1, data1 = mail.search(None, "ALL")
        mail_list = data1[0].split()
        talk("You Have Reached Your Sent Mails Folder. You Have " + str(len(mail_list)) + " Mails In Your Sent Mails Folder. To Read All Emails say Read. To Search A Specific email Say Search. To Go Back To The Menu Page Say Back. To Logout Say Logout")
        flag = True
        while (flag):
            action = listen()
            action = action.lower()
            if action == 'read':
                read_mails(mail_list, 'sent')
            if action == 'search':
                flag = False
                emailid = ""
                while True:
                    talk("Enter Email ID Of Receiver.")
                    emailid = listen()
                    talk("You Meant " + emailid + " Say Yes To Confirm Or No To Enter Again")
                    choice = listen()
                    choice = choice.lower()
                    if choice == 'yes':
                        break
                emailid = emailid.strip()
                emailid = emailid.replace(' ', '')
                emailid = emailid.lower()
                emailid = convert_special_char(emailid)
                search_specific_mail('"[Gmail]/Sent Mail"', 'TO', emailid,'sent')

            elif action == 'back':
                talk("You Will Now Be Redirected To The Menu Page.")
                mail.logout()
                return JsonResponse({'result': 'success'})

            elif action == 'logout':
                email_address = ""
                email_password = ""
                talk("You Have Been Logged Out Of Your Account And Now Will Be Redirected Back To The Login Page.")
                return JsonResponse({'result': 'logout'})

            else:
                talk("Invalid Action. Please Try Again.")

            talk("If You Wish To Do Anything Else In The Sent Mails Folder. Say Yes Or Else Say No to Logout.")
            ans = listen()
            ans = ans.lower()
            if ans == 'yes':
                flag = True
                talk("Enter Your Desired Action. Say Search, Back Or Logout.")
        talk("You Will Now Be Redirected To The Menu Page.")
        mail.logout()
        return JsonResponse({'result': 'success'})

    elif request.method == 'GET':
        return render(request, 'sent.html')

#Trash Page Code
def trash_view(request):
    global email_address, email_password, mail
    if request.method == 'POST':
        mail.select('"[Gmail]/Trash"')
        result1, data1 = mail.search(None, "ALL")
        mail_list = data1[0].split()
        text = "You have reached your trash folder. You have " + str(len(mail_list)) + " mails in your trash folder. To search a specific email say Search. To go back to the menu page say Go Back. To logout say Logout."
        talk(text)
        flag = True
        while (flag):
            action = listen()
            action = action.lower()
            print(action)
            if action == 'search':
                flag = False
                email_id = ""
                while True:
                    talk("Enter email ID of sender.")
                    email_id = listen()
                    talk("You meant " + email_id + " say yes to confirm or no to enter again")
                    yn = listen()
                    yn = yn.lower()
                    if yn == 'yes':
                        break
                email_id = email_id.strip()
                email_id = email_id.replace(' ', '')
                email_id = email_id.lower()
                search_specific_mail('"[Gmail]/Trash"', 'FROM', email_id, 'trash')

            elif action == 'back':
                talk("You will now be redirected to the menu page.")
                mail.logout()
                return JsonResponse({'result': 'success'})

            elif action == 'log out':
                email_address = ""
                email_password = ""
                talk("You have been logged out of your account and now will be redirected back to the login page.")
                return JsonResponse({'result': 'logout'})

            else:
                talk("Invalid action. Please try again.")

            talk("If you wish to do anything else in the trash folder say yes or else to logout say no.")
            ans = listen()
            ans = ans.lower()
            print(ans)
            if ans == 'yes':
                flag = True
                talk("Enter your desired action. Say search, back or logout. ")

        talk("You will now be redirected to the menu page.")
        mail.logout()
        return JsonResponse({'result': 'success'})
    return render(request, 'trash.html')