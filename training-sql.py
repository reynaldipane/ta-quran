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

	wordArray 		= []
	countWordArray  = []

	for tag, count in zip(vocab,dist):
		wordArray.append(tag)
		countWordArray.append(count)

	return wordArray, countWordArray
#end of fungsi getFeatures

#fungsi makeDataSet
def makeDataSet(rangeawal, rangeakhir):
	query 	= ("SELECT id, teksayat FROM ta_ayat WHERE id > %s AND id <= %s")
	cursor_select.execute(query,(rangeawal,rangeakhir))

	id_data_training 	= []
	data_training		= []
	rows = cursor_select.fetchall()

	for row in rows:
		data_training.append(row[1])

	sz_dtTraining 	= len(data_training)
	clear_data 		= []

	for i in xrange(0,sz_dtTraining):
		clear_data.append(preProcessing(data_training[i]))
	
	return clear_data
#end of fungsi makeDataSet

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
	if (countrows > 0):
		for row in rows: 
			data_training.append(row[0])
			sz_dtTraining 	= len(data_training)
			clear_data 		= []

		for i in xrange(0,sz_dtTraining):
			clear_data.append(preProcessing(data_training[i]))
		return countrows , clear_data
	else:
		countrows = 0
		clear_data = 0
		return countrows, clear_data
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

#fungsi storeTrueLikelihood
def storeTrueLikelihood(wordList, countWordList, likelihoodList, log_likelihoodlist, level_1, level_2, level_3, level_4, level_5, level_6):
	add_data 	= ("INSERT INTO ta_truelikelihood (word, count_word, likelihood, log_likelihood, level_1,level_2,level_3,level_4,level_5,level_6) VALUES(%(word)s,%(count_word)s,%(likelihood)s,%(log_likelihood)s,%(level_1)s,%(level_2)s,%(level_3)s,%(level_4)s,%(level_5)s,%(level_6)s)")
	
	for i in xrange(0, len(wordList)):
		data  	= {
			'word' 			: wordList[i],
			'count_word'	: int(countWordList[i]),
			'likelihood' 	: likelihoodList[i],
			'log_likelihood': log_likelihoodlist[i],
			'level_1'		: level_1,
			'level_2'		: level_2,
			'level_3'		: level_3,
			'level_4'		: level_4,
			'level_5'		: level_5,
			'level_6'		: level_6,
		}		
		cursor_insert.execute(add_data,data)
	cnx.commit()
	
	return 1	
#end of fungsi storeTrueLikelihood

def storeTruePrior(prior,log_prior,level_1, level_2, level_3, level_4, level_5, level_6):
	add_data 	= ("INSERT INTO ta_trueprior (prior, log_prior, level_1,level_2,level_3,level_4,level_5,level_6) VALUES (%(prior)s,%(log_prior)s,%(level_1)s,%(level_2)s,%(level_3)s,%(level_4)s,%(level_5)s,%(level_6)s)")
	data  	= {
		'prior'			: prior,
		'log_prior'		: log_prior,
		'level_1'		: level_1,
		'level_2'		: level_2,
		'level_3'		: level_3,
		'level_4'		: level_4,
		'level_5'		: level_5,
		'level_6'		: level_6,
	}		
	cursor_insert.execute(add_data,data)
	cnx.commit()

def storeFalsePrior(falseprior, log_falseprior, level_1, level_2, level_3, level_4, level_5, level_6):
	add_data 	= ("INSERT INTO ta_falseprior (prior,log_prior,level_1,level_2,level_3,level_4,level_5,level_6) VALUES (%(falseprior)s,%(log_falseprior)s,%(level_1)s,%(level_2)s,%(level_3)s,%(level_4)s,%(level_5)s,%(level_6)s)")
	data  	= {
		'falseprior'	: falseprior,
		'log_falseprior': log_falseprior,
		'level_1'		: level_1,
		'level_2'		: level_2,
		'level_3'		: level_3,
		'level_4'		: level_4,
		'level_5'		: level_5,
		'level_6'		: level_6,
	}		
	cursor_insert.execute(add_data,data)
	cnx.commit()	

