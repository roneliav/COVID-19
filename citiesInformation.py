"""
The program caculates many information about cities with more than 5,000 residents.
"""

import openpyxl
import math
import fromURLtoList
from datetime import datetime, timedelta


# take the information from MOH website. Return a dictionary
def getCitiesByDays():
    url = 'https://data.gov.il/api/3/action/datastore_search?resource_id=d07c0771-01a8-43b2-96cc-c6154e7fa9bd'
    return fromURLtoList.getList(url)

# get a dictionary of one day and return the number of sicks in this day.
def getActiveSicksThisDay(day):
    if day.get('accumulated_cases') == '<15' or day.get('accumulated_recoveries') == '<15':
        return 1
    return int(day.get('accumulated_cases')) - int(day.get('accumulated_recoveries'))

# change the input day to the day after input days (integer)
def changeDate(day, days):
    day = datetime.strptime(day, '%Y/%m/%d')
    daysToMove = timedelta(days = days)
    nextDay = day + daysToMove
    return (str(nextDay.year) + "/" + nextDay.strftime('%m/%d'))

# create a dictionary with the number of residents in each city
def makePopulationDict():
    populationDict = {}
    populationPath = 'population_madaf_2018_1.xlsx' # the file is from 'https://www.cbs.gov.il/he/publications/Pages/2017/%D7%90%D7%95%D7%9B%D7%9C%D7%95%D7%A1%D7%99%D7%99%D7%94-%D7%95%D7%9E%D7%A8%D7%9B%D7%99%D7%91%D7%99-%D7%92%D7%99%D7%93%D7%95%D7%9C-%D7%91%D7%99%D7%99%D7%A9%D7%95%D7%91%D7%99%D7%9D-%D7%95%D7%91%D7%90%D7%96%D7%95%D7%A8%D7%99%D7%9D-%D7%A1%D7%98%D7%98%D7%99%D7%A1%D7%98%D7%99%D7%99%D7%9D-2017.aspx'
    populationFile = openpyxl.load_workbook(populationPath)
    populationSheet = populationFile['עולים ביישובים 5000+']
    # create a key for each city and insert the number of residents as a value
    for row in range(13, 200):
        city = populationSheet['A'+str(row)].value
        # remove '*' char from the end of the city name
        if '*' in city:
            city = city[0:-1]
        populationDict[city] = populationSheet['C'+str(row)].value
    populationFile.close()
    return populationDict

# return the accumulated cases
def getAccumulatedSicks(day):
    # if the accumulated cases are under 15, return 1
    if day.get('accumulated_cases') == '<15':
        return 1
    return int(day.get('accumulated_cases'))

# return the accumulated tedsted in the input day.
def getTestedUntilThisDay(day):
    # if the accumulated tested are under 15, return 1
    if day.get('accumulated_tested') == '<15':
        return 1
    return int(day.get('accumulated_tested'))

# add a dictionary for the input day
def makeNewDay(dict, day):
    dict[day] = {'activeSicksToday': 0,
                 'newSicksInLastWeek': 0,
                 'growthRate': 0,
                 'positiveChecks': 0,
                 'testedLastWeek': 0,
                 'newSicksLastWeekPer10thousand': 0}

# divide the grades to lights according 'traffic light program'
def getColorFromGrade(grade):
    if grade == 'NaN':
        return 'NaN'
    elif grade <= 4.5:
        return 'green'
    elif grade <= 6:
        return 'yellow'
    elif grade <= 7.5:
        return 'orange'
    return 'red'

# calculate the city grade according the city's data
def lightGrade(citiesDict, city):
    for day in citiesDict[city]:
        dayDict = citiesDict[city][day]
        try:
            # the equation is according: 'https://www.themarker.com/embeds/pdf_upload/2020/20200830-160844.pdf'
            grade = 2 + math.log(dayDict['newSicksLastWeekPer10thousand'] * dayDict['growthRate'] * dayDict['growthRate']) + (dayDict['positiveTestingRateLastWeek'] / 8)
            if grade > 10:
                grade = 10
            elif grade < 0:
                grade = 0
            # print("הציון עבור" , city , "בתאריך", day, "הוא:", "%.2f" % (grade))
        # means the city has missing data
        except:
            grade = "NaN"
            # print("הציון עבור", city, "בתאריך", day, "הוא:", grade)
        dayDict['lightGrade'] = grade
        dayDict['colorGrade'] = getColorFromGrade(grade)

