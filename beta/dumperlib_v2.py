# -*- coding: utf-8 -*-
"""
Created on Sat Sep 22 13:37:21 2018

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
#import urllib
#import urllib.reqests
#import urllib.error
import time

#######################

requesttimeout = 10

##########SUB##########

def getdatadatelist (symbol = "AAPL"): #uses stock full charts to create trading days list
	try:
		fychart = requests.get("https://api.iextrading.com/1.0/stock/"+symbol+"/chart/5y",timeout=requesttimeout)
	except:
		print("Failed to fetch "+symbol+" 5Y Chart")
		return 0
	json_data = json.loads(fychart.text)
	df = pd.DataFrame(json_data)
	datelist = list(df["date"])
	datelist = [i.replace("-","") for i in datelist]
	return datelist

def getsymlist ():
	try:
		allsymlist = requests.get("https://api.iextrading.com/1.0/ref-data/symbols",timeout=requesttimeout)
	except:
		print("Failed to fetch symbols list")
		return 0
	symlistjson = json.loads(allsymlist.text)
	symdf = pd.DataFrame(symlistjson)
	#symdf = symdf.set_index("symbol")
	symlist = list(symdf["symbol"])
	return symlist

def url2df (url="https://api.iextrading.com/1.0/ref-data/symbols"):
	try:
		r = requests.get(url,timeout=requesttimeout)
	except:
		print("Failed to fetch "+url)
		return 0
	json_data = json.loads(r.text)
	#df = pd.DataFrame(json_data)
	try:
		df = pd.DataFrame(json_data)
	except ValueError:
		df = pd.DataFrame(data=json_data, index=[json_data["symbol"]] )
	return df

def findstartdate_sub (datelist, testurl="https://api.iextrading.com/1.0/stock/aapl/chart/date/"): #list must be sorted
	#print("findstartdatecalled" + " ".join(datelist))
	if len(datelist) <= 2:
		for i in range(len(datelist)):
			url = testurl+datelist[i]
			if testresponse(url):
				#print("url is " + url)
				break
		return datelist[i]
	else: 
		testindex = int(len(datelist)/2)
		url = testurl+datelist[testindex]
		#print("testindex " + str(testindex))
		if testresponse(url):
			return findstartdate(datelist[:testindex+1], testurl)
		else:
			return findstartdate(datelist[testindex:], testurl)


def findstartdate (datelist, testurl="https://api.iextrading.com/1.0/stock/aapl/chart/date/"): #wrapper to sort list
	datelist.sort()
	urle = testurl+datelist[-1]
	if testresponse(urle):
		return findstartdate_sub(datelist)
	else:
		return 0
		
	
def testresponse (url):
	try:
		r = requests.get(url,timeout=requesttimeout)
	except:
		print("Failed to recieve any response")
		return 0
	#print(url)
	json_data = json.loads(r.text)
	if (json_data):
		return 1
	else:
		return 0
	
def download_file(url,fileloc,to=requesttimeout,redirect=True):
	try:
		r = requests.get(url, allow_redirects=redirect, timeout=to)
		with open(fileloc, 'wb') as f:
			f.write(r.content)
		del r
		return 1
	except:
		return 0
	
		
	
###############################################################################

def dumptofile (symlist, datatype, savelocation="RawFiles\\test", datelist='1', overwrite=0):
	
	t1=time.gmtime()
	tt1=time.time()
	
	begintime = time.strftime('%a, %d %b %Y %H:%M:%S GMT',t1)
	
	datatype = datatype.capitalize()
	
	print("Begin IEX "+datatype+" DB Dump at "+begintime)
	
	fileloc = savelocation+"\\"+datatype+"\\"
	
	logd = open(fileloc+".downloadlog.txt","a+")
	loge = open(fileloc+".errorlog.txt","a+")

	logd.write("\n##############################################################################################################\n")
	loge.write("\n##############################################################################################################\n")
	
	logd.write(begintime+ "\nBegin Logging:\n")
	loge.write(begintime+ "\nBegin Logging:\n")
	
	for i in symlist:
		for d in datelist:
			url = urlsyntax(datatype,i,d)
			filename = datatype+'.'+i
			filename = filename.replace('*','9')
			filename = filename.replace('#','9')
			
			
			if len(d)==8:
				filename = filename+'.'+d
			filename = filename+".JSON"
			
			print("Fetching " + i + " via " + url + " try saving to "+fileloc+filename)
			
			if (not overwrite):
				
				try:
					testfile = open(fileloc+filename, "r")
					test_json = json.loads(testfile.read())
					testfile.close()
					if (test_json):
						print(fileloc+filename+" Already exist skipping..")
						continue
				except FileNotFoundError:
					print(fileloc+filename+" File not found downloading..")
				except ValueError:
					print(fileloc+filename+" Bad JSON found downloading..")
					
			if(download_file(url, fileloc+filename)):
				print("Fetch "+url+" sucessfully saved to "+fileloc+filename)				
				logd.write("Fetch "+url+" sucessfully saved to "+fileloc+filename+"\n")
			else:
				print("Fetch "+url+" failed to save to "+fileloc+filename)
				loge.write("Fetch "+url+" failed to save to "+fileloc+filename+"\n")
				
	t2 = time.gmtime()
	tt2 = time.time()
	
	endtime = time.strftime('%a, %d %b %Y %H:%M:%S GMT',t2)	 
	
	elapsedtime = str(tt2-tt1)
	
	logd.write(endtime+ "\nEnd Logging Time Elapsed: \n"+elapsedtime)
	loge.write(endtime+ "\nEnd Logging Time Elapsed: \n"+elapsedtime)
	
	
	logd.close()
	loge.close()
	
	print("End IEX "+datatype+" DB Dump at "+endtime+ " Took :"+elapsedtime+" seconds. \n")
	
	return 1;



def urlsyntax (datatype, symbol, date="n/a"):
	syntax = {
			'Company':"https://api.iextrading.com/1.0/stock/"+symbol+"/company",
			
			'Chart':"https://api.iextrading.com/1.0/stock/"+symbol+"/chart",
			'Chart5y':"https://api.iextrading.com/1.0/stock/"+symbol+"/chart/5y",
			'Chart2y':"https://api.iextrading.com/1.0/stock/"+symbol+"/chart/2y",
			'Chart1y':"https://api.iextrading.com/1.0/stock/"+symbol+"/chart/1y",
			'Chartytd':"https://api.iextrading.com/1.0/stock/"+symbol+"/chart/ytd",
			'Chart6m':"https://api.iextrading.com/1.0/stock/"+symbol+"/chart/6m",
			'Chart3m':"https://api.iextrading.com/1.0/stock/"+symbol+"/chart/3m",
			'Chart1m':"https://api.iextrading.com/1.0/stock/"+symbol+"/chart/1m",
			'Chart1d':"https://api.iextrading.com/1.0/stock/"+symbol+"/chart1d",
			'Chartdate':"https://api.iextrading.com/1.0/stock/"+symbol+"/chart/date/"+date,
			'Chartdynamic':"https://api.iextrading.com/1.0/stock/"+symbol+"/chart/dynamic",
			
			'Financials':"https://api.iextrading.com/1.0/stock/"+symbol+"/financials",
			'FinancialsAnnual':"https://api.iextrading.com/1.0/stock/"+symbol+"/financials?period=annual",
			}
	return syntax[datatype] if datatype in syntax else 0


###############################################################################

print("Begin \n")



datelist = getdatadatelist()
firstdate = findstartdate(datelist)
sorteddatelist = datelist
sorteddatelist.sort(reverse=True)
firstdateindex = sorteddatelist.index(firstdate)

dailydates = sorteddatelist[0:firstdateindex+1]

symlist = getsymlist()
testdf = url2df()
print(testdf)

'''
#symlist=['MSFT','AAPL']
dumptofile (symlist,"Company")
dumptofile (symlist,"Chart5y")
dumptofile (symlist,"Chartdate",datelist=dailydates)

'''

def qw(s):
	return list(s.split())


sp1500list = qw("DDD MMM EGHT AIR ABM ACIW ADTN ACM AES AFL AGCO AKS AMAG AMCX AME AMN ANIP ANSS ARR ARRS ASGN T ATNI AZZ AAON AAN ABBV ABT ANF ABMD ACHC AKR ACN ACET ACOR ATVI ATU AYI ACXM ADNT ADBE ATGE ASIX AAP AEIS AMD AEGN AJRD AVAV AET AMG A AGYS ADC APD AKAM AKRX ALG ALRM ALK AIN ALB ALEX ARE ALXN ALGN Y ATI ALGT ALLE AGN ALE ADS LNT MDRX ALL GOOGL GOOG MO AMZN AMBC AMED AEE AAL AAT AXL ACC AEO AEP AEL AXP AFG AIG APEI AWR AMT AVD AWK AMWD AMP ABCB AMSF ABC AMGN AMPH APH APC ADI ANDV ANDE ANGO ANIK AXE ANTM AON APA AIV APY APOG ARI AAPL AIT AMAT AAOI ATR APTV WTR ARCB ADM AROC ARNC ANET AHH ARW ABG ASNA ASH AHL ASRT ASB AIZ ASTE AAWW ATO AN AZO ADSK ADP AVB AVNS AVY CAR AVA AVT AVP ACLS AAXN BOFI BGS OZK BBT BJRI BMI BHGE BCPC BLL BANC BXS BAC BOH BANR BNED BKS B BAX BDX BBBY BELFB BDC BEL BMS BHE BRK.B BHLB BBY BGFV BIG BIO TECH BEAT BIIB BKH BLK BLKB HRB BCOR BA BCC BCEI BKNG BWA SAM BPFH BXP BSX EPAY BYD BRC BGG BHF EAT BMY BRS AVGO BR BRKL BRKS BRO BF.B BC BKE CJ CA CACI CBL CBRE CBS CDK CF CHRW CIEN CME CMS CNO CNX CEIX CROX CSGS CSX CTS CVBF CVS CABO CBT CCMP COG CDNS CALM CAMP CVGW CAL CWT ELY CPE CBM CPT CPB CMD COF CMO CRR CAH CATM CTRE CECO CSL KMX CCL CRS CRZO CARS CRI CASY CTLT CAT CATY CATO CVCO CBOE CDR CELG CNC CNP CENT CENTA CPF CENX CTL CERN CEVA CRL GTLS CHTR CLDT CAKE CHE CHFC CHK CHSP CVX CHS PLCE CMG CB CHD CHDN CHUY CI XEC CBB CINF CNK CTAS CIR CRUS CSCO C CFG CTXS CHCO CLH CLW CLX CLD COKE KO CCOI CGNX CTSH COHR COHU CL COLB CMCSA CMA FIX CBSH CMC CBU CYH CHCT CVLT CMP CPSI CMTL CAG CXO CNMD COP CNSL ED STZ CTRL CVG COO CTB CPS CPRT CORT CLB CORE CXW CLGX COR GLW OFC CRVL COST COTY CUZ CBRL CR CRAY CREE CCRN CCI CRY CUB CFR CMI CW CUBI CUTR CY CONE CYTK DISH DSPG DSW DTE DXC DXPE DVA DAKT DAN DHR DRI DAR PLAY DF DECK DE DLPH DAL DLX DNR XRAY DVN DO DRH DKS DBD DGII DLR DDS DCOM DIN DIOD DPLO DFS DISCA DISCK DG DLTR D DPZ UFS DCI DFIN RRD DORM DEI DOV DWDP DRQ DUK DRE DNB DNKN DY ETFC EOG EPR EQT ESE EVTC SSP EZPW EXP EGRX EWBC EGP DEA EMN ETN EV EBIX ECHO ECL EPC EIX EDR EW EE LOCO ERI ESIO EA EFII EME EBS EMR EIG NPO ENTA EHC ECPG WIRE ENDP EGN ENR ENS EGL ENVA ESV ETR EVHC PLUS EFX EQIX EQR ERA ESND ESS EL ESL ETH EVR RE EVRG ES EXEL EXC EXLS EXPE EXPD EXPO EXPR ESRX EXTN EXR EXTR XOM FFIV FARO FLIR FMC FNB FTD FCN FN FB FDS FICO FAST FDX FRT FSS FII FIS LION FRGI FITB FNSR FAF FBP FCF FFBC FFIN FHN FR FMBI FSLR FCFS FE FISV FIVE FLT FTK FLO FLS FLR FL F FORM FORR FTNT FTV FBHS FWRD FOSL FCPT FOXF FRAN FELE FSB BEN FSP FCX FTR FUL FULT FF GIII GATX AJG GME GCI GPS GRMN IT GD GE GIS GM GCO GWR GNTX THRM GPC GNW GEO GEOS GTY ROCK GILD GBCI GLT GNL GPN GMED GS GT GOV GGG GHC GWW GVA GPMT GWB GNBC GDOT GPRE GBX GHL GEF GFF GPI GES GIFI GPOR HCA HCI HCP HF HMSY HNI HPQ HAE HAIN HAL HWC HBI HAFC THG HOG HLIT HRS HSC HIG HAS HVT HE HA HWKN HAYN HQY HSTM HR HCSG HTLD HSII HELE HLX HP JKHY HFWA HT HSY HSKA HES HPE HIBB HPR HIW HRC HI HLT HFC HOLX HOMB HD HMST HON HOPE HMN HRL DHI HPT HST HUBG HUBB HUM JBHT HBAN HII ICUI IDA IEX IDXX INFO IIVI INTL IPGP IQV IRDM ITT ICHR ITW ILMN INCY IRT INDB IR NGVT INGR IPHS IOSP INVA INGN NSIT NSP IBP IIIN ITGR IART IDTI INTC IPAR IDCC IBKR ICE TILE IPG IBOC IBM IFF IP ISCA INTU ISRG IVC IVZ IVR ITG IRM ITRI JJSF JCOM JBGS JPM JBL JACK JEC JRVR JHG JEF JBLU JBT JW.A JNJ JCI JLL JNPR KBH KBR KLAC KLXI KALU KAMN KSU KS K KELYA KEM KMPR KMT KEY KEYS KRC KMB KIM KMI KEX KIRK KRG KNX KN KSS KOPN KOP KFY KRA KR KLIC LB LLL LCII LGIH LHCG LKQ LXU LKSD LTC LZB LHO LH LRCX LAMR LW LANC LSTR LCI LNTH LMAT LTXB LM LEG LDOS TREE LEN LII LXP LPT LSI LPNT LGND LLY LECO LNC LNN LQDT LAD LFUS LIVN LYV LPSN LMT L LOGM LPX LOW LL LITE LMNX LDL LYB MTB MHO MHLD MMS MBFI MDC MDU MGM MKSI MGPI MSA MSM MSCI MTSC MYRG MAC CLI M MGLN MNK MANH MAN MANT MRO MPC MCS HZO MKTX MAR VAC MMC MRTN MLM MAS MASI MA MTDR MTRN MTRX MATX MAT MATW MXL MKC MDR MCD MCK MPW MDSO MED MD MDT MRK MCY MRCY MDP VIVO MMSI MTH CASH MEI MET MTD MDXG KORS MSTR MCHP MU MSFT MAA MLHR MTX MINI MHK MOH TAP MNTA MCRI MDLZ MPWR TYPE MNRO MNST MCO MOG.A MS MOS MPAA MSI MOV MLI LABL MUR MUSA MYE MYL MYGN NBTB NCR EGOV NKE NMIH NFBK DNOW NRG NUS NVR NBR NANO NDAQ NBHC NFG NATI NOV NPK NNN NSA BABY NLS NAVI NCI NAVG NP NKTR NEOG NTAP NFLX NTGR NTCT NJR NEWM NYCB NYMT NYT NEU NWL NFX NEM NR NWSA NWS NEE NXGN NLSN NI NE NBL NDSN JWN NSC NTRS NOC NWBI NWN NWE NCLH NUVA NUE NTRI NVDA ORLY OFG OGE OGS OKE OPB OSIS OAS OXY OII OCLR ODP OIS ODFL ONB ORI OLN OLLI ZEUS OHI OMCL OMC OSPN OSUR ORCL ORN ORIT OFIX OSK OMI OI OXM PCAR PBF PDCE PDFS PCG PGTI PNC PNM PPG PPL PRAA PSB PTC PVH PACW PPBI PKG PZZA PARR PKE PH PATK PDCO PTEN PYPL PAYX PENN PVAC JCP PEI PMT PNR PBCT PEP PRFT PKI PRGO PERY PRSP PETS PFE PAHC PM PSX PLAB PNFP PNW PES PXD PJC PBI PLT PLXS PII POL POOL POST PCH POWL POWI PRAH PX PFBC PBH PRI PFG PRA PLD PUMP PG PGNX PRGS PGR PB PRLB PRSC PFS PRU PEG PSA PHM QEP QCOM QRVO KWR QLYS NX PWR DGX QNST QHC RMAX RGNX REX RH RLI RPM RL RMBS RPT RRC RAVN RJF RYAM RYN RTN O RHT RRGB RWT RBC REG REGN RF RGS RGA RS RNR REGI RCII RGEN RSG RMD RECN ROIC REI RHI ROK COL ROG ROL ROP ROST RDC RCL RGLD RTEC RUTH R STBA SPGI SBAC SCG CKH SEIC SLG SLM SM SPSC SPXC FLOW SRCI STE SIVB SBRA SABR SAFT SAIA CRM SBH SAFM JBSS SANM BFS SCSC HSIC SLB SCHL SCHW SWM SAIC SGMS SMG SBCF STX SEE SEM SIGI SRE SMTC SENEA SNH SXT SCI SFBS SHAK SHW SCVL SFLY SSTK SBNY SIG SLGN SLAB SFNC SPG SSD SIX SKX SKYW SWKS SNBR AOS SJM SNA SEDG SAH SONC SON BID SJI SO SBSI LUV SWX SWN SPTN SPPI SR SPOK SFM STMP SMP SXI SWK SBUX STT STLD SCL SRCL STL SHOO STC SF STRA SYK RGR INN SXC STI SPN SUP SUPN SVU SRDX SYKE SYMC SYNA SYF SYNH SNX SNPS SNV SYY TROW TCF TEL TGNA ENSG TJX TPH TTEC TTMI TRHC TCMD TLRD TTWO SKT TPR TGT TCO TISI TECD FTI TDY TFX TDS TPX THC TNC TDC TER TEX TTEK TTI TCBI TXN TXRH TXT BK BCO CC KHC MDCO MIK TTS WEN WMB TMO TPRE THO TIVO TIF TKR TMST TWI TVTY TOL TMP TR BLD TMK TTC TSS TSCO TDG RIG TRV TVPT TG THS TREX TRMB TRN TRIP TBK TGI TBI TRST TRMK TUP FOXA FOX TWTR TYL TSN UDR UGI UMBF USB USCR ECOL USPH SLCA ULTA ULTI UCTT UMPQ UAA UA UFI UNF UNP UIS UNT UBSI UCBI UAL UFCS UIHC UNFI UPS URI X UTX UTHR UNH UNIT UVV UEIC UFPI UHT UHS UVE UNM UE URBN UBA VFC VRTU VLO VLY VMI VVV VREX VAR VVC VECO VTR VRA VRSN VRSK VRTV VZ VSM VRTX VSAT VIAB VVI VIAV VICR VRTS V VSH VSTO VC VSI VG VNO VMC WDFC WEC WEX WPX WRB WNC WAB WDR WAGE WBA WD WMT DIS WAFD WPG WM WAT WSO WTS WBS WRI WCG WFC WELL WERN WST WRK WABC WDC WU WY WHR WSR WLH WSM WLTW WING WGO WTFC WETF WWW WWD WRLD INT WWE WOR WYND WH WYNN XL XOXO XEL XRX XLNX XPER XYL YUM ZBRA ZBH ZION ZTS ZUMZ EBAY EHTH IRBT STAR NVT")

sp500list = qw("MMM AES AFL AME ANSS T ABBV ABT ABMD ACN ATVI ADBE AAP AMD AET AMG A APD AKAM ALK ALB ARE ALXN ALGN ALLE AGN ADS LNT ALL GOOGL GOOG MO AMZN AEE AAL AEP AXP AIG AMT AWK AMP ABC AMGN APH APC ADI ANDV ANTM AON APA AIV AAPL AMAT APTV ADM ARNC ANET AIZ AZO ADSK ADP AVB AVY BBT BHGE BLL BAC BAX BDX BRK.B BBY BIIB BLK HRB BA BKNG BWA BXP BSX BHF BMY AVGO BR BF.B CA CBRE CBS CF CHRW CME CMS CSX CVS COG CDNS CPB COF CAH KMX CCL CAT CBOE CELG CNC CNP CTL CERN CHTR CVX CMG CB CHD CI XEC CINF CTAS CSCO C CFG CTXS CLX KO CTSH CL CMCSA CMA CAG CXO COP ED STZ COO CPRT GLW COST COTY CCI CMI DISH DTE DXC DVA DHR DRI DE DAL XRAY DVN DLR DFS DISCA DISCK DG DLTR D DOV DWDP DUK DRE ETFC EOG EQT EMN ETN ECL EIX EW EA EMR ETR EVHC EFX EQIX EQR ESS EL RE EVRG ES EXC EXPE EXPD ESRX EXR XOM FFIV FLIR FMC FB FAST FDX FRT FIS FITB FE FISV FLT FLS FLR FL F FTV FBHS BEN FCX AJG GPS GRMN IT GD GE GIS GM GPC GILD GPN GS GT GWW HCA HCP HPQ HAL HBI HOG HRS HIG HAS HP HSY HES HPE HLT HFC HOLX HD HON HRL DHI HST HUM JBHT HBAN HII IDXX INFO IPGP IQV ITW ILMN INCY IR INTC ICE IPG IBM IFF IP INTU ISRG IVZ IRM JPM JEC JEF JNJ JCI JNPR KLAC KSU K KEY KMB KIM KMI KSS KR LB LLL LKQ LH LRCX LEG LEN LLY LNC LMT L LOW LYB MTB MGM MSCI MAC M MRO MPC MAR MMC MLM MAS MA MAT MKC MCD MCK MDT MRK MET MTD KORS MCHP MU MSFT MAA MHK TAP MDLZ MNST MCO MS MOS MSI MYL NKE NRG NDAQ NOV NKTR NTAP NFLX NWL NFX NEM NWSA NWS NEE NLSN NI NBL JWN NSC NTRS NOC NCLH NUE NVDA ORLY OKE OXY OMC ORCL PCAR PCG PNC PPG PPL PVH PKG PH PYPL PAYX PNR PBCT PEP PKI PRGO PFE PM PSX PNW PXD PX PFG PLD PG PGR PRU PEG PSA PHM QCOM QRVO PWR DGX RL RJF RTN O RHT REG REGN RF RSG RMD RHI ROK COL ROP ROST RCL SPGI SBAC SCG SLG SIVB CRM HSIC SLB SCHW STX SEE SRE SHW SPG SWKS AOS SJM SNA SO LUV SWK SBUX STT SRCL SYK STI SYMC SYF SNPS SYY TROW TEL TJX TTWO TPR TGT FTI TXN TXT BK KHC WMB TMO TIF TMK TSS TSCO TDG TRV TRIP FOXA FOX TWTR TSN UDR USB ULTA UAA UA UNP UAL UPS URI UTX UNH UHS UNM VFC VLO VAR VTR VRSN VRSK VZ VRTX VIAB V VNO VMC WEC WBA WMT DIS WM WAT WFC WELL WRK WDC WU WY WHR WLTW WYNN XL XEL XRX XLNX XYL YUM ZBH ZION ZTS EBAY")

sp400list = qw("ACIW ACM AGCO AMCX ARRS AAN ACHC AYI ACXM ADNT ATGE AKRX ALEX Y ATI ALE MDRX ACC AEO AFG APY ATR WTR ARW ASH AHL ASB ATO AN AVNS CAR AVT OZK BXS BOH BBBY BDC BMS BIG BIO TECH BKH BLKB SAM BYD EAT BRO BC CDK CIEN CNO CNX CABO CBT CPE CPT CMD CSL CRS CARS CRI CASY CTLT CATY CRL CAKE CHE CHFC CHK CHDN CNK CRUS CLH CGNX COHR CBSH CMC CVLT CMP CVG CLB CXW CLGX COR OFC CUZ CBRL CR CREE CFR CW CY CONE DAN DECK DLPH DLX DO DKS DDS DPZ UFS DCI DEI DRQ DNB DNKN DY EPR EXP EWBC EV EPC EDR ERI EME EHC EGN ENR ENS ESV ESL EVR EXEL FNB FDS FICO FII FAF FHN FR FSLR FIVE FLO FTNT FULT GATX GWR GNTX GNW GEO GMED GGG GHC GVA GEF GPOR HNI HAE HAIN HWC THG HE HR HCSG HELE JKHY HIW HRC HOMB HPT HUBB ICUI IDA IEX ITT INGR IART IDTI IDCC IBKR IBOC ISCA JCOM JBGS JBL JACK JHG JBLU JW.A JLL KBH KBR KLXI KMPR KMT KEYS KRC KEX KNX LHO LAMR LW LANC LSTR LM LDOS TREE LII LPT LSI LPNT LECO LFUS LIVN LYV LOGM LPX LITE MMS MBFI MDU MKSI MSA MSM CLI MNK MANH MAN MKTX VAC MASI MTDR MDR MPW MDSO MD MCY MDP MLHR MTX MOH MPWR MUR MUSA NCR DNOW NUS NVR NBR NFG NATI NNN NAVI NTCT NJR NYCB NYT NEU NDSN NWE NUVA OGE OGS OAS OII ODFL ORI OLN OLLI OHI OSK OI PBF PNM PTC PACW PZZA PDCO PTEN PRSP PNFP PBI PLT PII POL POOL POST PCH PRAH PBH PRI PB QEP RPM RRC RYN RBC RGA RS RNR ROL RDC RGLD R SEIC SLM SM STE SBRA SABR SBH SAFM SAIC SGMS SMG SNH SXT SCI SBNY SIG SLGN SLAB SIX SKX SON BID SWX SWN SFM STLD STL SF SPN SYNA SYNH SNX SNV TCF TGNA TPH SKT TCO TECD TDY TFX TDS TPX THC TDC TER TEX TCBI TXRH BCO CC MIK WEN THO TKR TOL TR TTC RIG THS TRMB TRN TRMK TUP TYL UGI UMBF ULTI UMPQ UBSI UNFI X UTHR UNIT UE URBN VLY VMI VVV VVC VSM VSAT VSH VC WEX WPX WRB WAB WAFD WSO WBS WRI WCG WERN WST WSM WTFC WWD INT WWE WOR WYND WH ZBRA NVT")

sp600list = qw("DDD EGHT AIR ABM ADTN AKS AMAG AMN ANIP ARR ASGN ATNI AZZ AAON ANF AKR ACET ACOR ATU ASIX AEIS AEGN AJRD AVAV AGYS ADC ALG ALRM AIN ALGT AMBC AMED AAT AXL AEL APEI AWR AVD AMWD ABCB AMSF AMPH ANDE ANGO ANIK AXE APOG ARI AIT AAOI ARCB AROC AHH ABG ASNA ASRT ASTE AAWW AVA AVP ACLS AAXN BOFI BGS BJRI BMI BCPC BANC BANR BNED BKS B BELFB BEL BHE BHLB BGFV BEAT BCOR BCC BCEI BPFH EPAY BRC BGG BRS BRKL BRKS BKE CJ CACI CBL CEIX CROX CSGS CTS CVBF CCMP CALM CAMP CVGW CAL CWT ELY CBM CMO CRR CATM CTRE CECO CRZO CATO CVCO CDR CENT CENTA CPF CENX CEVA GTLS CLDT CHSP CHS PLCE CHUY CBB CIR CHCO CLW CLD COKE CCOI COHU COLB FIX CBU CYH CHCT CPSI CMTL CNMD CNSL CTRL CTB CPS CORT CORE CRVL CRAY CCRN CRY CUB CUBI CUTR CYTK DSPG DSW DXPE DAKT DAR PLAY DF DNR DRH DBD DGII DCOM DIN DIOD DPLO DFIN RRD DORM ESE EVTC SSP EZPW EGRX EGP DEA EBIX ECHO EE LOCO ESIO EFII EBS EIG NPO ENTA ECPG WIRE ENDP EGL ENVA PLUS ERA ESND ETH EXLS EXPO EXPR EXTN EXTR FARO FTD FCN FN FSS LION FRGI FNSR FBP FCF FFBC FFIN FMBI FCFS FTK FORM FORR FWRD FOSL FCPT FOXF FRAN FELE FSB FSP FTR FUL FF GIII GME GCI GCO THRM GEOS GTY ROCK GBCI GLT GNL GOV GPMT GWB GNBC GDOT GPRE GBX GHL GFF GPI GES GIFI HCI HF HMSY HAFC HLIT HSC HVT HA HWKN HAYN HQY HSTM HTLD HSII HLX HFWA HT HSKA HIBB HPR HI HMST HOPE HMN HUBG IIVI INTL IRDM ICHR IRT INDB NGVT IPHS IOSP INVA INGN NSIT NSP IBP IIIN ITGR IPAR TILE IVC IVR ITG ITRI JJSF JRVR JBT KALU KAMN KS KELYA KEM KIRK KRG KN KOPN KOP KFY KRA KLIC LCII LGIH LHCG LXU LKSD LTC LZB LCI LNTH LMAT LTXB LXP LGND LNN LQDT LAD LPSN LL LMNX LDL MHO MHLD MDC MGPI MTSC MYRG MGLN MANT MCS HZO MRTN MTRN MTRX MATX MATW MXL MED MRCY VIVO MMSI MTH CASH MEI MDXG MSTR MINI MNTA MCRI TYPE MNRO MOG.A MPAA MOV MLI LABL MYE MYGN NBTB EGOV NMIH NFBK NANO NBHC NPK NSA BABY NLS NCI NAVG NP NEOG NTGR NEWM NYMT NR NXGN NE NWBI NWN NTRI OFG OPB OSIS OCLR ODP OIS ONB ZEUS OMCL OSPN OSUR ORN ORIT OFIX OMI OXM PDCE PDFS PGTI PRAA PSB PPBI PARR PKE PATK PENN PVAC JCP PEI PMT PRFT PERY PETS PAHC PLAB PES PJC PLXS POWL POWI PFBC PRA PUMP PGNX PRGS PRLB PRSC PFS KWR QLYS NX QNST QHC RMAX RGNX REX RH RLI RMBS RPT RAVN RYAM RRGB RWT RGS REGI RCII RGEN RECN ROIC REI ROG RTEC RUTH STBA CKH SPSC SPXC FLOW SRCI SAFT SAIA JBSS SANM BFS SCSC SCHL SWM SBCF SEM SIGI SMTC SENEA SFBS SHAK SCVL SFLY SSTK SFNC SSD SKYW SNBR SEDG SAH SONC SJI SBSI SPTN SPPI SR SPOK STMP SMP SXI SCL SHOO STC STRA RGR INN SXC SUP SUPN SVU SRDX SYKE ENSG TTEC TTMI TRHC TCMD TLRD TISI TNC TTEK TTI MDCO TTS TPRE TIVO TMST TWI TVTY TMP BLD TVPT TG TREX TBK TGI TBI TRST USCR ECOL USPH SLCA UCTT UFI UNF UIS UNT UCBI UFCS UIHC UVV UEIC UFPI UHT UVE UBA VRTU VREX VECO VRA VRTV VVI VIAV VICR VRTS VSTO VSI VG WDFC WNC WDR WAGE WD WPG WTS WABC WSR WLH WING WGO WETF WWW WRLD XOXO XPER ZUMZ EHTH IRBT STAR")

''' reconcile lists '''

downloadlist = symlist
downloadlist = list(set(downloadlist).intersection(sp1500list))


			
###############################################################################


#symlist=['MSFT','AAPL']
#dumptofile (downloadlist,"Company")
#dumptofile (downloadlist,"Chart5y")
dumptofile (downloadlist,"Chartdate",datelist=dailydates)
dumptofile (symlist,"Financials")
dumptofile (symlist,"FinancialsAnnual")
