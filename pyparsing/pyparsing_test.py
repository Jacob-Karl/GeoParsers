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
        return {"latitude":lat, "longitude":lon}
    



## Parsing elements
digits = Word(nums)

coordPart = Combine(digits + Optional(Literal(".") + digits))

degSign = Literal("º") | Literal('°') | Literal('˚') | CaselessLiteral("degrees")
minSign = Literal("’") | Literal("′") | Literal("′") | Literal("'") | CaselessLiteral("minutes")
secSign = Literal('″') | Literal('"') | Literal("′′") | Literal("''") | Literal('”') | CaselessLiteral("seconds")
negSign = Literal("-")

latHemi = oneOf("north south N S", caseless=True)
latHemi.setParseAction(formatHemi)
lonHemi = oneOf("east west E W", caseless=True)
lonHemi.setParseAction(formatHemi)

latDeg = coordPart + Suppress(degSign)
latDeg.setParseAction(validateLatDeg)

lonDeg = coordPart + Suppress(degSign)
lonDeg.setParseAction(validateLonDeg)

mins = coordPart + Suppress(Optional(minSign))
mins.setParseAction(validateMinSec)
secs = coordPart + Suppress(Optional(secSign))
secs.setParseAction(validateMinSec)

mins = coordPart + Suppress(Optional(minSign))
sec = coordPart + Suppress(Optional(secSign))

separator = Suppress(Optional(Literal(',') | Literal(";") | oneOf("by and", caseless=True)))
fluff = Suppress(Optional(CaselessLiteral("latitude of") | CaselessLiteral("longitude of") | oneOf("latitude lat lat. lat: longitude lon lon. lon:", caseless=True) ))

latPart = fluff + Optional(latHemi.setResultsName('latHemi')) + Optional(negSign.setResultsName('latNeg')) + latDeg.setResultsName('latDeg') + Optional(mins.setResultsName('latMin')) + Optional(secs.setResultsName('latSec')) + Optional(latHemi.setResultsName('latHemi')) + fluff
lonPart = fluff + Optional(lonHemi.setResultsName('lonHemi')) + Optional(negSign.setResultsName('latNeg')) + lonDeg.setResultsName('lonDeg') + Optional(mins.setResultsName('lonMin')) + Optional(secs.setResultsName('lonSec')) + Optional(lonHemi.setResultsName('lonHemi')) + fluff

coordinateParser = latPart + separator + lonPart

# Questions for when we have internet
# 1. test driven library for Python
# 2. case select format
# 3. rounding, sig digits of results
# 4. figure out why parseaction isn't working for mins > 60
# 5. Construct a test set from articles (JournalMap database dump) of locations that should parse and those that should not.
# 6. How common is it to have an article with coordinates that doesn't use degree signs? - Strategy might be to have one parser that requires degree signs but is otherwise more flexible and then a second parser that doesn't require the degree sign but is much more strict for other formatting.
# 7. Look on trello board for coordinates that aren't parsing.

