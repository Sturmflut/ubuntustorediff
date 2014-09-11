#!/usr/bin/python3

import sys
import simplejson
import time
import urllib.request

# App class
class App:
  def __init__(self, name, version, publisher, lastupdate, description, changelog):
    self.name = name
    self.version = version
    self.publisher = publisher
    self.lastupdate = lastupdate
    self.description = description
    self.changelog = changelog



# Print Usage
def usage():
  print("Usage: " + sys.argv[0] + " <output file>")


# Fetch the app list from the store
def fetch_app_details(appurl):
  result = simplejson.load(urllib.request.urlopen(appurl))

  if 'Error' in result:
    sys.exit("Could not fetch/parse JSON for the following URL: " + appurl)
    
  lastupdate_raw = time.strptime(result['last_updated'], '%Y-%m-%dT%H:%M:%S.%fZ')
  lastupdate = time.strftime('%a, %d %b %Y %H:%M:%S GMT', lastupdate_raw);
    
  return (result['version'], result['description'], result['changelog'], lastupdate)



# Fetch the app list from the store
def fetch_app_list():
  result = simplejson.load(urllib.request.urlopen("https://search.apps.ubuntu.com/api/v1/search?q=architecture:armhf&size=100000&page=1"))

  if 'Error' in result:
    sys.exit("Could not fetch/parse JSON.")
    
  appdatajson = result['_embedded']['clickindex:package']
    
  applist = []
    
  for app in appdatajson:
    (version, description, changelog, lastupdate) = fetch_app_details(app['_links']['self']['href'])
    applist.append(App(app['name'], version, app['publisher'], lastupdate, description, changelog))
    
  return applist



# Write the output RSS file
def write_rss_feed(filename, applist):
  f = open(filename, 'w')

  # Write RSS Header
  f.write("<?xml version=\"1.0\" encoding=\"utf-8\"?>\n")
  f.write("<rss version=\"2.0\">\n")
  f.write("<channel>\n")
  f.write("  <title>Ubuntu Store App Feed</title>\n")
  
  for app in applist:
    f.write("  <item>\n")
    f.write("    <title>" + app.name + " " + app.version + "</title>\n")
    f.write("    <pubDate>" + app.lastupdate + "</pubDate>\n")
    f.write("    <guid>" + app.name + "_" + app.version + "_" + app.lastupdate + "</guid>\n")
    f.write("    <description><![CDATA[Changelog: " + app.changelog + "]]></description>\n")
    f.write("  </item>\n")
    
  f.write("</channel>\n")
  f.write("</rss>\n")
    



if __name__ == '__main__':
  if(len(sys.argv) != 2):
    usage()
    sys.exit()
  
  applist = fetch_app_list()
  write_rss_feed(sys.argv[1], applist)