def storeFalseLikeLihood(wordList, falselikelihoodList, log_falseLikelihoodList, level_1, level_2, level_3, level_4, level_5, level_6):
	add_data 	= ("INSERT INTO ta_falselikelihood (word, likelihood, log_likelihood, level_1,level_2,level_3,level_4,level_5,level_6) VALUES(%(word)s,%(falselikelihood)s, %(log_falselikelihood)s,%(level_1)s,%(level_2)s,%(level_3)s,%(level_4)s,%(level_5)s,%(level_6)s)")
	for i in xrange(0, len(wordList)):
		data  	= {
			'word' 					: wordList[i],
			'falselikelihood' 		: falselikelihoodList[i],
			'log_falselikelihood' 	: log_falseLikelihoodList[i],
			'level_1'				: level_1,
			'level_2'				: level_2,
			'level_3'				: level_3,
			'level_4'				: level_4,
			'level_5'				: level_5,
			'level_6'				: level_6,
		}		
		cursor_insert.execute(add_data,data)
	cnx.commit()
	return 1	

def countWordFalseLikeLihood(totalfalseword,level_1, level_2, level_3, level_4, level_5, level_6):
	query 	= ("SELECT word, SUM(count_word) FROM ta_truelikelihood WHERE level_1 <> %s OR level_2 <> %s OR level_3 <> %s OR level_4 <> %s OR level_5 <> %s OR level_6 <> %s GROUP BY word")
	cursor_select.execute(query,(level_1,level_2,level_3,level_4,level_5,level_6))

	data_word 				= []
	data_falselikelihood	= []
	data_logfalselikelihood = []
	rows					= cursor_select.fetchall()
	countrows 				= cursor_select.rowcount

	for row in rows: 
		data_word.append(row[0])
		data_falselikelihood.append(float(row[1])/float(totalfalseword))
		data_logfalselikelihood.append(math.log(float(row[1])/float(totalfalseword)))
	
	return data_word, data_falselikelihood, data_logfalselikelihood

def sumWordFalseLikelihood(level_1, level_2, level_3, level_4, level_5, level_6):
	query 	= ("SELECT SUM(count_word) FROM ta_truelikelihood WHERE level_1 <> %s OR level_2 <> %s OR level_3 <> %s OR level_4 <> %s OR level_5 <> %s OR level_6 <> %s")
	cursor_select.execute(query,(level_1,level_2,level_3,level_4,level_5,level_6))

	rows					= cursor_select.fetchall()
	countrows 				= cursor_select.rowcount
	for row in rows: 
		total_count = row[0]
	
	return total_count


###############################################################################################################
# 	  #   ######    #     #	    #
## 	 ##	  #    #    #     # #   #
# ##  #   ######	#     #  #  #
#     #   #    #	#     #   # #
#     #   #    #	#	  #	    #
###############################################################################################################

#new_code
range_awal  = 1000
range_akhir = 6236

totalData 	= range_akhir - range_awal

clearDataTrain 			= makeDataSet(range_awal,range_akhir)
wordArray, countArray 	= getFeatures(clearDataTrain)


arrKelas  	= getAllKClassList()
sizeArrKelas = len(arrKelas)

