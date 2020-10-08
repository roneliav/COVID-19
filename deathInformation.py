"""
The program calculates many information about death in all the country
"""

from prettytable import PrettyTable
import fromURLtoList

def getDeadList():
    url = 'https://data.gov.il/api/3/action/datastore_search?resource_id=a2b2fceb-3334-44eb-b7b5-9327a573ea2c'
    return fromURLtoList.getList(url)

# If the information in the string isn't a number, return 0.
def convertToFloat(string):
    try:
        val = float(string)
    except ValueError:
        val = 0
    return val

def makeGroupsDict():
    dict = {
    'lowAgeSum' : 0,
    'lowAgeVentilated' : 0,
    'lowAgeDaysToDeath' : 0,
    'mediumMinusAgeSum' : 0,
    'mediumMinusAgeVentilated' : 0,
    'mediumMinusAgeDaysToDeath' : 0,
    'mediumPlusAgeSum' : 0,
    'mediumPlusAgeVentilated' : 0,
    'mediumPlusAgeDaysToDeath' : 0,
    'highAgeSum' : 0,
    'highAgeVentilated' : 0,
    'highAgeDaysToDeath' : 0,
    }
    return dict

def ageGroupInfo(ageGroupsDict, person):
    # low-age inforamtiom
    if person.get('age_group') == '<65':
        ageGroupsDict['lowAgeSum'] += 1
        if person.get('Ventilated') == '1':
            ageGroupsDict['lowAgeVentilated'] += 1
        ageGroupsDict['lowAgeDaysToDeath'] += convertToFloat(person.get("Time_between_positive_and_death"))

    # medium-minus age inforamtiom
    if person.get('age_group') == '65-74':
        ageGroupsDict['mediumMinusAgeSum'] += 1
        if person.get('Ventilated') == '1':
            ageGroupsDict['mediumMinusAgeVentilated'] += 1
        ageGroupsDict['mediumMinusAgeDaysToDeath'] += convertToFloat(person.get("Time_between_positive_and_death"))

    # medium-plus age inforamtiom
    if person.get('age_group') == '75-84':
        ageGroupsDict['mediumPlusAgeSum'] += 1
        if person.get('Ventilated') == '1':
            ageGroupsDict['mediumPlusAgeVentilated'] += 1
        ageGroupsDict['mediumPlusAgeDaysToDeath'] += convertToFloat(person.get("Time_between_positive_and_death"))

    # high-age inforamtiom
    if person.get('age_group') == '85+':
        ageGroupsDict['highAgeSum'] += 1
        if person.get('Ventilated') == '1':
            ageGroupsDict['highAgeVentilated'] += 1
        ageGroupsDict['highAgeDaysToDeath'] += convertToFloat(person.get("Time_between_positive_and_death"))


def printAgesGropInfo(agesGroupDict):
    # print a table with information by ages group
    agesInformation = PrettyTable()
    agesInformation.field_names = ["Age group", "Total deathes", "Total ventilated", "Average days until death"]
    agesInformation.add_row(["<65", agesGroupDict.get('lowAgeSum'), agesGroupDict.get('lowAgeVentilated'), "%.2f" % (agesGroupDict.get('lowAgeDaysToDeath') / agesGroupDict.get('lowAgeSum'))])
    agesInformation.add_row(["65-74", agesGroupDict.get('mediumMinusAgeSum'), agesGroupDict.get('mediumMinusAgeVentilated'), "%.2f" % (agesGroupDict.get('mediumMinusAgeDaysToDeath') / agesGroupDict.get('mediumMinusAgeSum'))])
    agesInformation.add_row(["75-84", agesGroupDict.get('mediumPlusAgeSum'), agesGroupDict.get('mediumPlusAgeVentilated'), "%.2f" % (agesGroupDict.get('mediumPlusAgeDaysToDeath') / agesGroupDict.get('mediumPlusAgeSum'))])
    agesInformation.add_row(["85+", agesGroupDict.get('highAgeSum'), agesGroupDict.get('highAgeVentilated'), "%.2f" % (agesGroupDict.get('highAgeDaysToDeath') / agesGroupDict.get('highAgeSum'))])
    print(agesInformation)

# print detailes about hospitializated and died and non-hospitializated and died, by age group and more.
def countryDeathInformation():
    # open the death information
    deadList = getDeadList()

    isVantilated = 0
    daysVantilatedUntilDeath = 0
    daysNotVantilatedUntilDeath = 0
    daysFromSickToDeath = 0
    didntHospitialization = 0

    ageGropsDict = makeGroupsDict()


    for person in deadList:

        lengthOfHospitalization = convertToFloat(person.get("Length_of_hospitalization"))

        # length of hospitalization time for all the ages
        if lengthOfHospitalization == 0:
            didntHospitialization += 1

        # length of sickness of all the ages
        lengthOfSick = convertToFloat(person.get("Time_between_positive_and_death"))

        # length of hospitalization for ventilated and non-vantilated
        if convertToFloat(person.get('Ventilated')) == 1:
            isVantilated += 1
            daysVantilatedUntilDeath += lengthOfHospitalization
        else:
            daysNotVantilatedUntilDeath += lengthOfHospitalization
        daysFromSickToDeath += lengthOfSick

        ageGroupInfo(ageGropsDict, person)
    # print the information
    print("Total deaths:", len(deadList))
    print("Ave. days from the sickness to the death:", "%.2f" % (daysFromSickToDeath / len(deadList)))
    print("")
    print("Total deads ventilated:", isVantilated)
    print("Ave. days for hospitalization for ventilated until death:", "%.2f" % (daysVantilatedUntilDeath / isVantilated))
    print("")
    print("Total deads non-ventilated:", len(deadList) - isVantilated)
    print("Ave. days for hospitalization for non-ventilated until death:", "%.2f" % (daysNotVantilatedUntilDeath / (len(deadList) - isVantilated)))
    print("")
    print("Total deads non-hospitalizated:", didntHospitialization)
    print("")
    #print ages information
    printAgesGropInfo(ageGropsDict)
