import pandas as pd
import re
import sys
import xlwt
import math
import numpy as np
from numpy import array
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import CountVectorizer
import pickle
import mysql.connector
from mysql.connector import errorcode
np.set_printoptions(threshold=sys.maxint)

try:
	cnx = mysql.connector.connect(user='root', password='',
                              host='127.0.0.1',
                              database='ta-quran')
	cursor_select	= cnx.cursor(buffered=True);
	cursor_insert   = cnx.cursor(buffered=True);

except mysql.connector.Error as err:
  if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
    print("Something is wrong with your user name or password")
  elif err.errno == errorcode.ER_BAD_DB_ERROR:
    print("Database does not exist")
  else:
    print(err)

#fungsi preprocessing
def preProcessing(terjemahan):
	letters_only	= re.sub("[^a-zA-Z]"," ",terjemahan)
	words 			= letters_only.lower().split()
	stops 			= set(stopwords.words("english"))
	real_words 		= [w for w in words if not w in stops]
	return(" ".join(real_words))
#end of fungsi preprocessing

#fungsi getFeatures
def getFeatures(data):
	vectorizer 		= CountVectorizer(analyzer		= "word",
									  tokenizer 	= None,
									  preprocessor 	= None,
									  stop_words	= None,
									  max_features	= 15000
										)

	dataFeatures 	= vectorizer.fit_transform(data)
	dataFeatures	= dataFeatures.toarray()
	vocab 			= vectorizer.get_feature_names()
	dist 			= np.sum(dataFeatures, axis=0)

	word 			= []
	countWord  		= []

	for tag, count in zip(vocab,dist):
		word.append(tag)
		countWord.append(count)


	return word, countWord
#end of fungsi getFeatures

#fungsi makeDataSet
def makeDataSet(rangeawal, rangeakhir):
	query 	= ("SELECT id, teksayat FROM ta_ayat WHERE id > %s AND id <= %s")
	cursor_select.execute(query,(rangeawal,rangeakhir))

	id_data_training 	= []
	data_training		= []
	rows = cursor_select.fetchall()

	for row in rows:
		id_data_training.append(row[0])
		data_training.append(row[1])

	sz_dtTraining 	= len(data_training)
	clear_data 		= []
	for i in xrange(0,sz_dtTraining):
		clear_data.append(preProcessing(data_training[i]))

	return id_data_training,clear_data
#end of fungsi makeDataSet


def getClearDataTestById(idx):
	query 	= ("SELECT id, teksayat FROM ta_ayat WHERE id = %s")
	cursor_select.execute(query,(idx,))

	id_data_training 	= []
	data_training		= []
	rows = cursor_select.fetchall()

	for row in rows:
		id_data_training.append(row[0])
		data_training.append(row[1])

	sz_dtTraining 	= len(data_training)
	clear_data 		= []
	wordArr 		= []
	countArr 		= []
	for i in xrange(0,sz_dtTraining):
		clear_data.append(preProcessing(data_training[i]))
		word,countWord = getFeatures(clear_data)
		wordArr.append(word)
		countArr.append(countWord)
	# for i in xrange(0, len(clear_data)):

	return wordArr,countArr


#fungsi getAllKClassList
def getAllKClassList():
	query = ("SELECT DISTINCT level_1, level_2, level_3, level_4, level_5, level_6 FROM ta_kelas")
	cursor_select.execute(query)
	temp2 = []

	for level_1, level_2, level_3, level_4, level_5, level_6 in cursor_select:
		temp1 = []
		temp1.append(level_1)
		temp1.append(level_2)
		temp1.append(level_3)
		temp1.append(level_4)
		temp1.append(level_5)
		temp1.append(level_6)
		temp2.append(temp1)
	return temp2
#end of fungsi getAllKClassList

#fungsi getDataLikelihood
def getDataLikelihood(range_awal, range_akhir, level_1,level_2,level_3,level_4,level_5,level_6):
	query 	= ("SELECT teksayat FROM ta_ayat WHERE id IN (SELECT id_ayat FROM ta_kelas WHERE id_ayat > %s AND id_ayat <= %s AND level_1 = %s AND level_2 = %s AND level_3 = %s AND level_4 = %s AND level_5 = %s AND level_6 = %s)")
	cursor_select.execute(query,(range_awal, range_akhir, level_1,level_2,level_3,level_4,level_5,level_6))

	data_training	= []
	rows			= cursor_select.fetchall()
	countrows 		= cursor_select.rowcount
	for row in rows: 
		data_training.append(row[0])

	sz_dtTraining 	= len(data_training)
	clear_data 		= []

	for i in xrange(0,sz_dtTraining):
		clear_data.append(preProcessing(data_training[i]))
	
	return countrows , clear_data
