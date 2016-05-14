#parser_testing.py
import os, sys, re, StringIO
sys.path.append('/Users/Jason/Dropbox/JournalMap/scripts/GeoParsers')
#from jmap_geoparser_re import *
from jmap_geoparser import *

#def test_parsing():
test = "blah blah blah 45º 23' 12'', 123º 23' 56'' and blah blah blah 32º21'59''N, 115º 23' 14''W blah blah blah"  
coords = coordinateParser.searchString(test)
for coord in coords:
    assert coordinate(coord).calcDD(), "Coordinate Transform Error for "+str(coord)


test = "45.234º, 123.43º" 
assert coordinate(coordinateParser.parseString(test)).calcDD() == {'latitude': 45.234, 'longitude': 123.43}

test = "-45º 23' 12'', -123º 23' 56''"  
assert coordinate(coordinateParser.parseString(test)).calcDD() == {'latitude': -45.38667, 'longitude': 123.39889}

test = "32º21'59''N, 115º 23' 14''W"
assert coordinate(coordinateParser.parseString(test)).calcDD() == {'latitude': 32.36639, 'longitude': -115.38722}

test = "12 43 56 North, 23 56 12 East"
assert coordinate(coordinateParser.parseString(test)).calcDD() == {'latitude': 12.73222, 'longitude': 23.93667}

test = "52 15 10N, 0 01 54W"
assert coordinate(coordinateParser.parseString(test)).calcDD() == {'latitude': 52.25278, 'longitude': -0.03167}

test = "52 35 31N, 1 28 05E"
assert coordinate(coordinateParser.parseString(test)).calcDD() == {'latitude': 52.59194, 'longitude': 1.46806}

test = "30° 47' N, 34° 46' E"
assert coordinate(coordinateParser.parseString(test)).calcDD() == {'latitude': 30.78333, 'longitude': 34.76667}

'''    
test = "AT; 1 spm, CN 3-41, 21°00′ N, 112°30′ E"
for result, start, end in coordinateParser.scanString(test):
    assert coordinate(result).calcDD() == {'latitude': 21.0, 'longitude': 112.5}

test = '27°43.886, 34°15.663'
assert coordinate(coordinateParser.parseString(test)).calcDD() == {'latitude': 27.73143, 'longitude': 34.26105}    

test = '49°17’13”N, 13°40’18”E'
assert coordinate(coordinateParser.parseString(test)).calcDD() == {'latitude': 49.28694, 'longitude': 13.67167}

test = '45.9215º; -76.6219º'
assert coordinate(coordinateParser.parseString(test)).calcDD() == {'latitude': -45.9215, 'longitude': 76.6219}

test = "latitude 32°47′47″ S and longitude 26°50′56″ E"
assert coordinate(coordinateParser.parseString(test)).calcDD() == {'latitude': -32.79639, 'longitude': 26.84889}

test = "N15°46′ W87°00'"    
assert coordinate(coordinateParser.parseString(test)).calcDD() == {'latitude': 15.76667, 'longitude': -87.0}

test = "latitude of 35°13', longitude of 4°11'"
assert coordinate(coordinateParser.parseString(test)).calcDD() == {'latitude': 35.21667, 'longitude': 4.18333}    

test = "expects to find coordinates: 52 degrees, 42 minutes north, 124 degrees, 50 minutes west"
assert coordinate(coordinateParser.parseString(test)).calcDD() == {'latitude': 52.7, 'longitude': -124.83333}

# Should return an exception, but instead calculates latitude as 6º 10'
#test = "expects to find coordinates: 5°70'N, 73°46'W"  # Minutes greater than 60    

#test = "expects not to find: 4.5–5.0 "
'''   