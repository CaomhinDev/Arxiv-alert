# Arxiv-alert
This is a simple web scraping script that checks for new papers published to Arxiv containing certain keywords.
It can be configured as a scheduled task that will periodically.
When new papers are detected, an email will be sent to an address specified by the user.
## Setup
### Email Configuration
Create a Gmail account and set it to allow less secure apps. This is used to allow Python to authenticate with the Gmail credentials.
You can turn on this feature at the [following link](https://myaccount.google.com/lesssecureapps?pli=1&rapt=AEjHL4PBzRUYCw8jDFLXfrpP7Q6Rn_ZMsC-o9oZiZsIREsKSa17ekyl8XmDNm_SYoPnMWa78ZM36i7hTKZq5caqUpz7zZwqosQ)
### Python Packages
Ensure you have all the Python packages installed, you can install them by using * *pip install -r requirements.txt* *
## Usage
Create an array of search URLs and update the * *queryURLs* * variable in Poller.py, you can manually visit the site and construct your advanced searches.
Rename the * *.envExample* * file to * *.env* * and configure the sender email, sender password, and destination email values.
Set the Python file to run as a scheduled task on Windows or Cronjob on Linux.
# Linux Cronjob
Use * *crontab -e* * to create a cronjob. You can add an entry as follows "30 * * * * /usr/bin/python3 /home/<pathTo>Arxiv-alert/src/poller.py >> ~/cron.log 2>&1" to schedule the script to run every 30 minutes and log any output to the specified log file.
# Windows Schedule Task
Use the task scheduler to run the script periodically.