#end of fungsi getDataLikelihood

#fungsi find
def find(l, elem):
    for row, i in enumerate(l):
        try:
            column = i.index(elem)
        except ValueError:
            continue
        return row
    return -1
#end of fungsi find

def newCountTrueLikelihoodProb(wordArray, countArray):
	allLikelihoodArr 		= []
	for i in xrange(0,len(wordArray)):
		for j in xrange(0,len(wordArray[i])):
			query	= ("SELECT log_likelihood FROM ta_truelikelihood WHERE word = %s ")
			cursor_select.execute(query,(wordArray[i][j],))
			rows					= cursor_select.fetchall()
			countrows 				= cursor_select.rowcount
			likelihoodArr 			= []
			if (countrows > 0):
				for row in rows:
					likelihoodArr.append(float(countArray[i][j] * row[0]))

				allLikelihoodArr.append(likelihoodArr)

	
	return allLikelihoodArr

def newCountFalseLikelihoodProb(wordArray, countArray):
	allLikelihoodArr 		= []
	for i in xrange(0,len(wordArray)):
		for j in xrange(0,len(wordArray[i])):
			query	= ("SELECT log_likelihood FROM ta_falselikelihood WHERE word = %s ")
			cursor_select.execute(query,(wordArray[i][j],))
			rows					= cursor_select.fetchall()
			countrows 				= cursor_select.rowcount
			likelihoodArr 			= []
			if (countrows > 0):
				for row in rows:
					likelihoodArr.append(float(countArray[i][j] * row[0]))

				allLikelihoodArr.append(likelihoodArr)

	
	return allLikelihoodArr

def getAllTruePriorProb():
	priorArr 	= []
	query 		= ("SELECT log_prior FROM ta_trueprior")
	cursor_select.execute(query)
	rows 		= cursor_select.fetchall()
	countrows   = cursor_select.rowcount

	if (countrows > 0):
		for row in rows:
			priorArr.append(float(row[0]))

	return priorArr

def getAllFalsePriorProb():
	priorArr 	= []
	query 		= ("SELECT log_prior FROM ta_falseprior")
	cursor_select.execute(query)
	rows 		= cursor_select.fetchall()
	countrows   = cursor_select.rowcount

	if (countrows > 0):
		for row in rows:
			priorArr.append(float(row[0]))

	return priorArr

def storeOutput(idList, outputList):
	add_data 	= ("INSERT INTO ta_output1 (id_ayat, level_1, level_2, level_3, level_4, level_5, level_6) VALUES(%(id_ayat)s,%(level_1)s,%(level_2)s,%(level_3)s,%(level_4)s,%(level_5)s,%(level_6)s)")
	for i in xrange(0,len(idList)):
			data 	= {
					'id_ayat'		: int(idList[i]),
					'level_1'		: int(outputList[i][0]),
					'level_2'		: int(outputList[i][1]),
					'level_3'		: int(outputList[i][2]),
					'level_4'		: int(outputList[i][3]),
					'level_5'		: int(outputList[i][4]),
					'level_6'		: int(outputList[i][5]),
				}
			cursor_insert.execute(add_data,data)	
	cnx.commit()
	return 1


#new_code
range_awaltest   = 0
range_akhirtest  = 1000

id_data,clearDataTest 	= makeDataSet(range_awaltest,range_akhirtest)


arrKelas  	= getAllKClassList()
idArr 					= []
labelArr  				= []
for jj in xrange(0,len(id_data)):
	id_observ				= id_data[jj]
	wordArray, countArray 	= getClearDataTestById(id_data[jj])
	trueLikelihoodArr 		= newCountTrueLikelihoodProb(wordArray,countArray)
	falseLikelihoodArr 		= newCountFalseLikelihoodProb(wordArray,countArray)

	truePriorArr 			= getAllTruePriorProb()
	falsePriorArr 			= getAllFalsePriorProb()

	trueLikelihoodArr.append(truePriorArr)
	falseLikelihoodArr.append(falsePriorArr)

	posteriorTrueArr  		= [sum(x) for x in zip(*trueLikelihoodArr)]
	posteriorFalseArr 		= [sum(x) for x in zip(*falseLikelihoodArr)]

	for i in xrange(0,len(posteriorTrueArr)):
		if (posteriorTrueArr[i] > posteriorFalseArr[i]):
			idArr.append(id_observ)
			labelArr.append(arrKelas[i])

	print "Iterasi ke - " , jj

storeData = storeOutput(idArr,labelArr)