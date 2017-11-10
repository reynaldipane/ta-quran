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

def getTargetList(id_ayat):
  query = ("SELECT level_1, level_2, level_3, level_4, level_5, level_6 FROM ta_kelas WHERE id_ayat = %s")
  cursor_select.execute(query,(id_ayat,))
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


def getOutputList(id_ayat):
  query = ("SELECT level_1, level_2, level_3, level_4, level_5, level_6 FROM ta_output1 WHERE id_ayat = %s")
  cursor_select.execute(query,(id_ayat,))
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


#MAIN
ctbenar = 0
ctsalah = 0
for i in xrange(0,1000):
  targetList  = getTargetList(i)
  outputList  = getOutputList(i)
  for j in xrange(0,len(outputList)):
    if(outputList[j] in targetList):
      ctbenar = ctbenar + 1
    else:
      ctsalah = ctsalah + 1

  for k in xrange(0,len(targetList)):
    if(targetList[k] in outputList):
      ctbenar = ctbenar
    else:
      ctsalah = ctsalah + 1

  print i


print ctbenar , ctsalah

hammingLoss   = float(float(ctsalah) / float(1010 * 1000)) * 100
print hammingLoss


#END OF MAIN