## Test the parser
test = "45º 23' 12'', 123º 23' 56''"  # Should return lat:45.38667, lon:123.39889
test = "45.234º, 123.43º"  # Should return lat: 45.234, lon: 123.43
test = "-45º 23' 12'', -123º 23' 56''"  # Should return lat:-45.38667, lon:-123.39889
test = "32º21'59''N, 115º 23' 14''W"
test = "12 43 56 North, 23 56 12 East"
test = "expects to find coordinates: 52 15 10N, 0 01 54W"  #  No degree sign, so don't parse
test = "expects to find coordinates: 52 35 31N, 1 28 05E"  #  no degree sign, so don't parse
test = "30° 47' N, 34° 46' E"
test = "Avdat site is located in the Central Negev highlands, (30° 47' N, 34° 46' E) (Fig. 1). It is an arid ecosystem with annual precipitation of 95 mm (range 20–180 mm). At the winter 2005 rain precipitation was relatively low in Avdat with 70.7 mm and average max temperature 25.4 °C in April. At 2006 precipitation in Avdat went lower with 58.8 mm and 24.1 average max temperature 24.1 °C (Department of Solar Energy and Environmental Physics, Ben-Gurion University of the Negev). The vegetation is dominated by dwarf shrubs Haloxylon scoparium (Pomel), which serves as the focal shrub patch in this site. The average shrub cover is 25% (Zaady et al., 1997). A Transplant experiment was conducted on the Sede Zin plateau in the Central Negev highlands. It is located 10 km north from Avdat research site, near Midreshet Ben-Gurion (30°51' N, 34° 47' E) and similar in vegetation and climate. Lehavim is located in the northern Negev desert (31°21' N, 34°49' E) (Fig. 1) at the transition between the Mediterranean and the semi-arid climate zones, with an average annual precipitation of 305 mm (range of 78–504 mm, (1953–1995) (Baram, 1996)). Rainfall occurs between December to March. Rain precipitation at 2005 and 2006 was relatively low in Lehavim, with 277 mm and 205 mm respectively. Average maximum Temperatuire in April was 25.2 °C and 24.7 °C respectively (Lehavim LTER station). The vegetation is a shrubland, dominated by the dense, spiny shrub Sarcopoterium spinosum (Linnaeus), which serves in this study as the focal shrub patch. Inter-shrub open patches are covered with biogenic crust, of up to 15 mm thickness (Zaady et al., 1997). Herbaceous vegetation appears shortly after the first rains and persists for 3–5 months, depending on the amount and distribution of the precipitation (Giladi et al., 2007). The average shrub cover is 42% (Zaady et al., 1997)."
test = "expects to find coordinates: 'AT; 1 spm, CN 3-41, 21°00′ N, 112°30′ E, muddy sand'"
test = 'expects to find coordinates: 27°43.886, 34°15.663'
test = 'expects to find coordinates: 49°17’13”N, 13°40’18”E'
test = 'expects to find coordinates: 45.9215º; -76.6219º'
test = "expects to find coordinates: (latitude 32°47′47″ S and longitude 26°50′56″ E)"
test = "expects to find coordinates: N15°46′ W87°00',"
test = "Sidi Ameur and Himalatt sites of the Algerian Sahara. A. The hypersaline Sidi Ameur and Himalatt sites are respectively located 55 km to the northwest and 25 km to the southeast of Bou Saâda, Algeria (latitude of 35°13', longitude of 4°11' and altitude of 663 m). B. Representative images of Sidi Ameur Lake depicting the barren landscape and high salt concentrations."
test = "latitude of 35°13', longitude of 4°11'"
test="The field experiments took place at the Nevada Desert FACE (Free-Air CO2 Enrichment) Facility (NDFF; Jordan et al., 1999) located within the Department of Energy’s Nevada Test Site (NTS), about 100 km from the city of Las Vegas, NV, USA (36°49'N, 115°55'W, 965–970 m elevation). The NDFF has been in operation since April 1997, consisted of three control circular plots fumigated at ambient [CO2] (380 ppm), and three plots at elevated [CO2] (550 ppm). Within the FACE rings, an intact Mojave Desert ecosystem is exposed continuously to the target atmospheric CO2 concentrations (Jordan et al., 1999), although conditional shut-downs occurred during high winds (>7 m s-1) and freezing temperatures. During daylight hours, when plants are photosynthetically active, CO2 fumigation occurred over 95% of the time on an annual basis."
test = "Seeds of P. villosa were collected near the Ordos Sandland Ecological Station (OSES, 39°02'N, 109°21'E) of the Institute of Botany, Chinese Academy of Sciences. On 2 June 2006, the seeds were planted in 2.0 m × 1.5 m × 0.5 m containers full of sand under natural daylight. After 23 days, 60 similar-sized seedlings of P. villosa were transplanted into four 450 cm × 40 cm × 25 cm containers, each with 15 plants. All the containers were placed on benches in a greenhouse at OSES. All the plants in each container were 30 cm apart and with water-proof sheets between them to ensure that nutrients, water and roots did not interfere with each other. Thus competition among plants within each container could be ignored. All the plants in a same container were subjected to one of the four treatments consisting of two levels of MP (non-MP vs. MP 1 min d-1) and two levels of water availability (200 ml d-1 vs. 400 ml d-1). There were 15 replicates for each treatment."

### Don't parse correctly
# Should return an exception, but instead calculates latitude as 6º 10'
test = "expects to find coordinates: 5°70'N, 73°46'W"  # Minutes greater than 60


## Structuring the parser into the document reader
for result, start, end in coordinateParser.scanString(test):
    print coordinate(result).calcDD()