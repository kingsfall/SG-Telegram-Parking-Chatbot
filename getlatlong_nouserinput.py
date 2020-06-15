# -*- coding: utf-8 -*-
"""
Created on Mon Mar  2 22:38:31 2020

@author: allen
"""


import argparse
import requests
import json
import math
import operator

def conv4326ToXY3414(Lat,Lng):
    #This function converts google's destLat & destLng to 4326 to 3414
    #More info: https://docs.onemap.sg/#4326-wgs84-to-3857
    urlOnemapHeadTo3414 = "https://developers.onemap.sg/commonapi/convert/4326to3414?"
    latlng = "latitude=" + str(Lat) + "&longitude=" + str(Lng)
    urlOnemapTo3414 = urlOnemapHeadTo3414 + latlng
    fileobj = requests.get(urlOnemapTo3414)
    convToXY3414 = json.loads(fileobj.text)
    p1 = [convToXY3414["X"],convToXY3414["Y"]]
    return p1

def getDistancefromXYcoord(p1,p2):
    dist = math.sqrt(((p1[0]-p2[0])**2)+((p1[1]-p2[1])**2))
    return dist

def parseUserInput():
    parser = argparse.ArgumentParser()
    parser.add_argument("destLat", type=float)
    parser.add_argument("destLng", type=float)
    args = parser.parse_args()

    destLat = args.destLat
    destLng = args.destLng
    destLatLngObj = {
        "destLat" : destLat,
        "destLng" : destLng
    }
    return destLatLngObj

def httpRequestForHDBCarpark():
    #website: https://data.gov.sg/dataset/hdb-carpark-information
    urlCarpark = "https://data.gov.sg/api/action/datastore_search?resource_id=139a3035-e624-4f56-b63f-89ae28d4ae4c&limit=10000"
    fileobj = requests.get(urlCarpark)
    carparkDB = json.loads(fileobj.text) #this function should only run once every period and store in a db
    with open('HDBCarpark_DB.txt', 'w') as my_data_file:
        my_data_file.write(fileobj.text)
    return

def httpRequestForCarparkShoppingMallAndHotel():
    urlCarpark = "https://data.gov.sg/api/action/datastore_search?resource_id=85207289-6ae7-4a56-9066-e6090a3684a5&limit=10000"
    fileobj = requests.get(urlCarpark)
    carparkDB = json.loads(fileobj.text) #this function should only run once every period and store in a db
    with open('CarparkShoppingMallAndHotel(original).txt', 'w') as my_data_file:
        my_data_file.write(fileobj.text)
    return

def httpRequestForURACarpark():
    urlCarpark = "https://data.gov.sg/api/action/datastore_search?resource_id=5a8f7572-0d46-4ce5-be71-a7081d2c42b0&limit=10000"
    fileobj = requests.get(urlCarpark)
    carparkDB = json.loads(fileobj.text) #this function should only run once every period and store in a db
    with open('URACarpark_DB.txt', 'w') as my_data_file:
        my_data_file.write(fileobj.text)
    return

def fromTXTHDBCarpark():
    carparkDB = open('HDBCarpark_DB.txt', 'r')
    carparkDB = json.loads(carparkDB.read())
    return carparkDB

def fromTXTCarparkShoppingMallAndHotel():
    carparkDB = open('CarparkShoppingMallAndHotel_DB.txt', 'r')
    carparkDB = json.loads(carparkDB.read())
    return carparkDB

def fromTXTCarparkURA():
    carparkDB = open('URACarpark_DB(Motor Car).txt', 'r')
    carparkDB = json.loads(carparkDB.read())
    return carparkDB

