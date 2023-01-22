"""Connect to sickw API"""
import os
import requests

# from modules import load_config as config
from modules import load_config as config

# from modules import load_config as config
# import load_config as config

print(f"Importing {os.path.basename(__file__)}...")


def get_data(serial_number, service):
    """Get requested data from Sickw API"""
    current_params = {"imei": serial_number, "service": service, "key": config.SICKW_API_KEY, "format": "JSON"}
    headers = {"User-Agent": "My User Agent 1.0"}
    response = requests.get("https://sickw.com/api.php", params=current_params, headers=headers, timeout=60)
    print(response.text)
    return response


# get_data("354442067957452", "103")

"""
Verizon 
Variable "service" with value "9" Tool: VERIZON USA STATUS - PRO | Price: 0.05 USD
{
  "result": "<img src=\"https://ss7.vzw.com/is/image/VerizonWireless/apple-iphone-6-plus-gold?$device-med$\"><br />
  Model: Apple A1522 iPhone 6 Plus 16GB in Gold<br />
  IMEI: 354442067957452<br />
  ESN Status: The phone associated with the Device ID you entered is not compatible with the Verizon Wireless network.<br />
  Error Code: Device Not Compatible<br />
  Part Number: MGCM2LL/A<br />
  Device SKU: SKU1200122<br />",
  "imei": "354442067957452",
  "balance": "57.42",
  "price": "0.05",
  "id": "41603836",
  "status": "success"
}

Variable "service" with value "16" Tool: T-MOBILE USA STATUS - PRO | Price: 0.08 USD
{
  "result": "
  IMEI: 354442067957452<br>
  Model Name: iPhone 6 Plus<br>
  Model Brand: Apple<br>
  eSIM Supported: No<br>
  ESN Status: <font color=\"red\">Blocked</font><br>
  Blacklist Reason: Reported stolen by a T-Mobile customer<br>",
  "imei": "354442067957452",
  "balance": "57.34",
  "price": "0.08",
  "id": "41603955",
  "status": "success"
}

Variable "service" with value "54" Tool: GSMA WW BLACKLIST STATUS | Price: 0.04 USD
{
  "result": "
  IMEI: 354442067957452<br>
  Manufacturer: Apple<br>
  Marketing Name: iPhone 6 Plus<br>
  Model: iPhone 6 Plus (A1524)<br>
  Blacklist Status: Blacklisted<br>
  Blacklist Reason: Reported stolen by a T-Mobile customer<br>",
  "imei": "354442067957452",
  "balance": "57.19",
  "price": "0.04",
  "id": "41604046",
  "status": "success"
}


Variable "service" with value "103" Tool: iPHONE CARRIER - SIMPLE | Price: 0.10 USD
{
  "result": "
  Model: iPhone 6 Plus 16GB Gold MM-TD [A1524] [iPhone7,1]<br />
  Description: SVC IPHONE 6 PLUS MM-TD 16GB GOLD CI/AR<br />
  IMEI Number: 354442067957452<br />
  Serial Number: F2NNWGUKG5QT<br />
  MEID Number: 35444206795745<br />
  Estimated Purchase Date: December 10, 2014<br />
  Warranty Status: Out Of Warranty<br />
  Device Age: 8 Years, 1 Month and 11 Days<br />
  Replaced Device: No<br />
  Device Status: Replacement<br />
  Locked Carrier: US Sprint/T-Mobile Locked Policy<br />
  Country: United States<br />
  SIM-Lock: <span style=\"COLOR:red\">Locked</span>",
  "imei": "354442067957452",
  "balance": "57.09",
  "price": "0.10",
  "id": "41604131",
  "status": "success"
}
"""