# #looping untuk menghitung likelihood given Cn = T
for jj in xrange(0, sizeArrKelas):	
	print arrKelas[jj]
	level_1 = arrKelas[jj][0]
	level_2 = arrKelas[jj][1]
	level_3 = arrKelas[jj][2]
	level_4 = arrKelas[jj][3]
	level_5 = arrKelas[jj][4]
	level_6 = arrKelas[jj][5]

	countTotalData, clearDataTrainPerClass 	= getDataLikelihood(range_awal,range_akhir,level_1,level_2,level_3,level_4,level_5,level_6)

	if (countTotalData > 0):
		print arrKelas[jj] , " masuk IF"
		wordPerClassArray, countPerClassArray 	= getFeatures(clearDataTrainPerClass)


		storeWordArr = []
		countWordArr = []

		for i in xrange(0, len(wordArray)):
			check 	 = wordArray[i] in wordPerClassArray
			if (check == True):
				idx  = find(wordPerClassArray,wordArray[i])
				storeWordArr.append(wordArray[i])
				countWordArr.append(countPerClassArray[idx]+1)
			else:
				storeWordArr.append(wordArray[i])
				countWordArr.append(1)

		log_conditionalProbArr = []
		conditionalProbArr = []
		for i in xrange(0,len(storeWordArr)):
			conditionalProbArr.append(float(countWordArr[i]) / float(sum(countWordArr)))
			log_conditionalProbArr.append(math.log(float(countWordArr[i]) / float(sum(countWordArr))))
		
		prior 						= float(countTotalData+1) / float(totalData+2)
		log_prior					= math.log(float(countTotalData+1) / float(totalData+2))

		falseprior 					= 1 - prior
		log_falseprior 				= math.log(1 - prior) 

		commitTrueLikelihoodData 	= storeTrueLikelihood(storeWordArr, countWordArr, conditionalProbArr, log_conditionalProbArr, level_1, level_2, level_3, level_4, level_5, level_6)
		commitTruePriorData 		= storeTruePrior(prior,log_prior,level_1, level_2, level_3, level_4, level_5, level_6)
		commitFalsePriorData 		= storeFalsePrior(falseprior,log_falseprior,level_1, level_2, level_3, level_4, level_5, level_6)
	else:
		print arrKelas[jj], " tidak masuk IF"
		storeWordArr = []
		countWordArr = []
		for i in xrange(0,len(wordArray)):
			storeWordArr.append(wordArray[i])
			countWordArr.append(1)

		log_conditionalProbArr = []
		conditionalProbArr = []

		for i in xrange(0,len(storeWordArr)):
			conditionalProbArr.append(float(countWordArr[i]) / float(sum(countWordArr)))
			log_conditionalProbArr.append(math.log(float(countWordArr[i]) / float(sum(countWordArr))))

		prior 						= float(countTotalData+1) / float(totalData+2)
		log_prior					= math.log(float(countTotalData+1) / float(totalData+2))

		falseprior 					= 1 - prior
		log_falseprior 				= math.log(1 - prior)	

		commitTrueLikelihoodData 	= storeTrueLikelihood(storeWordArr, countWordArr, conditionalProbArr, log_conditionalProbArr, level_1, level_2, level_3, level_4, level_5, level_6)
		commitTruePriorData 		= storeTruePrior(prior,log_prior,level_1, level_2, level_3, level_4, level_5, level_6)
		commitFalsePriorData 		= storeFalsePrior(falseprior,log_falseprior,level_1, level_2, level_3, level_4, level_5, level_6)

	print jj
# #end of looping untuk menghitung likelihood given Cn = T

for jj in xrange(0,sizeArrKelas):
	level_1 = arrKelas[jj][0]
	level_2 = arrKelas[jj][1]
	level_3 = arrKelas[jj][2]
	level_4 = arrKelas[jj][3]
	level_5 = arrKelas[jj][4]
	level_6 = arrKelas[jj][5]

	total = sumWordFalseLikelihood(level_1,level_2,level_3,level_4,level_5,level_6)
	wordFalseArr, falseLikelihoodArr, log_falseLikelihoodArr = countWordFalseLikeLihood(total,level_1,level_2,level_3,level_4,level_5,level_6)

	commitFalseLikelihood 	= storeFalseLikeLihood(wordFalseArr,falseLikelihoodArr,log_falseLikelihoodArr,level_1,level_2,level_3,level_4,level_5,level_6)
	print jj