#depreciated
def insertXYCoordToCarparkDB(carparkDB):
    #Key in your Google API key here
    apiKey = 'YOUR GOOGLE API KEY'
    geocodeRequest = 'https://maps.googleapis.com/maps/api/geocode/json?address='
    keyCode = '&key='
    noresultsIDArray = []
    for num in range(len(carparkDB["result"]["records"])):
        print(num)
        inputAddress = carparkDB["result"]["records"][num]["carpark"]
        inputAddress = inputAddress.replace(" ","+")
        googleHttpRequest = geocodeRequest + inputAddress + keyCode + apiKey
        googleMapResponseObj = requests.post(googleHttpRequest).text
        googleMapResponseObj = json.loads(googleMapResponseObj)
        if googleMapResponseObj["status"]=='ZERO_RESULTS':
            noresultsIDArray.append(carparkDB["result"]["records"][num]["_id"])
            print(noresultsIDArray)
        else:
            Lat = googleMapResponseObj["results"][0]["geometry"]["location"]["lat"]
            Lng = googleMapResponseObj["results"][0]["geometry"]["location"]["lng"]
            p1 = conv4326ToXY3414(Lat,Lng)
            xyCoordObj = {
                "x_coord": p1[0],
                "y_coord": p1[1]
            }
            carparkDB["result"]["records"][num].update(xyCoordObj)
    
    # print(carparkDB["result"]["records"])
    carparkDBtoStr = json.dumps(carparkDB)
    with open('CarparkShoppingMallAndHotel_DB.txt', 'w') as my_data_file:
        my_data_file.write(carparkDBtoStr)

    # loadedtxt = open('data.txt', 'r')
    # loadedtxt = json.loads(loadedtxt.read())
    # print(type(loadedtxt))

    noresultsIDArray = json.dumps(noresultsIDArray)
    with open('noresultsIDArray.txt', 'w') as my_data_file:
        my_data_file.write(noresultsIDArray)
    return

#this 2 are run together after function httpRequestForCarparkShoppingMallAndHotel() and then insertXYCoordToCarparkDB(carparkDB). CarparkDB for shopping mall is ready to be used for nearest carpark
def deleteNoGoogleResultRoutine(notepadRead,notepadWrite,delArrayID):
    carparkDB = open(notepadRead, 'r')
    carparkDB = json.loads(carparkDB.read())

    for index in range(len(delArrayID)):
        idValue = delArrayID[index]
        for num in range(len(carparkDB["result"]["records"])):
            if carparkDB["result"]["records"][num]["_id"] == idValue:
                print(num)
                print(carparkDB["result"]["records"][num])
                del carparkDB["result"]["records"][num]
                break

    carparkDB = json.dumps(carparkDB)
    with open(notepadWrite, 'w') as my_data_file:
        my_data_file.write(carparkDB)    
    return
def fillXYCoordSubRoutine(carparkDB,carparkKeyValue,noresultsIDArray,notepadWrite,notepadWriteNoResult1stArray,notepadWriteNoResult2ndArray):
    apiKey = 'YOUR GOOGLE API KEY'
    geocodeRequest = 'https://maps.googleapis.com/maps/api/geocode/json?address='
    keyCode = '&key='

    noresultsIDArray2ndRound = []
    if len(noresultsIDArray) > 0:
        for index in range(len(noresultsIDArray)):
            print("this should not be running!")
            idValue = noresultsIDArray[index]
            for num in range(len(carparkDB["result"]["records"])):
                if carparkDB["result"]["records"][num]["_id"] == idValue:
                    inputAddress = carparkDB["result"]["records"][num][carparkKeyValue]
                    inputAddress = inputAddress.replace(" ","+")
                    googleHttpRequest = geocodeRequest + inputAddress + keyCode + apiKey
                    googleMapResponseObj = requests.post(googleHttpRequest).text
                    googleMapResponseObj = json.loads(googleMapResponseObj)

                    if googleMapResponseObj["status"]=='ZERO_RESULTS':
                        noresultsIDArray2ndRound.append(carparkDB["result"]["records"][num]["_id"])
                        print(noresultsIDArray2ndRound)
                    else:
                        Lat = googleMapResponseObj["results"][0]["geometry"]["location"]["lat"]
                        Lng = googleMapResponseObj["results"][0]["geometry"]["location"]["lng"]
                        p1 = conv4326ToXY3414(Lat,Lng)
                        xyCoordObj = {
                            "x_coord": p1[0],
                            "y_coord": p1[1]
                        }
                        carparkDB["result"]["records"][num].update(xyCoordObj)
    else:
        for num in range(len(carparkDB["result"]["records"])):
            inputAddress = carparkDB["result"]["records"][num][carparkKeyValue]
            inputAddress = inputAddress.replace(" ","+")
            googleHttpRequest = geocodeRequest + inputAddress + keyCode + apiKey
            googleMapResponseObj = requests.post(googleHttpRequest).text
            googleMapResponseObj = json.loads(googleMapResponseObj)

            if googleMapResponseObj["status"]=='ZERO_RESULTS':
                noresultsIDArray.append(carparkDB["result"]["records"][num]["_id"])
                print(noresultsIDArray)
            else:
                Lat = googleMapResponseObj["results"][0]["geometry"]["location"]["lat"]
                Lng = googleMapResponseObj["results"][0]["geometry"]["location"]["lng"]
                p1 = conv4326ToXY3414(Lat,Lng)
                xyCoordObj = {
                    "x_coord": p1[0],
                    "y_coord": p1[1]
                }
                carparkDB["result"]["records"][num].update(xyCoordObj)
                print(carparkDB["result"]["records"][num])    
    
    carparkDB = json.dumps(carparkDB)
    with open(notepadWrite, 'w') as my_data_file:
        my_data_file.write(carparkDB)

    if len(noresultsIDArray) > 0:
        noresultsIDArray = json.dumps(noresultsIDArray)
        with open(notepadWriteNoResult1stArray, 'w') as my_data_file:
            my_data_file.write(noresultsIDArray)

    if len(noresultsIDArray2ndRound) > 0:
        with open(notepadWriteNoResult2ndArray, 'w') as my_data_file:
            my_data_file.write(noresultsIDArray2ndRound)

    return
