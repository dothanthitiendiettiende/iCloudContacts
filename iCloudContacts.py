#!/usr/bin/python
#manwhoami
import re, base64, plistlib, getpass, urllib2, sys
from xml.etree import ElementTree as ET

def dsidFactory(uname, passwd): #subroutine same as poof
    creds = base64.b64encode("%s:%s" % (uname, passwd))
    url = "https://setup.icloud.com/setup/authenticate/%s" % uname
    headers = {
        'Authorization': 'Basic %s' % creds,
        'Content-Type': 'application/xml',
    }
    request = urllib2.Request(url, None, headers)
    response = None
    try:
        response = urllib2.urlopen(request)
    except urllib2.HTTPError as e:
        if e.code != 200:
            if e.code == 401:
                return "HTTP Error 401: Unauthorized. Are you sure the credentials are correct?"
            elif e.code == 409:
                return "HTTP Error 409: Conflict. 2 Factor Authentication appears to be enabled. You cannot use this script unless you get your MMeAuthToken manually (generated either on your PC/Mac or on your iOS device)."
            elif e.code == 404:
                return "HTTP Error 404: URL not found. Did you enter a username?"
            else:
                return "HTTP Error %s." % e.code
        else:
            print e
            raise HTTPError
    content = response.read()
    DSID = int(plistlib.readPlistFromString(content)["appleAccountInfo"]["dsPrsID"]) #stitch our own auth DSID
    mmeAuthToken = plistlib.readPlistFromString(content)["tokens"]["mmeAuthToken"] #stitch with token
    return (DSID, mmeAuthToken)

def getCardLinks(dsid, token):
    url = 'https://p04-contacts.icloud.com/%s/carddavhome/card' % dsid
    headers = {
        'Depth': '1',
        'Authorization': 'X-MobileMe-AuthToken %s' % base64.b64encode("%s:%s" % (dsid, token)),
        'Content-Type': 'text/xml',
    }
    data = """<?xml version="1.0" encoding="UTF-8"?>
    <A:propfind xmlns:A="DAV:">
      <A:prop>
        <A:getetag/>
      </A:prop>
    </A:propfind>
    """
    request = urllib2.Request(url, data, headers)
    request.get_method = lambda: 'PROPFIND' #replace the get_method fxn from its default to PROPFIND to allow for successfull cardDav pull
    response = urllib2.urlopen(request)
    zebra = ET.fromstring(response.read())
    returnedData = """<?xml version="1.0" encoding="UTF-8"?>
    <F:addressbook-multiget xmlns:F="urn:ietf:params:xml:ns:carddav">
      <A:prop xmlns:A="DAV:">
        <A:getetag/>
        <F:address-data/>
      </A:prop>\n"""
    for response in zebra:
        for link in response:
            href = response.find('{DAV:}href').text #get each link in the tree
        returnedData += "<A:href xmlns:A=\"DAV:\">%s</A:href>\n" % href
    return "%s</F:addressbook-multiget>" % str(returnedData)

def getCardData(dsid, token, emailaddr):
    url = 'https://p04-contacts.icloud.com/%s/carddavhome/card' % dsid
    headers = {
        'Content-Type': 'text/xml',
        'Authorization': 'X-MobileMe-AuthToken %s' % base64.b64encode("%s:%s" % (dsid, token)),
    }
    data = getCardLinks(dsid, token)
    request = urllib2.Request(url, data, headers)
    request.get_method = lambda: 'REPORT' #replace the get_method fxn from its default to REPORT to allow for successfull cardDav pull
    response = urllib2.urlopen(request)
    zebra = ET.fromstring(response.read())
    i = 0
    contactList = []
    phoneList = []
    returnValue = ""
    for response in zebra:
        vcard = response.find('{DAV:}propstat').find('{DAV:}prop').find('{urn:ietf:params:xml:ns:carddav}address-data').text
        if vcard:
            for y in vcard.splitlines():
                if y.startswith("FN:"):
                    returnValue += "%s\n" % y[3:] 
                if y.startswith("TEL;"):
                    i+=1
                    z = y.split("type")[-1].split(":")[-1]
                    returnValue += "%s\n" % z
                if y.startswith("END:VCARD"):
                    returnValue += "---"
    returnValue = '---\n'.join(sorted(returnValue.split("---"))) #sorts based on name (first id)
    with open('%s.txt' % emailaddr, 'w') as output:
        output.write(returnValue.encode('ascii', 'ignore'))
    return returnValue + "\nFound %s contacts for user %s! Wrote contacts to %s.txt" % (i, emailaddr, emailaddr)

if __name__ == '__main__':
    user = raw_input("Apple ID: ")
    try: #in the event we are supplied with an DSID, convert it to an int
        int(user)
        user = int(user)
        emailaddr = user
    except ValueError: #otherwise we have an apple id email address
        emailaddr = user #used for output filename
        pass #no pun intended
    passw = getpass.getpass()
    tokenTime = dsidFactory(user, passw)
    try:
        (dsid, token) = tokenTime
    except ValueError:
        print tokenTime
        sys.exit()

    print getCardData(dsid, token, emailaddr) #start chain
