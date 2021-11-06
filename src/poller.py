# Import smtplib for the actual sending function
import smtplib
import ssl
# Import the email modules we'll need
from email.message import EmailMessage
import hashlib
import base64
from datetime import datetime
import json
import os
import httplib2
import re
import webbrowser
from bs4 import BeautifulSoup
from pprint import pprint
from dotenv import load_dotenv

#Change to DB directory
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

#Read ENV file credentails
load_dotenv()
senderEmail = os.getenv('SENDER_EMAIL')
senderEmailPassword = os.getenv('PASSWORD')
destinationEmail = os.getenv('DEST_EMAIL')
### Define all URLs to query #################################################
queryURLs = [
"https://arxiv.org/search/advanced?advanced=&terms-0-operator=AND&terms-0-term=quinn&terms-0-field=all&classification-physics_archives=all&classification-include_cross_list=include&date-filter_by=all_dates&date-year=&date-from_date=&date-to_date=&date-date_type=submitted_date&abstracts=show&size=50&order=-announced_date_first",
"https://arxiv.org/search/advanced?advanced=1&terms-0-operator=AND&terms-0-term=Randal-Williams&terms-0-field=author&terms-1-operator=AND&terms-1-term=homotopy&terms-1-field=abstract&terms-2-operator=OR&terms-2-term=K-theory&terms-2-field=abstract&terms-3-operator=OR&terms-3-term=equivariant&terms-3-field=title&terms-4-operator=OR&terms-4-term=cohommology&terms-4-field=title&classification-mathematics=y&classification-physics_archives=all&classification-include_cross_list=include&date-filter_by=all_dates&date-year=&date-from_date=&date-to_date=&date-date_type=submitted_date&abstracts=show&size=50&order=-announced_date_first"
]
##############################################################################

def poll_new_articles(queryURL):
    progSafeURL = str(queryURL).encode('utf-8')
    progSafeURL = base64.b64encode(progSafeURL)
    progSafeURL = hashlib.md5(progSafeURL)
    jsonFileName = (progSafeURL.hexdigest()+".json")
    # Fetch the data
    http = httplib2.Http()
    resp, data = http.request(queryURL)

    #Compare Article to top article in JSON output file
    fileExists = False
    latestArticle = {
            "Title": None,
            "Published": None,
        }
    try:
        with open('mockDB/' +jsonFileName) as jsonDB:
            fileData = json.load(jsonDB)
            #Print latest article
            #pprint(fileData[0])
            latestArticle = fileData[0]
            jsonDB.close()
            fileExists = True
    except FileNotFoundError:
        fileExists = False
        print("Loading existing --- File does not exist.")
    except IndexError:
        print("File was probably empty..Index out of range")

    # Parse data with Beautiful soup
    soup = BeautifulSoup(str(data), 'lxml')
    results = soup.find_all("li", attrs={'class': 'arxiv-result'})
    matchingArticles = []
    matchFound = False
    newPapers = False
    for article in results:
        articleSoup = BeautifulSoup(str(article), 'lxml')
    # Article Name parsing
        articleTitle = articleSoup.find("p", attrs={'class': re.compile('^title')})
        articleName = articleTitle.text.replace("\\n", "")
        articleName = articleName.strip()
    # Article Link
        articleLink = articleSoup.find("p", attrs={'class': re.compile('^list-title')})
        articleLink = articleLink.find("a")
        articleLink = str(articleLink['href'])
    # Article published time parsing
        articlePublished = articleSoup.find(
            "p", attrs={'class': re.compile('^is-size-7')})
        articlePublished = articlePublished.text.replace("\\n", "")
        articlePublished = articlePublished.strip()
        articlePublished = articlePublished.split(";")
        articlePublished = articlePublished[0].replace("Submitted ", "")
    # Convert time string to date
        dateObj = datetime.strptime(articlePublished, "%d %B, %Y")
    # Add to JSON object
        articleEntry = {
            "Title": articleName,
            "Published": datetime.strftime(dateObj, "%Y-%m-%d"),
            "Link" : articleLink
        }
    #Detect when you reach an article already in the file
        if(articleEntry['Title'] == latestArticle['Title']):
            matchFound = True
            break #End loop as a match was found
        matchingArticles.append(articleEntry)
        #pprint(articleEntry)


    #Output results to JSON file, if there was at least one article found
    if(len(matchingArticles) >= 1):
        newPapers = True
        print("--- New Articles Detected---\n")
        pprint(matchingArticles)
        with open("mockDB/" + jsonFileName, "w", encoding = 'utf-8') as outputFile:
            json.dump(matchingArticles, outputFile)
    return newPapers
        
#Authenticate with email service
try: 
    #Create your SMTP session 
    smtp = smtplib.SMTP('smtp.gmail.com', 587) 

#Use TLS to add security 
    smtp.starttls() 
    #User Authentication 
    smtp.login(senderEmail,senderEmailPassword)
    #Defining The Message 
    message = ""
except Exception as ex: 
    print("Something went wrong....",ex) 

#Call the polling function for each URL
for url in queryURLs:
    newPapers = poll_new_articles(url)
    #Get filename
    if(newPapers):
        progSafeURL = url.encode('utf-8')
        progSafeURL = base64.b64encode(progSafeURL)
        progSafeURL = hashlib.md5(progSafeURL)
        jsonFileName = (progSafeURL.hexdigest()+".json")
        #Print new articles from the log file
        
        try:
            with open('mockDB/' +jsonFileName) as jsonDB:
                fileData = json.load(jsonDB)
                jsonDB.close()
                #Prepare email
                msg = EmailMessage()
                msg['Subject'] = str(len(fileData)) + ' New Papers Detected'
                msg['From'] = senderEmail
                msg['To'] = destinationEmail
                msgBody = "\nSearch URL:" + url + "\n\nNew Papers:"
                for paper in fileData:
                    msgBody += "\n\n" + paper['Title'] + '\t\n' + paper['Published'] + '\t\n' + paper['Link']
                #Sending the Email
                msg.set_content(msgBody)
                print("New paper emails will be sent.")
                smtp.send_message(msg) 
        except FileNotFoundError:
            print("Email send function -> JSON file does not exist.")
    else:
        print("No new papers")
smtp.quit()