def fillXYCoordMain(notepadRead,notepadWrite,notepadWriteNoResult1stArray,carparkKeyValue,notepadWriteNoResult2ndArray):
    carparkDB = open(notepadRead, 'r')
    carparkDB = json.loads(carparkDB.read())
    noresultsID1stArray = []
    #line below should be run at the start and then comment out
    # fillXYCoordSubRoutine(carparkDB,carparkKeyValue,noresultsID1stArray,notepadWrite,notepadWriteNoResult1stArray,notepadWriteNoResult2ndArray)

    #3 lines below should be run after line at the top
    delArrayID = open(notepadWriteNoResult2ndArray, 'r')
    delArrayID = json.loads(delArrayID.read())
    deleteNoGoogleResultRoutine(notepadRead,notepadWrite,delArrayID)
    
    return
# fillXYCoordMain("URACarpark_DB(Motor Car).txt","URACarpark_DB(Motor Car)(XY).txt","noresultsIDArrayURA1st.txt","ura_carpark_name","noresultsIDArrayURA2nd.txt")
#for running delete code
# fillXYCoordMain("URACarpark_DB(Motor Car)(XY).txt","URACarpark_DB(Motor Car)(XY)- After Delete.txt","noresultsIDArrayURA1st.txt","ura_carpark_name","noresultsIDArrayURA2nd.txt")


#this 3 function below will run together to filter motorcar carparks from original database
def loop(carparkDB,key,value):
    print(len(carparkDB["result"]["records"]))
    for index, carparks in enumerate(carparkDB["result"]["records"]):
        if type(value) == str:
            if value not in carparks[key]:
                # print(carparkDB["result"]["records"][index])
                del carparkDB["result"]["records"][index]
                bDel = 1
            else:
                bDel = 0
        else:
            if  carparks[key] == str(value):
                print(carparkDB["result"]["records"][index])
                del carparkDB["result"]["records"][index]
                bDel = 1
            else:
                bDel = 0

    print(len(carparkDB["result"]["records"]))

    obj = {
        "carparkDB": carparkDB,
        "bDel": bDel
    }
    return obj
def filterURACarpark(notepadRead,key,value,notepadWrite):
    carparkDB = open(notepadRead, 'r')
    carparkDB = json.loads(carparkDB.read())
    bDel = 1
    while bDel != 0:
        obj = loop(carparkDB,key,value)
        carparkDB = obj["carparkDB"]
        bDel = obj["bDel"]

    carparkDB = json.dumps(carparkDB)
    with open(notepadWrite, 'w') as my_data_file:
        my_data_file.write(carparkDB)
    return
def filterURACarparkOverall():
    filterURACarpark('URACarpark_DB.txt',"type_of_lot","Motor Car",'URACarpark_DB(Motor Car).txt')
    filterURACarpark('URACarpark_DB(Motor Car).txt',"number_of_lots",0,'URACarpark_DB(Motor Car).txt')
    return

def combineAllCarparksDB():
    carparkDBURA = open('URACarpark_DB(Motor Car)(XY)- After Delete.txt', 'r')
    carparkDBURA = json.loads(carparkDBURA.read())

    carparkDBHDB = open('HDBCarpark_DB.txt', 'r')
    carparkDBHDB = json.loads(carparkDBHDB.read())

    carparkDBSPM = open('CarparkShoppingMallAndHotel_DB(XY).txt', 'r')
    carparkDBSPM = json.loads(carparkDBSPM.read())

    combinedDB = {
        "result": {"records":[]}
    }


    combinedDB["result"]["records"].extend(carparkDBURA["result"]["records"])
    combinedDB["result"]["records"].extend(carparkDBHDB["result"]["records"])
    combinedDB["result"]["records"].extend(carparkDBSPM["result"]["records"])
    combinedDB["result"]["total_records"] = len(combinedDB["result"]["records"])

    combinedDB = json.dumps(combinedDB)
    with open("combinedCarparkDB.txt", 'w') as my_data_file:
        my_data_file.write(combinedDB)
    return

