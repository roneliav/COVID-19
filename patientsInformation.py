"""
The program calculates some information about patients in all the country.
"""

import fromURLtoList

def getPatientsList():
    url = 'https://data.gov.il/api/3/action/datastore_search?resource_id=8455d49f-ce32-4f8f-b1d4-1d764660cca3'
    return fromURLtoList.getList(url)

# If the information in the string isn't a number, return 0.
def convertToFloat(string):
    try:
        val = float(string)
    except ValueError:
        val = 0
    return val

# print the average number of days for recovery (from positive test until negative test or equal)
def countryPatientsInformation():
    patientsList = getPatientsList()
    sumDaysOfSickness = 0
    for patient in patientsList:
        sumDaysOfSickness += convertToFloat(patient.get("days_between_pos_and_recovery"))
    print("Average number of days for recovery:", "%.2f" % (sumDaysOfSickness / len(patientsList)))