from crontab import CronTab
import os


# init cron
cron = CronTab(user="Amirhossein")
for job in cron:
    print(job.frequency())
    cron.remove(job)
    cron.write()

# add new cron job
job = cron.new(command='/Users/amirhossein/.local/share/virtualenvs/stackoverflow-5mmwjvAZ/bin/python3 {}/jobs.py'.
               format(os.getcwd()))

# job settings
job.hour.every(23)

cron.write()