def returnNearestCarpark(carparkDB):
    #for testing, comment 3 lines below
    destLatLngObj = parseUserInput()
    destLat = destLatLngObj["destLat"]
    destLng = destLatLngObj["destLng"]
    
    # #for testing    
    # destLat = 1.3602298
    # destLng = 103.8595684
    p1 = conv4326ToXY3414(destLat,destLng)

    #Long = X, Lat = Y
    #This function finds the distance between p2 (x,y coord for HDB carpark DB) with p1 (destination's x,y coord) 
    distDict = {}
    for num in range(len(carparkDB["result"]["records"])):
        xCoord2 = float(carparkDB["result"]["records"][num]["x_coord"])
        yCoord2 = float(carparkDB["result"]["records"][num]["y_coord"])
        p2 = [xCoord2, yCoord2]
        dist = getDistancefromXYcoord(p1,p2)
        distDict[num] = round(dist)
    
    #This function sort distance (value) with their carpark (keys) with smallest distance at the top 
    distDict = sorted(distDict.items(), key=operator.itemgetter(1))
    distDict = dict((x, y) for x, y in distDict)
    #distKeysArray will store only the keys to be used later to reference and get the particular carpark name
    distKeysArray = list(distDict.keys())
    

    nearestCarpark = {"carpark_details" : {}}
    for num in range(0,5):
        index = distKeysArray[num]
        #For getting carpark address
        if "address" in carparkDB["result"]["records"][index]:
            carparkAddress = str(carparkDB["result"]["records"][index]["address"])
            #to also additionally get HDB parking rates
            carparkRate = "$0.60 or $1.20 per half-hour* (More info here: https://www.hdb.gov.sg/cs/infoweb/car-parks/short-term-parking/short-term-parking-charges)"
        elif "carpark" in carparkDB["result"]["records"][index]:
            carparkAddress = str(carparkDB["result"]["records"][index]["carpark"])
            #to also additionally get SPM parking rates
            carparkRate1 = carparkDB["result"]["records"][index]["weekdays_rate_1"]
            carparkRate2 = carparkDB["result"]["records"][index]["weekdays_rate_2"]
            
            if (carparkRate2 == "-" or carparkRate2 == carparkRate1):
                carparkRate = carparkRate1
            else:
                carparkRate = carparkRate1 + "AND" + carparkRate2

        elif "ura_carpark_name" in carparkDB["result"]["records"][index]:
            carparkAddress = str(carparkDB["result"]["records"][index]["ura_carpark_name"])
            #to also additionally get URA parking rates
            carparkRate = "$0.60 or $1.20 per half-hour* (More info here: https://www.ura.gov.sg/Corporate/Car-Parks/Short-Term-Parking/Parking-coupons"
            
        # For calculating distance
        distanceFromDest = str(distDict.get(index))
        xCoord = float(carparkDB["result"]["records"][index]["x_coord"])
        yCoord = float(carparkDB["result"]["records"][index]["y_coord"])
        urlOnemapTo3857 = "https://developers.onemap.sg/commonapi/convert/3414to3857?"
        XandY = "X=" + str(xCoord) + "&Y=" + str(yCoord)
        urlOnemapTo3857 = urlOnemapTo3857 + XandY
        fileobj = requests.get(urlOnemapTo3857)
        convTo3857 = json.loads(fileobj.text)
        lng = convTo3857["X"]
        lat = convTo3857["Y"]        
        nearestCarpark["carpark_details"][num] = {"address": str(carparkAddress), "lat": str(lat), "lng": str(lng), "distance_from_dest": str(distanceFromDest+'m'),"carpark_rates": str(carparkRate)}

    nearestCarpark = json.dumps(nearestCarpark).replace('\'', '"')
    print(nearestCarpark)
    return

carparkDB = open('combinedCarparkDB.txt','r')
carparkDB = json.loads(carparkDB.read())
returnNearestCarpark(carparkDB)



# this 2 function should be run periodically once every month to refresh data from govtech
# httpRequestForHDBCarpark()
# httpRequestForCarparkShoppingMallAndHotel()
