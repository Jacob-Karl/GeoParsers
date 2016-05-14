# -*- coding: utf-8 -*-

"""
name: location_parser.py
author: J.W. Karl
date: 5/2/13
purpose: parses each XML file in the input directory for geographic coordinates that match the nasty-looking regular expression below. Coordinates that are found are then converted to standardized decimal degree format. The regular expression is a modification (and simplification) of the GeoLucidate code. Outputs a csv file that can then be run through the loc_intersects.py script to create the locations.csv file for JournalMap
arguments: none, but paths and file variables need to be modified below
"""

import os, glob, csv, StringIO, re, sys
from decimal import Decimal, setcontext, ExtendedContext
from bs4 import BeautifulSoup

class UnicodeWriter(object):
    """
    Like UnicodeDictWriter, but takes lists rather than dictionaries.
    
    Usage example:
    
    fp = open('my-file.csv', 'wb')
    writer = UnicodeWriter(fp)
    writer.writerows([
        [u'Bob', 22, 7],
        [u'Sue', 28, 6],
        [u'Ben', 31, 8],
        # \xc3\x80 is LATIN CAPITAL LETTER A WITH MACRON
        ['\xc4\x80dam'.decode('utf8'), 11, 4],
    ])
    fp.close()
    """
    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = StringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoding = encoding
    
    def writerow(self, row):
        # Modified from original: now using unicode(s) to deal with e.g. ints
        self.writer.writerow([unicode(s).encode("utf-8") for s in row])
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = data.encode(self.encoding)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)
    
    def writerows(self, rows):
        for row in rows:
            self.writerow(row)

def _cleanup(parts):
    """
    Normalize up the parts matched by :obj:`parser.parser_re` to
    degrees, minutes, and seconds.

    >>> _cleanup({'latdir': 'south', 'longdir': 'west',
    ...          'latdeg':'60','latmin':'30',
    ...          'longdeg':'50','longmin':'40'})
    ['S', '60', '30', '00', 'W', '50', '40', '00']

    >>> _cleanup({'latdir': 'south', 'longdir': 'west',
    ...          'latdeg':'60','latmin':'30', 'latdecsec':'.50',
    ...          'longdeg':'50','longmin':'40','longdecsec':'.90'})
    ['S', '60', '30.50', '00', 'W', '50', '40.90', '00']

    """

    # trap for no hemisphere given
    if not (parts['dir11'] or parts ['dir12']):
        dir1 = "N"
        dir2 = "E"
    else:
        dir1 = (parts['dir11'] or parts['dir12']).upper()[0]
        dir2 = (parts['dir21'] or parts['dir22']).upper()[0]

    #bail if they're the same - indicating bounding box
    if dir1[0] == dir2[0]: return
    
    #assign latdir and longdir
    if dir1:
        if (dir1[0]=="N" or dir1[0]=="S"):
            latdir = dir1
            longdir = dir2
        else:
            latdir = dir2
            longdir = dir1
    else:
        latdir = ''
        longdir = ''
    #latdir = (parts['latdir'] or parts['latdir2']).upper()[0]
    #longdir = (parts['longdir'] or parts['longdir2']).upper()[0]

    latdeg = parts.get('latdeg')
    longdeg = parts.get('longdeg')

    latdecdeg = parts.get('latdecdeg')
    longdecdeg = parts.get('longdecdeg')

    latmin = parts.get('latmin', '00') or '00'
    longmin = parts.get('longmin', '00') or '00'

    latdecsec = parts.get('latdecsec', '')
    longdecsec = parts.get('longdecsec', '')

    if (latdecdeg and longdecdeg):
        latdeg += latdecdeg
        longdeg += longdecdeg
        latmin = '00'
        longmin = '00'
        latsec = '00'
        longsec = '00'

    if (latdecsec and longdecsec):
        latmin += latdecsec
        longmin += longdecsec
        latsec = '00'
        longsec = '00'
    else:
        latsec = parts.get('latsec', '') or '00'
        longsec = parts.get('longsec', '') or '00'

    return [latdir, latdeg, latmin, latsec, longdir, longdeg, longmin, longsec]


def _convert(latdir, latdeg, latmin, latsec, longdir, longdeg, longmin, longsec):
    """
    Convert normalized degrees, minutes, and seconds to decimal degrees.
    Quantize the converted value based on the input precision and
    return a 2-tuple of strings.

    >>> _convert('S','50','30','30','W','50','30','30')
    ('-50.508333', '-50.508333')

    """
    precision = Decimal('0.00001')

    latitude = Decimal(latdeg)
    latmin = Decimal(latmin)
    latsec = Decimal(latsec)

    longitude = Decimal(longdeg)
    longmin = Decimal(longmin)
    longsec = Decimal(longsec)

    if latsec > 59 or longsec > 59:
        #Assume that 'seconds' greater than 59 are actually a decimal
        #fraction of minutes
        latitude += (latmin +
                     (latsec / Decimal('100'))) / Decimal('60')
        longitude += (longmin +
                  (longsec / Decimal('100'))) / Decimal('60')
    else:
        latitude += (latmin +
                     (latsec / Decimal('60'))) / Decimal('60')
        longitude += (longmin +
                      (longsec / Decimal('60'))) / Decimal('60')

    if latdir == 'S':
        latitude *= Decimal('-1')

    if longdir == 'W':
        longitude *= Decimal('-1')

    lat_str = unicode(latitude.quantize(precision))
    long_str = unicode(longitude.quantize(precision))

    return (lat_str, long_str)

