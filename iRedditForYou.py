import praw
import time
import datetime
import smtplib
import argparse

from email.mime.text import MIMEText

parser = argparse.ArgumentParser(description = "I read Reddit for you!")
parser.add_argument('--sender', '-s', type = str, help = 'Email address of the sender', required = True)
parser.add_argument('--senderpassword', '-pw', type = str, help = 'Password of senders email account', required = True)
parser.add_argument('--reciever', '-r', type = str, help = 'Email address of the reciever', required = True)
parser.add_argument('--numhours', '-nh', type = int, default = 4, help = 'Number of hours between each read of reddit')
parser.add_argument('--clientid', '-cid', type = str, help = 'client_id of the reddit application', required = True)
parser.add_argument('--clientsecret', '-cs', type = str, help = 'client_secret of the reddit application', required = True)
parser.add_argument('--useragent', '-ua', type = str, help = 'user_agent of the reddit application', required = True)
parser.add_argument('--subreddit', '-sr', type = str, help = 'The subreddit you want the program to read for you', required = True)
parser.add_argument('--keywords', '-kw', type = str, help = 'The keywords the program will search for', required = True)
parser.add_argument('--sorting', '-st', type = str, default = 'new', help = 'Sorting of the submission results')
parser.add_argument('--timeperiod', '-t', type = str, default = 'month', help = 'Time period for submission results')
args = parser.parse_args()

lastProcessedSubmission = datetime.datetime.now() - datetime.timedelta(days = 30)  

reddit = praw.Reddit(client_id=args.clientid, 
                    client_secret=args.clientsecret, 
                    user_agent=args.useragent)

while True:
    section = ""
    mailSections = ""
    submissions = list(reddit.subreddit(args.subreddit).search(args.keywords, args.sorting, 'lucene', args.timeperiod))

    for i, submission in enumerate(submissions):
        if(datetime.datetime.fromtimestamp(submission.created) > lastProcessedSubmission):
            #Fix, this is ugly af
            if i == 0:
                latestSubmission = datetime.datetime.fromtimestamp(submission.created)
            
            section =   datetime.datetime.fromtimestamp(submission.created).strftime("%Y-%m-%d %H:%M:%S") + "\n\n" 
            section +=  submission.title + " "  
            section +=  submission.selftext + "\n\n" 
            section +=  submission.url + "\n\n\n"
            section +=  "============================================================"
            section +=  "\n\n\n"

            mailSections += section
             
    if mailSections != "":
        lastProcessedSubmission = latestSubmission 

        mail = MIMEText(mailSections)
        mail['Subject'] = args.keywords
        mail['From'] = args.sender
        mail['To'] = args.reciever

        try:
            server = smtplib.SMTP_SSL('smtp.gmail.com', 465) #587)
            server.ehlo()
            server.login(args.sender, args.senderpassword)
            server.send_message(mail)
            server.quit()
        except:
            print("Error connecting to the email server")

    time.sleep(3600 * args.numhours)
