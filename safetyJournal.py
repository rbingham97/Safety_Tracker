
# first pass at a COVID safety journal backend
# written by Russell Bingham the week of 10/12/20

import calendar
import datetime
import matplotlib
from matplotlib import pyplot as plt
import numpy as np
from scipy.interpolate import spline

# to be changed: base discrete list of risk levels for unmasked one on one interaction
# defines shape of infectiousness curve to be scaled by other factors
BASE_RISK_LIST = np.array([0.0, 0.1, 0.3, 0.6, 1.0, 0.75, 0.53, 0.4, 0.31, 0.24, 0.18, 0.12, 0.07, 0.03, 0.0])

MASK_RISK_REDUCTION = 0.5 # factor of risk reduction for wearing mask
DISTANCE_RISK_REDUCTION = 0.5 # factor of risk reduction for distancing
OUTDOORS_RISK_REDUCTION = 0.5 # factor of risk reduction for outdoors instead of indoors

# log an event, dayOffset to move event to a day other than today
def logEvent(user):
    
    # ask relevant questions
    dayOffset = int(input("When was the event? (enter offset, 0 for today): "))

    # how many people were there?
    numPeople = int(input("How many people were there? (enter a number): ")) #get num from terminal

    # were people wearing masks?
    temp = input("Were people wearing masks? (y/n): ")
    if temp == "y":
        maskBool = 1.0
    else:
        maskBool = 1.0/MASK_RISK_REDUCTION
    
    temp = input("Were people socially distanced? (y/n): ")
    # were people distanced?
    if temp == "y":
        distanceBool = 1.0
    else:
        distanceBool = 1.0/DISTANCE_RISK_REDUCTION

    temp = input("Was the event outside? (y/n): ")
    # was the event outside?
    if temp == "y":
        outdoorsBool = 1.0
    else:
        outdoorsBool = 1.0/OUTDOORS_RISK_REDUCTION

    #aggregate risk factors
    riskFactor = (MASK_RISK_REDUCTION*maskBool)*(DISTANCE_RISK_REDUCTION*distanceBool)*(OUTDOORS_RISK_REDUCTION*outdoorsBool)
    
    # The size of each step in days
    day_delta = datetime.timedelta(days=1)

    start_date = datetime.date.today() + dayOffset*day_delta
    end_date = start_date + 15*day_delta

    for i in range((end_date - start_date).days):
        currentDay = start_date + i*day_delta
        user.addDayRisk(currentDay, (numPeople*BASE_RISK_LIST[i])*riskFactor)

        

#graph the user's risk from startDate to endDate
def graphRiskRange(user, startDate, endDate):
    day_delta = datetime.timedelta(days=1)
    riskVals = []
    dates = []
    numDays = (endDate - startDate).days

    for i in range(numDays):
        currentDay = startDate + i*day_delta
        dates += [currentDay]
        riskVals += [user.getDayRisk(currentDay)]

    riskX = np.linspace(0, numDays, numDays)
    
    # just smooth out the curve to look nice
    xsmooth = np.linspace(riskX.min(), riskX.max(), 300)
    ysmooth = spline(riskX, riskVals, xsmooth)

    # start plotting
    fig, ax = plt.subplots()

    plt.plot(xsmooth, ysmooth)

    plt.ylim(0, 9)
    plt.yticks([1.5, 4.5, 7.5], ["Low", "Medium", "High"])
    ax.axhspan(0, 3, facecolor='green', alpha=0.5)
    ax.axhspan(3, 6, facecolor='yellow', alpha=0.5)
    ax.axhspan(6, 9, facecolor='red', alpha=0.5)
    
    plt.show()

# user profile container
class UserProfile:
    
    def __init__(self, username, password):
        self._username = username
        self._password = password
        
        # risk data to be stored in dictionary with keys as dates, values as risk numbers
        self._riskDict = {}

    # return risk associated with a date. return 0 if date not in self.riskDict
    def getDayRisk(self, date):
        
        if date not in self._riskDict:
            return 0
        else:
            return self._riskDict[date]

    #add risk value to date in dict, set if no value yet
    def addDayRisk(self, date, risk):

        if date not in self._riskDict:
            self._riskDict[date] = risk
            return 0 # status flag
        else:
            self._riskDict[date] += risk
            return 1 # status flag
        
    
if __name__ == "__main__":
    day_delta = datetime.timedelta(days=1)

    #make dummy profile
    user = UserProfile("russell", "pw")

    #log a test event
    logEvent(user)
    #log another test event
    logEvent(user)

    #plot
    graphRiskRange(user, datetime.date.today(), datetime.date.today() + day_delta*14)



