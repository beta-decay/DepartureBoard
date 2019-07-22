# Run this program in the background at the same time as index.htm 

import requests, time, json
from requests.auth import HTTPBasicAuth

# Choose a station to display using its three-letter code
station = "DHM"

# Your Realtime Trains API username and password here
username = ""
password = ""

while True:
    try:
        response = requests.get("https://api.rtt.io/api/v1/json/search/"+station, auth=HTTPBasicAuth(username, password)).text
        data = json.loads(response)
        
        output = {
            "services": [],
            "nextpassing": False
        }
        
        i = 0
        
        while len(output["services"]) < 3:
            if data["services"] == None:
                output["services"] = [{},{},{}]
            else:
                try:
                    passTest =  data["services"][i]["locationDetail"]["isCall"]
                except IndexError:
                    passTest = True
                    
                if not passTest:
                        if i == 0:
                            output["nextpassing"] = True
                else:
                    try:
                        test2 = data["services"][i]["isPassenger"] and data["services"][i]["serviceType"] == "train"
                    except IndexError:
                        test2 = True
                    if test2:
                        if len(output["services"]) == 0:
                            output["services"].append({})
                            
                            try:
                                output["services"][-1]["station"] = data["services"][i]["locationDetail"]["destination"][0]["description"]
                                
                                if "cancelReasonCode" in data["services"][i]["locationDetail"].keys():
                                    output["services"][-1]["time"] = data["services"][i]["locationDetail"]["gbttBookedArrival"][:2] + ":" + data["services"][i]["locationDetail"]["gbttBookedArrival"][2:]
                                    
                                    expectedTime = "Cancelled"
                                elif "gbttBookedArrival" in data["services"][i]["locationDetail"].keys():
                                    output["services"][-1]["time"] = data["services"][i]["locationDetail"]["gbttBookedArrival"][:2] + ":" + data["services"][i]["locationDetail"]["gbttBookedArrival"][2:]
                                    
                                    expectedTime = data["services"][i]["locationDetail"]["realtimeArrival"][:2] + ":" + data["services"][i]["locationDetail"]["realtimeArrival"][2:]
                                    
                                else:
                                    output["services"][-1]["time"] = data["services"][i]["locationDetail"]["gbttBookedDeparture"][:2] + ":" + data["services"][i]["locationDetail"]["gbttBookedDeparture"][2:]
                                    
                                    expectedTime = data["services"][i]["locationDetail"]["realtimeDeparture"][:2] + ":" + data["services"][i]["locationDetail"]["realtimeDeparture"][2:]
                                
                                if expectedTime == output["services"][-1]["time"]:
                                    output["services"][-1]["expected"] = "On time"
                                elif expectedTime == "Cancelled":
                                    output["services"][-1]["expected"] = "Cancelled"
                                else:
                                    output["services"][-1]["expected"] = "Expt "+expectedTime

                                if expectedTime == "Cancelled":
                                        output["services"][-1]["cancelled"] = True
                                        output["services"][-1]["cancelReason"] = "Cancelled due to "+data["services"][i]["locationDetail"]["cancelReasonLongText"]
                                else:
                                        # Get next stations
                                        date = data["services"][i]["runDate"].replace("-","/") 
                                        serviceUid = data["services"][i]["serviceUid"]
                                        
                                        time.sleep(30)
                                        stationResponse = requests.get("https://api.rtt.io/api/v1/json/service/"+serviceUid+"/"+date, auth=HTTPBasicAuth(username, password)).text
                                        stationData = json.loads(stationResponse)
                                        
                                        afterCurrent = False
                                        
                                        output["services"][-1]["callingAt"] = []
                                        #print(stationData["locations"])
                                        for call in stationData["locations"]:
                                            if afterCurrent:
                                                output["services"][-1]["callingAt"].append({
                                                    "station": call["description"],
                                                    "expected": call["realtimeArrival"][:2] + ":" + call["realtimeArrival"][2:]
                                                })
                            
                                            else:
                                                if call["crs"] == station:
                                                    afterCurrent = True
                                                    
                                        output["services"][-1]["atoc"] = stationData["atocName"]
                                        output["services"][-1]["cancelled"] = False
                                                                            
                            except IndexError:
                                pass
                        else:
                            output["services"].append({})
                            
                            try:                    
                                output["services"][-1]["station"] = data["services"][i]["locationDetail"]["destination"][0]["description"]

                                if "cancelReasonCode" in data["services"][i]["locationDetail"].keys():
                                     output["services"][-1]["time"] = data["services"][i]["locationDetail"]["gbttBookedArrival"][:2] + ":" + data["services"][i]["locationDetail"]["gbttBookedArrival"][2:]

                                     expectedTime = "Cancelled"
                                elif "gbttBookedArrival" in data["services"][i]["locationDetail"].keys():
                                    output["services"][-1]["time"] = data["services"][i]["locationDetail"]["gbttBookedArrival"][:2] + ":" + data["services"][i]["locationDetail"]["gbttBookedArrival"][2:]
                                    
                                    expectedTime = data["services"][i]["locationDetail"]["realtimeArrival"][:2] + ":" + data["services"][i]["locationDetail"]["realtimeArrival"][2:]
                                    
                                else:
                                    output["services"][-1]["time"] = data["services"][i]["locationDetail"]["gbttBookedDeparture"][:2] + ":" + data["services"][i]["locationDetail"]["gbttBookedDeparture"][2:]
                                    
                                    expectedTime = data["services"][i]["locationDetail"]["realtimeDeparture"][:2] + ":" + data["services"][i]["locationDetail"]["realtimeDeparture"][2:]

                                if expectedTime == "Cancelled":
                                    output["services"][-1]["expected"] = "Cancelled"
                                        
                                elif expectedTime == output["services"][-1]["time"]:
                                    output["services"][-1]["expected"] = "On time"
                                
                                else:
                                    output["services"][-1]["expected"] = "Expt "+expectedTime
                                    
                            except IndexError:
                                pass
                i += 1
            
        with open("destinationData.json","w") as f:
            f.write(json.dumps(output))
        
        print("Done")
        time.sleep(30)
    except requests.exceptions.ConnectionError:
        print("Exception encountered")
        time.sleep(60)
