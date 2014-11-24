'''
Project: T GIS 501 a: Lab 7
Purpose: Create shapefile from Twitter REST API results
Author:  Kris Symer
Date:    2014-11-24
Notes:
'''

#============================================
# Part I: Get Tweets and save in text file
#============================================

from TwitterSearch import *
from geopy import geocoders
import io
# create geocoding function
def geo(location):
    g = geocoders.GoogleV3() # use Google V3 service
    loc = g.geocode(location)
    return loc.latitude, loc.longitude

try:

    # create a TwitterSearchOrder object
    tso = TwitterSearchOrder()
    keywords = ['bike', 'helmet'] # multiple items are treated as boolean AND
    print 'Search: ' + str(keywords)
    tso.set_keywords(keywords) # define search terms
    tso.set_include_entities(False) # do not return all entity information

    # search object creation with secret token
    ts = TwitterSearch(
        consumer_key = 'y9aNbDMxbsdIPXwtOSS4zihTo',
        consumer_secret = 'UczdMpZvWo2rYVNEsDEJtkcRazmCEVgydd4M2AK7jV8mXPDOQt',
        access_token = '25399537-DoK4qEBY0t5N1jJNVGQQPqCvRv2l8CAMvE8EqCssD',
        access_token_secret = 'Vb2Y1znuVcI6koQgMLDmYGis2MEwDHZLOJPcOkBrxo8tD'
     )

    # create a new text file to store data
    filename = 'tweetdata.txt'

    with io.open(filename, 'w', encoding='utf8') as f:
        # loop through search object
        i = 1
        for tweet in ts.search_tweets_iterable(tso):
            if tweet['place'] is not None: #return only tweets having a location
                # set lat,long variables from geocoded location
                (lat, lng) = geo(tweet['place']['full_name'])
                # print records as tab-delimited text file (lat long, user, text) ; strip new lines from text
                f.write(str(lat) + '\t' + str(lng) +'\t' + tweet['user']['screen_name'] + '\t')
                f.write(tweet['text'].replace('\n', ' ') + '\n')
                i = i + 1
        print str(i - 1) + ' rows written'

except TwitterSearchException as e:
    print(e)



# comment out code above after creating text file so we do not exceed api limit while testing

#============================================
# Part II: Create point shapefile from text file
#============================================

import arcpy
from arcpy import env
import csv

#set local variables
myfolder = 'X:/msgt/tgis501/lab_7/'
env.workspace = myfolder
env.overwriteOutput = True
outpath = myfolder
textfile = filename
newfc = 'tweets.shp'
geometry = 'POINT'
template = ''
has_m = 'DISABLED'
has_z = 'DISABLED'
#prjfile = '45.prj' # 7483 web mercator
spatialref = '' #arcpy.SpatialReference(prjfile) #web mercator

#create empty feature class
outfc = arcpy.CreateFeatureclass_management(outpath, newfc, geometry, template, has_m, has_z, spatialref)

#add attribute fields to feature class
arcpy.AddField_management(outfc, 'ID', 'LONG')
arcpy.AddField_management(outfc, 'SHAPE@XY', 'DOUBLE')
arcpy.AddField_management(outfc, 'scrname', 'TEXT', '', '', 15)
arcpy.AddField_management(outfc, 'tweetmsg', 'TEXT', '', '', 255)

#insert feature class records from text file
with open(textfile, 'rb') as f:
    reader = csv.reader(f, delimiter='\t', quoting=csv.QUOTE_NONE) #read tab-delimited data
    with arcpy.da.InsertCursor(outfc, ['ID', 'SHAPE@XY', 'scrname', 'tweetmsg']) as cursor:
        i = 1
        for row in reader:
            newpoint = (float(row[1]), float(row[0]))
            cursor.insertRow((i, newpoint, row[2], row[3]))
            print i, newpoint, row[2]
            #print i
            i = i + 1
    del cursor

