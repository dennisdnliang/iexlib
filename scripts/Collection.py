# -*- coding: utf-8 -*-
"""
Created on Mon Sep  3 00:38:55 2018

@author: Dennis
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

r = requests.get('https://api.iextrading.com/1.0/stock/market/collection/sector?collectionName=Technology')
#r = requests.get('https://api.iextrading.com/1.0/stock/eri/chart/dynamic')

json_data = json.loads(r.text)
#json_data = json_data['data']

df = pd.DataFrame(json_data)
df = df.set_index('symbol')

print(df.loc['AAPL'])

full = pd.DataFrame()

for i in df.index:
	print('fetching ' + i + ' via https://api.iextrading.com/1.0/stock/'+i+'/company')
	r = requests.get('https://api.iextrading.com/1.0/stock/'+i+'/company')
	json_data = json.loads(r.text)
	df2 = pd.DataFrame(json_data)
	frames = [full, df2]
	full = pd.concat(frames)
	if i == "SLP":
		break
	

r = requests.get('https://api.iextrading.com/1.0/stock/aapl/company')
json_data = json.loads(r.text)
#json_data = json_data['data']

df2 = pd.DataFrame(json_data)

"""
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

"""