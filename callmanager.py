#-------------------------------------------------------------------------------
# Name:         callmanager
# Purpose:      Extract data from callmanager and Cisco Unity servers such as
#               device details, user details and voicemail details
#
# Author:       Julian Hobley
#
# Created:     26/10/2012
# Copyright:   (c) JBHobley 2012
# Licence:     <your licence>
#
#   v1.2 - Added setCMQuery, setCMServer, getText methods
#
#-------------------------------------------------------------------------------
#!/usr/bin/env python



def main():
    print 'Callmanager module should be imported into another script and used from there'


class callmanager:
    def __init__(self,server=None,query=None):
        self.CMServer=server
        self.CMquery=query
        self.rawXML=None
        self.CMList=None

    def __str__(self):
        if(self.CMList):
            result="\n"
            line=""
            for row in self.CMList:
                line='\t'.join(map(str,row))

                #for item in row:
                #    line=line+"\t"+str(item)
                result=result+"\n"+line
            return(result)
        elif(self.rawXML):
            return(self.rawXML)
        elif(self.CMServer):
            result=self.CMServer+"\t"+self.CMquery
            return(result)
        else:
            return("The object has not yet been populated")

    def getText(self):
        return self.__str__()

    def getList(self):
        return self.CMList

    def setCredentials(self,password,username='ccmadministrator'):
        import urllib2
        # Now create a PasswordMgr object to pass the authentication to the server
        self.pwdb = urllib2.HTTPPasswordMgrWithDefaultRealm()
        self.pwdb.add_password(None, self.CMServer,username,password)

    def setCMQuery(self,query):
        self.CMquery=query

    def setCMServer(self,server):
        self.CMServer=server

    def getCMData(self):
        '''Interrogate callmanager (or a file://) and populate self.rawXML'''
        print "\nRunning query..."
        if(self.CMServer[0:4].upper()=='FILE'): # If a file url is given, load direct from file)
            self.readXMLFile(self.CMServer[7:])
        else:
            self.CUCM_SOAP()
        return(0)

    def writeCSV(self,filepath):
        ''' Write list of list (self.CMList) out to csv file '''
        print 'Writing CSV file'
        try:
            import csv

            outFile = csv.writer(open(filepath,'wb'))
            for list in self.CMList:
                outFile.writerow(list)
            return(0)
        except TypeError:
            print('An error has occurred: The list is empty')
            return(1)
        except Exception as error:
            print 'An error has occured:', error
            return(1)


    def parseET(self,rowTag='row', reqfields='*'):
        ''' Parse an xml string (self.rawXML) and populate a list of lists (self.CMList) containing the data '''

        import xml.etree.ElementTree as ET

        print '\nParsing data'

        # Initialise the list of lists
        lrows=[]
        getheader=1

        # Parse the xml string into an Element
        root = ET.fromstring(self.rawXML)

        # Identify all the rows
        for row in root.iter(rowTag):
            if reqfields!='*':
                # Initialise the inner list
                lrow=[]
                hrow=reqfields
                for field in reqfields:
                    lrow.append(row.find(field).text)
            else:
                lrow=[]
                hrow=[]
                # Iterate through the rows, appending each item to the inner list
                for item in row:
                    lrow.append(item.text)
                    if getheader<>0:
                        hrow.append(item.tag)
            # Append  the inner list into the list of lists
            if getheader<>0:
                lrows.append(hrow)
                getheader=0

            lrows.append(lrow)

        self.CMList=lrows
        # Return the resulting lists

        return(0)

    def CUCM_SOAP(self):
        ''' Connect to a callmanager server and execute a SQL query, returning a handle to the connection '''

        import urllib2

        # Build envelope template - %s will be substituted for the message content
        env_template = '<SOAP-ENV:Envelope  \
                    xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" \
                    xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/" \
                    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" \
                    xmlns:xsd="http://www.w3.org/2001/XMLSchema"> \
                        <SOAP-ENV:Header/> \
                        <SOAP-ENV:Body> \
                                    %s \
                        </SOAP-ENV:Body> \
                    </SOAP-ENV:Envelope>'

        # Build message - %s will be  substituted for the sql statement  (passed as a parameter)
        message = '<axl:executeSQLQuery xmlns:axl="http://www.cisco.com/AXL/7.0" sequence="1234"> \
                       <sql>%s</sql> \
                   </axl:executeSQLQuery> '

        # Do the actual substitutions
        message = message % self.CMquery
        postdata = env_template%(message)
        # print postdata

        # Now create an authentication handler to open the https request
        try:
            handler = urllib2.HTTPBasicAuthHandler(self.pwdb)
        except:
            print 'Sorry, no PasswordMgr object initialised - use setCredentials to set a password'
            return(1)
        opener=urllib2.build_opener(handler)

        # Install the opener to use it in future urlopen requests
        urllib2.install_opener(opener)

        # Request the SOAP results
        # result=urllib2.urlopen(service)
        # print result.read()

        # Create a request object and add the required headers
        request=urllib2.Request(self.CMServer)
        request.add_data(postdata)
        request.add_header("Content-type", "text/xml; charset=\"UTF-8\"")
        request.add_header("Content-length", "%d" % len(postdata))
        request.add_header("SOAPAction", "\"\"")

        # Open the request to return the results
        urlConnection=urllib2.urlopen(request)

        # Return a handle to the connection
        self.rawXML = urlConnection.read()

    def readXMLFile(self,filepath):
        ''' Read in the XML string from a previously saved xml file'''
        infile = open(filepath,'r')
        self.rawXML = infile.read()
        pass



    def getUnityData(self,query=''):
        ''' Connect to a callmanager server and execute a SQL query, returning a handle to the connection '''

        import urllib2

        # Now create an authentication handler to open the https request
        handler = urllib2.HTTPBasicAuthHandler(self.pwdb)
        opener=urllib2.build_opener(handler)

        # Install the opener to use it in future urlopen requests
        urllib2.install_opener(opener)

        # Request the SOAP results
        request=urllib2.Request(self.CMServer)

        result=urllib2.urlopen(request)

        # print result.read()
        self.rawXML = result.read()
        pass


if __name__ == '__main__':
    main()

