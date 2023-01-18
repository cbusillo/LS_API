import requests
import os
import config.secret as secret
import time

print("Importing {}...".format(os.path.basename(__file__)))

accoundID = 111082 #LS account number
accessToken = secret.accessToken #imported secret info for API

urls = {
    #URLS for LS API
    "access": "https://cloud.lightspeedapp.com/oauth/access_token.php",
    "item": f"https://api.lightspeedapp.com/API/V3/Account/{accoundID}/Item.json",
    "itemPut": f"https://api.lightspeedapp.com/API/V3/Account/{accoundID}/Item/{{itemID}}.json",
    "itemMatrix": f"https://api.lightspeedapp.com/API/V3/Account/{accoundID}/ItemMatrix.json",
    "customer": f"https://api.lightspeedapp.com/API/V3/Account/{accoundID}/Customer.json",
    "customerPut": f"https://api.lightspeedapp.com/API/V3/Account/{accoundID}/Customer/{{customerID}}.json"
    }

accessHeader = {
    "Authorization": ""
    }

#generate access requirements
def generate_access():
    response = requests.post(urls["access"], data=accessToken)
    accessHeader["Authorization"] = "Bearer " + response.json()["access_token"]
    
def get_data(currenturl, currentParams):
    response = requests.get(currenturl, headers=accessHeader, params=currentParams) 
    
    while response.status_code == 429:
            print (f"\nDelaying for rate limit. Level:{response.headers['x-ls-api-bucket-level']} Retry After:{response.headers['retry-after']}", end='\r')
            time.sleep(int(response.headers['retry-after']) + 1)
            response = requests.get(currenturl,headers=accessHeader, params=currentParams) 
        
    if response.status_code == 401:
        generate_access()
        response = requests.get(currenturl,headers=accessHeader, params=currentParams) 
    
    if response.status_code != 200:
        print(f"Received bad status code {currentParams}: " + response.text)
    return response

def put_data(currenturl, currentData):
    response = requests.put(currenturl,headers=accessHeader, json=currentData) 
    while response.status_code == 429:
        print (f"\nDelaying for rate limit. Level:{response.headers['x-ls-api-bucket-level']} Retry After:{response.headers['retry-after']}", end='\r')
        time.sleep(int(response.headers['retry-after']) + 1)
        response = requests.put(currenturl,headers=accessHeader, json=currentData) 
   
    if response.status_code == 401:
        generate_access()
        response = requests.put(currenturl,headers=accessHeader, json=currentData) 
   
    if response.status_code != 200:
        print(f"Received bad status code on {currentData}: " + response.text)