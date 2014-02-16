# Aaron Fraint, NYC DOT Bicycle Program
"""
    This script uses the Weather Underground API to build a CSV
    file of historic weather data.

    Pseudocode:
        - import libraries
        - setup global environment variables
        - define some functions
            >> build_query - returns a valid URL to access the API
            >> build_date_list - uses start/end dates to make a
                                 list of dates to query
            >> countdown - the API allows no more than 7 calls per minute.
                           as a result, this function kills time between
                           queries in order to avoid making too many calls
                           and getting the API account flagged
        - script body
            - define header row for output, and an output list
            - build the list of dates to query
            - for each date in that list:
                - build the date's query URL
                - call it and parse the JSON into a dictionary
                - slice into the dictionary to get at the daily summary
                - get 19 different data points about the day's weather
                - dump all of these values into a list
                - and then append this list to the output list
                - close the connection to the URL
                - hit the snooze button for 10 seconds to avoid making
                  too many calls
            - ... (after repeating for all dates) ...
            - write the output list to CSV file                     """
import os
import datetime
import urllib2
import json
import csv
import time

# ----------------------------------------------------------------- #
# after importing the necessary modules, it's time to setup some
# global environment variables that are called in the script body below
# ----------------------------------------------------------------- #

API_KEY = '6737a644ef181220' # for the account tied to aaron.fraint@gmail.com
filename = "2012_aug_to_july_2011_weather_data.csv" # the name of the output CSV

start_date = datetime.date(2011, 7, 1)
end_date = datetime.date(2010, 7, 1)

DIR = os.getcwd()
output = os.path.join(DIR, filename)

# ----------------------------------------------------------------- #
# these are function definitions that are called elsewhere in the script
# ----------------------------------------------------------------- #

def build_query(KEY, DATE):
    """ requires a weather underground API key
        and also a date in string format: "20131228"

        returns a URL for historic weather in NYC on
        the given DATE, using the API KEY        """
    URL = 'http://api.wunderground.com/api/' + KEY + \
          '/history_' + DATE + '/q/NY/New_York.json'
    return URL

def build_date_list(START_DATE, END_DATE):
    """ the start/end dates must be datetime objects,
        like datetime.date(2013, 12, 28)

        returns a list of text dates, like this:
            ["20131110", "20131109", "20131108", etc.]       """
    all_dates = []
    counter = 0
    the_day = START_DATE
    while the_day > END_DATE:
        # turn it from a datetime object into a string: "20131228"
        formatted_date = str(the_day).replace("-", "")
        all_dates.append(formatted_date)
        the_day = the_day - datetime.timedelta(1)
        counter += 1
    return all_dates

def countdown(AMOUNT):
    """ this function exists to waste time and make the script slower.
        Literally.
        Weather Underground has a 10 queries per minute rule.
        Python is so fast that we'd hit that within the first
        few miliseconds.                            """
    print '\tcounting down...'
    for i in reversed(range(AMOUNT + 1)[1:]):
        print '\t\t', "." * i, i
        time.sleep(1)

# ----------------------------------------------------------------- #
# ----------------------------------------------------------------- #
# this is the main body, where the weather underground API is used,
# and the desired pieces of information for each date are accessed,
# tossed into a list, and then appended to the list of output data
# ----------------------------------------------------------------- #
# ----------------------------------------------------------------- #

# setup the header row for the output CSV
header_row = ['year', 'month', 'day',
                'mintempi', 'meantempi', 'maxtempi',
                'minvisi', 'meanvisi', 'maxvisi',
                'fog', 'precipi', 'rain',
                'snow', 'snowdepthi', 'snowfalli',
                'meanwindspdi', 'monthtodatesnowfalli',
                'thunder', 'hail', 'humidity', 'precipsource']

# create a list to hold the data that will be dumped to CSV
query_results = [header_row]

# setup a list of dates that are going to be queried
dates_to_query = build_date_list(start_date, end_date)

for query_date in dates_to_query:
    # repeat the following steps for each date being queried

    # this is where the urllib2 and json libraries are used
    # they facilitate the web access of the JSON feed, and the
    # subsequent parsing into a python-friendly dictionary
    URL = build_query(API_KEY, query_date)
    f = urllib2.urlopen(URL)
    json_string = f.read()
    parsed_json = json.loads(json_string)

    # d is a slice into a list within two containing dictionaries
    # the data structure looks like this:
    #               json = {history: {dailysummary: [{key:value}]}
    d = parsed_json['history']['dailysummary'][0]

    # grab specific data points within the day's summary
    #
    # DATE has its own subdictionary, hence the extra key
    # also, they're unicode, so convert them to regular strings
    year = str(d['date']['year'])
    month = str(d['date']['mon'])
    day = str(d['date']['mday'])

    # the rest are just normal dictionary keys
    # TEMPERATURE: mean, min, and max
    mintempi = str(d['mintempi'])
    meantempi = str(d['meantempi'])
    maxtempi = str(d['maxtempi'])

    # VISIBILITY: mean min and max
    maxvisi = str(d['maxvisi'])
    meanvisi = str(d['meanvisi'])
    minvisi = str(d['minvisi'])

    # RAIN / FOG
    fog = str(d['fog'])
    precipi = str(d['precipi'])
    rain = str(d['rain'])

    # SNOW
    snow = str(d['snow'])
    snowdepthi = str(d['snowdepthi'])
    snowfalli = str(d['snowfalli'])

    # WINDSPEED
    meanwindspdi = str(d['meanwindspdi'])
    monthtodatesnowfalli = str(d['monthtodatesnowfalli'])

    # these would be interesting, but wunderground doesn't seem
    # to use them... they're all blank
    thunder = str(d['thunder'])
    hail = str(d['hail'])
    humidity = str(d['humidity'])
    precipsource = str(d['precipsource'])

    # package all the data up into a single list
    the_days_data = [year, month, day,
                    mintempi, meantempi, maxtempi,
                    minvisi, meanvisi, maxvisi,
                    fog, precipi, rain,
                    snow, snowdepthi, snowfalli,
                    meanwindspdi, monthtodatesnowfalli,
                    thunder, hail, humidity, precipsource]
    # add today's data to the list of lists
    query_results.append(the_days_data)

    # close the connection please!
    f.close()
    print 'processed: %s' % query_date
    countdown(10)

# ----------------------------------------------------------------- #
# ----------------------------------------------------------------- #
# save all that hard work!
# dump it into a CSV!
# ----------------------------------------------------------------- #
# ----------------------------------------------------------------- #

# write the data to a CSV file
# using the 'csv' python module
with open(output, 'wb') as csvfile:
    writer = csv.writer(csvfile, delimiter=',')
    for row in query_results:
        writer.writerow(row)
