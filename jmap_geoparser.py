#!/usr/bin/env python
# -*- coding: utf-8 -*-

### Call with:
### test = "45º 23' 12'', 123º 23' 56''"  
### assert coordinate(coordinateParser.parseString(test)).calcDD() == {'latitude': 45.38667, 'longitude': 123.39889}

from pyparsing import *

## Parsing validation functions
def validateLatDeg(nums):
    if abs(float(nums[0])) >= 90:
        raise ParseException("Invalid Latitude Degrees: %s" % nums[0])

def validateLonDeg(nums):
    if abs(float(nums[0])) >= 180:
        raise ParseException("Invalid Longitude Degrees: %s" % nums[0])

def validateMinSec(nums):
    if float(nums[0]) >= 60:
        raise ParseException("Invalid minute or seconds: %s" % nums[0])

def formatHemi(hemi):
    if hemi[0].lower()=='north': return 'n'
    if hemi[0].lower()=='south': return 's'
    if hemi[0].lower()=='east': return 'e'
    if hemi[0].lower()=='west': return 'w'


## Establish coordinate object class
class coordinate(object):
    latDeg = 0
    latMin = 0
    latSec = 0
    latHemi = 'N'
    lonDeg = 0
    lonMin = 0
    lonSec = 0
    lonHemi = 'E'
    
    def __init__(self, parseDict):
        self.parseDict = parseDict
        self.latDeg = float(parseDict.latDeg[0])
        if 'latMin' in parseDict: self.latMin = float(parseDict.latMin[0])
        if 'latSec' in parseDict: self.latSec = float(parseDict.latSec[0])
        if 'latNeg' in parseDict: self.latHemi = 'S'
        if 'latHemi' in parseDict: self.latHemi = parseDict.latHemi[0]
        
        self.lonDeg = float(parseDict.lonDeg[0])
        if 'lonMin' in parseDict: self.lonMin = float(parseDict.lonMin[0])
        if 'lonSec' in parseDict: self.lonSec = float(parseDict.lonSec[0])
        if 'lonNeg' in parseDict: self.lonHemi = 'W'
        if 'lonHemi' in parseDict: self.lonHemi = parseDict.lonHemi[0]
    
    def calcDD(self):
        latSign = 1
        lonSign = 1
        if self.latHemi.upper() == 'S': latSign = -1
        if self.lonHemi.upper() == 'W': lonSign = -1
        lat = latSign*(self.latDeg + self.latMin/60 + self.latSec/3600)
        lon = lonSign*(self.lonDeg + self.lonMin/60 + self.lonSec/3600)
        return {"latitude":round(lat,5), "longitude":round(lon,5)}
    



## Parsing elements
digits = Word(nums)

degSign = Literal("º") | Literal('°') | Literal(' ͦ') | Literal('˚') | Literal('º') | Literal('ø') | CaselessLiteral("degrees")  # º|°|˚|°|degrees|&deg;
minSign = Literal("’") | Literal("′") | Literal("'") | Literal("‛") | Literal("‘") | Literal('ʹ') | Literal('ʼ')  | CaselessLiteral("minutes")  # ″|"|′|'|’|minutes|′′|''
secSign = Literal('″') | Literal('"') | Literal("′′") | Literal("''") | Literal("’’") | Literal("‛‛") | Literal("‘‘") | Literal("ʹʹ") | Literal("ʼʼ") | Literal('“') | Literal('”') | Literal('‟') | Literal('〞') | Literal('＂') | Literal('ʺ') | Literal('˝')| CaselessLiteral("seconds")
negSign = Literal('-') | Literal('−') | Literal('–') | Literal('—') | Literal('―') | Literal('‒')
decPoint = Literal(".") | Literal(".")

coordPart = Combine(digits + Optional(decPoint + digits))

latHemi = oneOf("north south N S", caseless=True)
latHemi.setParseAction(formatHemi)
lonHemi = oneOf("east west E W", caseless=True)
lonHemi.setParseAction(formatHemi)

latDeg = coordPart + Suppress(degSign)
#latDeg = coordPart + Suppress(Optional(degSign))
latDeg.setParseAction(validateLatDeg)

lonDeg = coordPart + Suppress(degSign)
#lonDeg = coordPart + Suppress(Optional(degSign))
lonDeg.setParseAction(validateLonDeg)

mins = coordPart + Suppress(Optional(minSign))
mins.setParseAction(validateMinSec)
secs = coordPart + Suppress(Optional(secSign))
secs.setParseAction(validateMinSec)

separator = Suppress(Optional(Literal(',') | Literal(";") | oneOf("by and", caseless=True)))
fluff = Suppress(Optional(CaselessLiteral("latitude of") | CaselessLiteral("longitude of") | oneOf("latitude lat lat. lat: longitude long long. lon lon. lon:", caseless=True) ))

# Option that includes provision for commas between degrees, minutes, and seconds (pretty uncommon, but prevents other simpler versions from parsing
#latPart = fluff + Optional(latHemi.setResultsName('latHemi')) + Optional(negSign.setResultsName('latNeg')) + latDeg.setResultsName('latDeg') + Optional(Literal(",")) + Optional(mins.setResultsName('latMin')) + Optional(Literal(",")) + Optional(secs.setResultsName('latSec')) + Optional(latHemi.setResultsName('latHemi')) + fluff
#lonPart = fluff + Optional(lonHemi.setResultsName('lonHemi')) + Optional(negSign.setResultsName('latNeg')) + lonDeg.setResultsName('lonDeg') + Optional(Literal(",")) + Optional(mins.setResultsName('lonMin')) + Optional(Literal(",")) + Optional(secs.setResultsName('lonSec')) + Optional(lonHemi.setResultsName('lonHemi')) + fluff

# Standard version (no commas between degrees, minutes, and seconds.
latPart = fluff + Optional(latHemi.setResultsName('latHemi')) + Optional(negSign.setResultsName('latNeg')) + latDeg.setResultsName('latDeg') + Optional(mins.setResultsName('latMin')) + Optional(secs.setResultsName('latSec')) + Optional(latHemi.setResultsName('latHemi')) + fluff
lonPart = fluff + Optional(lonHemi.setResultsName('lonHemi')) + Optional(negSign.setResultsName('latNeg')) + lonDeg.setResultsName('lonDeg') + Optional(mins.setResultsName('lonMin')) + Optional(secs.setResultsName('lonSec')) + Optional(lonHemi.setResultsName('lonHemi')) + fluff

coordinateParser = latPart + separator + lonPart