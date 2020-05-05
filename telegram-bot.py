import requests
import json
import math
import operator
apiKey = ''
geocodeRequest = 'https://maps.googleapis.com/maps/api/geocode/json?address='
keyCode = '&key='







import telegram
botKey = '' 
bot = telegram.Bot(token=botKey)

from telegram.ext import Updater
updater = Updater(token=botKey, use_context=True)
dispatcher = updater.dispatcher

import logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

from telegram.ext import CommandHandler

def initStartCommand(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text='Please reply to this message by keying in your address.')

    
initStartCommand_handler = CommandHandler('searchall', initStartCommand)
dispatcher.add_handler(initStartCommand_handler)

def getLatLng(googleMapResponseObj,inputAddress):
    if(googleMapResponseObj['status'] == "OK"):
        countryIndex = len(googleMapResponseObj['results'][0]['address_components'])
    if (countryIndex >=2):
        countryLongName = googleMapResponseObj['results'][0]['address_components'][countryIndex-2]['long_name']
    else:
        countryLongName = googleMapResponseObj['results'][0]['address_components'][countryIndex-1]['long_name']
    
    if (countryLongName == "Singapore"):
        lat = googleMapResponseObj['results'][0]['geometry']['location']['lat']
        lng = googleMapResponseObj['results'][0]['geometry']['location']['lng']
        return {'destLat':lat,'destLng':lng}
    else:
        inputAddress = inputAddress + 'Singapore'
        googleMapResponseObj = gMapHTTPRequest(inputAddress)
        if(googleMapResponseObj['status'] == "OK"):
            countryIndex = len(googleMapResponseObj['results'][0]['address_components'])
        if (countryIndex >=2):
            countryLongName = googleMapResponseObj['results'][0]['address_components'][countryIndex-2]['long_name']
        else:
            countryLongName = googleMapResponseObj['results'][0]['address_components'][countryIndex-1]['long_name']
        if (countryLongName == "Singapore"):
            lat = googleMapResponseObj['results'][0]['geometry']['location']['lat']
            lng = googleMapResponseObj['results'][0]['geometry']['location']['lng']
            return {'destLat':lat,'destLng':lng}
        if(googleMapResponseObj['status'] != "OK"):
            outputMessage = "Bro what you smoking? This place doesn't exist! Please try again with a different search term." + googleMapResponseObj['status']
            return outputMessage
        elif (googleMapResponseObj['results'][0]['address_components'][len(googleMapResponseObj['results'][0]['address_components'])-2]['long_name'] != "Singapore"):
            formattedAddress = googleMapResponseObj['results'][0]['formatted_address']
            outputMessage = "Yo bro your search result resides in " + formattedAddress + ". Please try again with a different search term."
            return outputMessage


def gMapHTTPRequest(inputAddress):
    googleHttpRequest = geocodeRequest + inputAddress + keyCode + apiKey
    googleMapResponseObj = requests.post(googleHttpRequest).text
    googleMapResponseObj = json.loads(googleMapResponseObj)
    return googleMapResponseObj

def getDistancefromXYcoord(p1,p2):
    dist = math.sqrt(((p1[0]-p2[0])**2)+((p1[1]-p2[1])**2))
    return dist
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
def returnNearestCarpark(carparkDB,destLatLngObj):
    #for testing, comment 3 lines below
    destLat = destLatLngObj["destLat"]
    destLng = destLatLngObj["destLng"]
    print("ok1")
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
    return nearestCarpark

def matchAndSendCarPark(destLatLngObj):
    print("ok2")
    carparkDB = open('combinedCarparkDB.txt','r')
    carparkDB = json.loads(carparkDB.read())
    nearestCarpark = returnNearestCarpark(carparkDB,destLatLngObj)
    return nearestCarpark

def sendAddress(update, context):
    inputAddress = update.message.text
    inputAddress = inputAddress.replace(' ','+').lower()
    symbols = '(),'
    for symbol in symbols:
        inputAddress = inputAddress.replace(symbol,'')
    googleMapResponseObj = gMapHTTPRequest(inputAddress)
    latLngOrRejectMessage = getLatLng(googleMapResponseObj,inputAddress)
    print(latLngOrRejectMessage)
    if type(latLngOrRejectMessage) == dict:
        print("ok3")
        destLatLngObj = latLngOrRejectMessage
        outputMessage = matchAndSendCarPark(destLatLngObj)
        print(outputMessage)
    elif type(latLngOrRejectMessage) == str:
        outputMessage = latLngOrRejectMessage
    
    context.bot.send_message(chat_id=update.effective_chat.id, text=outputMessage)


    # context.bot.send_message(chat_id=update.effective_chat.id, text=outputMessage)

#API for filter https://python-telegram-bot.readthedocs.io/en/latest/telegram.ext.filters.html#module-telegram.ext.filters
#API for MessageHandler https://python-telegram-bot.readthedocs.io/en/latest/telegram.ext.messagehandler.html
#API for telegram.Message https://python-telegram-bot.readthedocs.io/en/latest/telegram.message.html
from telegram.ext import MessageHandler, Filters
sendAddress_handler = MessageHandler(Filters.reply, sendAddress) #Filters can be combined using bitwise operators (& for and, | for or, ~ for not). 
dispatcher.add_handler(sendAddress_handler)

updater.start_polling()



googleParam = 'https://www.google.com/maps/search/?api=1&query='
carparkNum = 0

for num, carpark in enumerate(carpark_details):
    carparkNum = num + 1
    carparkDistToDestArray[num] = carpark['distance_from_dest']
    carparkRatesArray[num] = carpark['carpark_rates']
    carparkAddressArray[num] = carpark['address']
    carparkAddressArray[num] = carparkAddressArray[num].replace(' ','+').lower()
    symbols = '(),'
    for symbol in symbols:
        carparkAddressArray[num] = carparkAddressArray[num].replace(symbol,'')
    messageContent[num] = 'Carpark ' + carparkNum + ' Details: ' + '\n' + 'Distance from Destination: ' + carparkDistToDestArray[num] + '\n' + 'Carpark Rates: '+ carparkRatesArray[num] + '\n' + 'Google Map Link: '+ '\n' + googleParam + carparkAddressArray[num] + '\n\n'


for num in range(len(carparkAddressArray)):
    if (carparkAddressArray[num] == carparkAddressArray[num + 1]):
        del messageContent[num+1]
outputMessage = messageContent[0:3]
