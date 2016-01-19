import sys, getopt
import json
import collections
import base64

def main(argv):
    inputfile = ''
    outputfile = ''
    try:
       opts, args = getopt.getopt(argv,"hi:o:",["ifile=","ofile="])
    except getopt.GetoptError:
       print('generatejson.py -i  -o ')
       sys.exit(2)
    for opt, arg in opts:
          if opt == '-h':
             print('generatejson.py -i  -o ')
             print('Input File format:')
             print('FileURI Feature:maxResults ...')
             sys.exit()
          elif opt in ("-i", "--ifile"):
             inputfilename = arg
          elif opt in ("-o", "--ofile"):
             outputfilename = arg

    inputFile = open(inputfilename, 'r')
    lineCount = 0
    requestsJsonObj = {}
    requestArray = []
    for inputLine in inputFile:
      lineCount = lineCount + 1
      print(inputLine)
      wordCount = 0
      contentJsonObj = {}
      imageJsonObj = {}
      featureJsonObj = []
      lineWords = inputLine.split(" ")
      if len(lineWords) < 2:
          print("Invalid input file format")
          print("Valid Format: FileURI feature:maxResults feature:maxResults ....")
          sys.exit()
      for word in lineWords:
          if wordCount == 0:
              imageFile = open(word, 'rb')
              contentJsonObj['content'] = base64.b64encode(imageFile.read()).decode('utf-8')
              #contentJsonObj['content'] = base64.b64encode(imageFile.read())
              #print("img:" + word)
          else:
              detectValues = word.split(":")
              valueCount = 0
              featureDict = collections.OrderedDict()
              for values in detectValues:
                if valueCount == 0:
                    detectionType = getDetectionType(values)
                    featureDict['type'] = detectionType
                    print("detect:" + detectionType)
                else:
                    maxResults = values.rstrip()
                    featureDict['maxResults'] = maxResults
                    print("results: " + maxResults)
                valueCount = valueCount + 1
              featureJsonObj.append(featureDict)
          wordCount = wordCount + 1
      imageJsonObj['features'] = featureJsonObj
      imageJsonObj['image'] = contentJsonObj
      requestArray.append(imageJsonObj)
    requestsJsonObj['requests'] = requestArray
    with open(outputfilename, 'w') as outfile:
        json.dump(requestsJsonObj, outfile)
    #j = json.dumps(requestsJsonObj)
    #outputfile = open(outputfilename,'w')
    #print >> outputfile, j


def getDetectionType( detectNum ):
   if detectNum == "1":
       return "FACE_DETECTION"
   elif detectNum == "2":
       return "LANDMARK_DETECTION"
   elif detectNum == "3":
       return "LOGO_DETECTION"
   elif detectNum == "4":
       return "LABEL_DETECTION"
   elif detectNum == "5":
       return "TEXT_DETECTION"
   elif detectNum == "6":
       return "SAFE_SEARCH_DETECTION"
   return "TYPE_UNSPECIFIED";

if __name__ == "__main__":
   main(sys.argv[1:])