# calculate days from green city to red city and vice cersa
def timeBetweenLights(citiesDict, lastDay):
    fromRedToGreenTotal = 0
    fromRedToGreenTimes = 0
    fromGreenToRedTotal = 0
    fromGreenToRedTimes = 0
    for city in citiesDict:
        greenCount = 0
        yellowCount = 0
        orangeCount = 0
        redCount = 0
        for day in citiesDict[city]:
            dayDict = citiesDict[city][day]
            dayDate = datetime.strptime(day, '%Y/%m/%d')
            beginDate = datetime(2020, 5, 1) # before this day - there is missing data
            endDate = lastDay # after this day - there is missing data

            if dayDate >= beginDate and dayDate <= endDate:
                color = dayDict.get('colorGrade')
                if color == 'green':
                    differenceDays = yellowCount + orangeCount + 1
                    # if the differenceDays = 1, it's may be an unusual day
                    if redCount != 0 and differenceDays > 1:
                        # print("Days from red to green at", city, "is", yellowCount + orangeCount)
                        fromRedToGreenTotal += yellowCount + orangeCount
                        fromRedToGreenTimes += 1
                        # count again from 0
                        redCount = 0
                        orangeCount = 0
                        yellowCount = 0
                        greenCount = 1
                    elif yellowCount != 0 or orangeCount != 0:
                        # count again from 0
                        orangeCount = 0
                        yellowCount = 0
                        greenCount = 1
                    else:
                        greenCount += 1
                elif color == 'yellow':
                        yellowCount += 1
                elif color == 'orange':
                    orangeCount += 1
                elif color == 'red':
                    differenceDays = yellowCount + orangeCount + 1
                    # if the differenceDays = 1, it's may be an unusual day
                    if greenCount != 0 and differenceDays > 1:
                        # print("Days from green to red at", city, "is", differenceDays)
                        fromGreenToRedTotal += differenceDays
                        fromGreenToRedTimes += 1
                        # count again from 0
                        orangeCount = 0
                        yellowCount = 0
                        greenCount = 0
                    elif yellowCount != 0 or orangeCount != 0:
                        # count again from 0
                        orangeCount = 0
                        yellowCount = 0
                        greenCount = 1
                    redCount += 1

    # print averages
    fromGreenToRedAve = fromGreenToRedTotal / fromGreenToRedTimes
    print("The average days from green city to red city is:", "%.2f" % fromGreenToRedAve)
    fromRedToGreenAve = fromRedToGreenTotal / fromRedToGreenTimes
    print("The average days from red city to green city is:", "%.2f" % fromRedToGreenAve)

# activeSicksTodayPer10thousand = active-sicks for each 10,000 persons
def getActivesPer10Thousands(citiesDict, town, date, residentsNumber):
    # may be a problem with the residents number from HALMA"S data
    try:
       return int((citiesDict[town][date]['activeSicksToday'] / residentsNumber) * 10000)
    except:
        return "NaN"

def getNewSicksPer10Thousand(citiesDict, town, date, residentsNumber):
    try:
        newSicksLastWeekPer10thousand = int((citiesDict[town][date]['newSicksInLastWeek'] / residentsNumber) * 10000)
        if newSicksLastWeekPer10thousand == 0:
            newSicksLastWeekPer10thousand = 1  # for future dividing
        return newSicksLastWeekPer10thousand
    except:
        return 'NaN'

# positiveTestingRateLastWeek = new-Sicks-In-Last-Week / tested-Last-Week
def getPositiveTestingRate(citiesDict, town, date):
    if citiesDict[town][date]['testedLastWeek'] == 0:
        return 0
    else:
        return float((citiesDict[town][date]['newSicksInLastWeek'] / citiesDict[town][date]['testedLastWeek']) * 100)

# get 2 days and return the last one.
# 'lastDay' type is 'datetime' and 'currentDay' type is 'string'
def updateLastDay(lastDay, currentDay):
    currentDay = datetime.strptime(currentDay, '%Y/%m/%d')
    if lastDay > currentDay:
        return lastDay
    return currentDay

# calculate and print cities information
def citiesInformation():
    lastDay = datetime(2000, 1, 1)
    populationCitiesDict = makePopulationDict()
    # get cities information
    citiesByDays = getCitiesByDays()
    # make a dictionary for the city information
    citiesDict = {}
    # for each city: caculate the number of its residents,
    for day in citiesByDays:
        town = day.get('town')
        date = day.get('date')
        lastDay = updateLastDay(lastDay, date)
        residentsNumber = populationCitiesDict.get(town)
        # add only cities wich located in the ecxel. otherwise, they are less then 5,000 residents.
        if residentsNumber == None:
            continue
        # if the town isn't in the dictionary keys, create a key for this city
        if not town in citiesDict.keys():
            citiesDict[town] = {}
        # each day is influnce itself and the day after week, so create new keys for those days
        if not date in citiesDict.get(town).keys():
            makeNewDay(citiesDict[town], date)
        dayNextWeek = changeDate(date, 7)
        if not dayNextWeek  in citiesDict.get(town).keys():
            makeNewDay(citiesDict[town], dayNextWeek)

        citiesDict[town][date]['activeSicksToday'] += getActiveSicksThisDay(day)
        citiesDict[town][date]['activeSicksTodayPer10thousand'] = getActivesPer10Thousands(citiesDict, town, date, residentsNumber)
        # newSicksInLastWeek = sicks-today - sick-before-week
        citiesDict[town][dayNextWeek]['newSicksInLastWeek'] -= getAccumulatedSicks(day)
        citiesDict[town][date]['newSicksInLastWeek'] += getAccumulatedSicks(day)
        # testedLastWeek = tested today - tested last week
        citiesDict[town][dayNextWeek]['testedLastWeek'] -= getTestedUntilThisDay(day)
        citiesDict[town][date]['testedLastWeek'] += getTestedUntilThisDay(day)
        citiesDict[town][date]['newSicksLastWeekPer10thousand'] = getNewSicksPer10Thousand(citiesDict, town, date, residentsNumber)
        # growthRate = new-Sicks-Last-Week-Per-10thousand / new-Sicks-before-two-Weeks-Per-10thousand
        citiesDict[town][dayNextWeek]['growthRate'] = 1 / citiesDict[town][date]['newSicksLastWeekPer10thousand']
        citiesDict[town][date]['growthRate'] *= citiesDict[town][date]['newSicksLastWeekPer10thousand']
        citiesDict[town][date]['positiveTestingRateLastWeek'] = getPositiveTestingRate(citiesDict, town, date)
        # calculate the grade of each city according the 'traffic light' program
        lightGrade(citiesDict, town)
    timeBetweenLights(citiesDict, lastDay)