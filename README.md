# Littlefield Data Scraper
## Intro
This application will help collect data from the official website
given the login credentials for a team. The data will be automatically
formatted into a readable format, allowing the user to easily create graphs
and analyze trends during the simulation. The application will run every hour
on the hour, ensuring that data is collected for every day of the simulation.

## Setup
For proper execution, the `setup.sh` file will need to be executed. To install and
setup the application, run the following commands:
```angular2html
cd ~/Desktop
git clone https://github.com/michaeljschwartz4/LittlefieldHelper.git
cd LittlefieldHelper
chmod +x setup.sh
./setup.sh
```
The user will be prompted to enter their team's name and password to connect to the website.

This setup will update data to the spreadsheet every hour. **Any modifications to the file will be overwritten!
Be sure to save your modifications to a new file!**

### Alternative Execution
After the initial setup, an ad hoc execution can be made by using the following commands:
```angular2html
chmod +x littlefield-script.py
source venv/bin/activate
./littlefield-script.py <team_name> <password>
deactivate
```

### Troubleshooting
If issues come up, please check the log for relevant information.
To verify that the job will run every hour, enter the following command into the terminal:
`sudo crontab -u <device-username-here> -l`

This will prompt the user to enter the password to their device.

A successfully scheduled job will look like the following:
```angular2html
❯ sudo crontab -u <device-username-here> -l
0 * * * * cd /Users/<device-username-here>/Desktop/Littlefield && ./venv/bin/python3 littlefield-script.py <team_name> <password> >> littlefield.log 2>&1
```
To remove your scheduled jobs, run `crontab -r`

**For any further questions or issues with the application, please email mjschwa@uw.edu**
## Schema
*INV* - Current inventory count

*CASH* - Amount of money (in thousands of dollars)

*JOBIN* - Jobs received during the day

*JOBQ* - Jobs queued during the day

*S1Q* - Backlog for Station 1

*S2Q* - Backlog for Station 2

*S3Q* - Backlog for Station 3

*S1UTIL* - Utilization rate of Station 1

*S2UTIL* - Utilization rate of Station 2

*S3UTIL* - Utilization rate of Station 3

*JOBT0* - Average job lead time (Contract 1)

*JOBT1* - Average job lead time (Contract 2)

*JOBT2* - Average job lead time (Contract 3)

*JOBREV0* - Average job revenue (Contract 1)

*JOBREV1* - Average job revenue (Contract 2)

*JOBREV2* - Average job revenue (Contract 3)

*JOBOUT0* - Number of completed jobs (Contract 1)

*JOBOUT1* - Number of completed jobs (Contract 2)

*JOBOUT2* - Number of completed jobs (Contract 3)

*Backlog* - Jobs in backlog