# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import pandas as pd
import os
import csv
import re
import numpy as np

import matplotlib.pyplot as plt

import requests
import json

print("Hello world! \n");
"""
module = "MSCI"
symbol = "ACWI.R"
item = "PI$"
date = "20180726"
chgopt = "CHG-1D"

output = os.system("autoserve.plx " + module + "," + symbol + "," + item + "," + date + "," + chgopt)

print (("autoserve.plx " + module + "," + symbol + "," + item + "," + date + "," + chgopt))

a = np.linspace(0, 10, 100)
b = np.exp(-a)
plt.plot(a,b)
plt.show()
"""
r = requests.get('https://api.iextrading.com/1.0/stock/spy/chart/5y')
#r = requests.get('https://api.iextrading.com/1.0/stock/eri/chart/dynamic')

json_data = json.loads(r.text)
#json_data = json_data['data']
print(json_data[0]['close'])

df = pd.DataFrame(json_data)
df = df.set_index('date')

#keys = list(json_data[0].keys)

size = len(json_data)
print(size)

for i in range(len(json_data)):
	
	#if not json_data[i]['close']:
	if not 'close' in json_data[i]:
		json_data[i]['close']=json_data[i-1]['close'] #trail data if missing
	print (json_data[i]['date']," = ",json_data[i]['close'])
	



closeprices = [json_data[i]['close'] for i in range(len(json_data))]
timestamps = [json_data[i]['date'] for i in range(len(json_data))]

a = range(len(json_data)) 
#np.linspace(0,np.amax(closeprices),1000)
plt.plot(a,closeprices)

