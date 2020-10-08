"""
The program converts a url to a JSON list
"""

import requests

# get a url and return a full JSON list
def getList(url):
    fullList = []
    partList = [0]
    i = 0
    while(len(partList) != 0):
        newUrl = url + '&limit=100000&offset=' + str(i * 100000)
        obj = requests.get(newUrl)
        Dict = obj.json()
        try:
            partList = Dict.get('result').get('records')
        # means the list in the url is over
        except:
            break
        for index in partList:
            fullList.append(index)
        i += 1
    return fullList