lat_degrees = ur'(?:-?1(?:[0-7][0-9]|80)|(?:-?0?[0-9][0-9])|(?:-?[0-9]))'

parser_re = re.compile(ur"""\b
    # Latitude direction, first position: one of N, S, NORTH, SOUTH
    ((?P<dir11>NORTH|SOUTH|EAST|WEST|[NSEW])\ ?)?
    # Latitude degrees: two digits 0-90
    (?P<latdeg>((?:-?[0-8][0-9])|(?:-?[0-9])))
    (?P<latdecdeg>\.\d{1,8})?
    # Degree mark or word separating degrees and minutes
    (?P<degmark>\ ?(?:º|°|˚|degrees))
    (?P<latminsec>
    # Latitude minutes: two digits 0-59
    (?P<latmin>[0-5]?[0-9])
    # If there was a degree mark before, look for punctuation after the minutes
    (\ |(?(degmark)(″|"|′|'|’|minutes|′′|'')))?
    (
    # Latitude seconds: two digits
    ((?P<latsec>(\d{1,2}))
    # Decimal fraction of minutes
    (?P<latdecsec>\.\d{1,8}))?)
    (?(degmark)(″|"|′|'|seconds|′′|'')?)
    )?
    # Latitude direction, second position, optionally preceded by a space
    (\ ?(?P<dir12>(?(dir11)|(NORTH|SOUTH|EAST|WEST|[NSEW]))))?
    # Optional word "latitude" or "longitude" offset by optional spaces
    (\ ?(LATITUDE|\ LONGITUDE)\ ?)?
    # Latitude/longitude delimiter: space, semicolon, comma, "by", or none
    (\ |\ BY\ |,\ ?|;\ ?)?
    # Longitude direction, first position: one of E, W, EAST, WEST
    (?(dir11)((?P<dir21>NORTH|SOUTH|EAST|WEST|[NSEW])\ ?))?
    # Longitude degrees: two or three digits
    (?P<longdeg>(?:-?1(?:[0-7][0-9]|80)|(?:-?0?[0-9][0-9])|(?:-?[0-9])))
    (?P<longdecdeg>\.\d{1,8})?   
    # If there was a degree mark before, look for another one here
    ((?(degmark)(\ ?(?:º|°|˚|degrees))))
    (?(latminsec)   #Only look for minutes and seconds in the longitude
    (?P<longminsec> #if they were there in the latitude
    # Longitude minutes: two digits
    (?P<longmin>[0-5]?[0-9])
    # If there was a degree mark before, look for punctuation after the minutes
    (\ |(?(degmark)(″|"|′|'|’|minutes|′′|'')))?
    # Longitude seconds: two digits
    ((?P<longsec>(\d{1,2}))
    # Decimal fraction of minutes
    (?P<longdecsec>\.\d{1,8}))?)
    (?(degmark)(″|"|′|'|seconds|′′|'')?)
    )
    #Longitude direction, second position: optionally preceded by a space
    (?(dir21)|\ ?(?P<dir22>(NORTH|SOUTH|EAST|WEST|[NSEW])))?
    # Optional word "latitude" or "longitude" offset by optional spaces
    (\ ?(LATITUDE|\ LONGITUDE)\ ?)?    
    \b
    """, re.VERBOSE | re.UNICODE | re.IGNORECASE)

################################################################################
### Begin parsing

outfile = '/Users/jason/Desktop/loc_parsing.csv' #sys.argv[1]  
indir = '/Volumes/XML Storage/Oxford/abopla5_xml' # sys.argv[2]
os.chdir(indir)

xmlList = glob.glob("*.xml")

### Set up CSV output #################################
csvfile = open(outfile, 'w')
out = UnicodeWriter(csvfile)
out.writerow(["doi","origLat","origLon","latDD","lonDD"])

### Get the XML data ##################################
#item = xmlList[2]
i = 0
for item in xmlList:
    soup = BeautifulSoup(open(item))
    article = soup.article
    #test = article('oasis:table')
    doi = article('article-id')[1] ## Not a stable way to get the DOI, assumes consistent order
    
    ### Return any coordinates that are found #############
    #for str in test.stripped_strings:
    text = ''
    for str in article.stripped_strings:
        text += ' ' + str
        
    #for str in article.stripped_strings:
    matches = parser_re.finditer(text)
    for match in matches:
        t= match.group()
        #print t
        t2 = _cleanup(match.groupdict())
        if not t2: break
        #print t2
        geodd = _convert(t2[0], t2[1], t2[2], t2[3], t2[4], t2[5], t2[6], t2[7])

        ### Write to the CSV
        i += 1
        print unicode(i) + ", " + doi.get_text() + ", " + t + ", " + geodd[0] + ", " + geodd[1]
        #out.writerow([doi.get_text(),t.split(",")[0],t.split(",")[1],geodd[0],geodd[1]])

