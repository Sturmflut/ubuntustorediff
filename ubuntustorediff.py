#!/usr/bin/python3

import sys
import simplejson
import time
import urllib.request
import hashlib

# App class
class App:
  def __init__(self, title, version, publisher, lastupdate, description, changelog, image, price, architecture, keywords, framework, whitelist_country_codes):
    realtitle = title.replace("&", "&amp;")

    self.title = realtitle
    self.version = version
    self.publisher = publisher
    self.lastupdate = lastupdate
    self.description = description
    self.changelog = changelog
    self.image = image
    self.price = price
    self.architecture = architecture
    self.keywords = keywords
    self.framework = framework
    self.whitelist_country_codes = whitelist_country_codes



# Print Usage
def usage():
  print("Usage: " + sys.argv[0] + " <output file>")


# Fetch the app list from the store
def fetch_app_details(appurl):
  result = simplejson.load(urllib.request.urlopen(appurl))

  if 'Error' in result:
    sys.exit("Could not fetch/parse JSON for the following URL: " + appurl)
  
  try:
    lastupdate = time.strptime(result['last_updated'], '%Y-%m-%dT%H:%M:%S.%fZ')
  except:
    lastupdate = time.strptime(result['last_updated'], '%Y-%m-%dT%H:%M:%SZ')
    
  return (result['version'], result['description'], result['changelog'], lastupdate, result['icon_url'], result['keywords'], result['framework'], result['whitelist_country_codes'])



# Fetch the app list from the store
def fetch_app_list():
  result = simplejson.load(urllib.request.urlopen("https://search.apps.ubuntu.com/api/v1/search?size=100000&page=1"))

  if 'Error' in result:
    sys.exit("Could not fetch/parse JSON.")
    
  appdatajson = result['_embedded']['clickindex:package']
    
  applist = []
    
  for app in appdatajson:
    (version, description, changelog, lastupdate, image, keywords, framework, whitelist_country_codes) = fetch_app_details(app['_links']['self']['href'])
    applist.append(App(app['title'], version, app['publisher'], lastupdate, description, changelog, image, app['price'], app['architecture'], keywords, framework, whitelist_country_codes))
    
  return applist


# Sort app entries by date (descending)
def sort_app_list_by_date(applist):
  applist.sort(key=lambda x: x.lastupdate, reverse=True)
  return applist


# Write the output RSS file
def write_rss_feed(filename, applist):
  f = open(filename, 'w')

  # Write RSS Header
  f.write("<?xml version=\"1.0\" encoding=\"utf-8\"?>\n")
  f.write("<rss version=\"0.91\">\n")
  f.write("<channel>\n")
  f.write("  <title>Ubuntu Store App Feed</title>\n")
  f.write("  <copyright>GPLv3</copyright>\n")
  f.write("  <link>http://www.ubuntu.com</link>\n")
  f.write("  <description>Ubuntu App Store RSS feed</description>\n")
  f.write("  <language>en</language>\n")
  f.write("  <lastBuildDate>" + time.strftime('%a, %d %b %Y %H:%M:%S GMT') + "</lastBuildDate>\n")
  f.write("  <pubDate>" + time.strftime('%a, %d %b %Y %H:%M:%S GMT') + "</pubDate>\n")
  f.write("  <generator>ubuntustorediff.py</generator>\n")
  
  for app in applist:
    f.write("  <item>\n")
    f.write("    <title>" + app.title + " " + app.version + "</title>\n")
    f.write("    <pubDate>" + time.strftime('%a, %d %b %Y %H:%M:%S GMT', app.lastupdate) + "</pubDate>\n")

    # GUID
    m = hashlib.md5(app.title.encode('utf-8') + "_".encode('utf-8') + app.version.encode('utf-8'))
    f.write("    <guid>" + m.hexdigest() + "</guid>\n")

    f.write("    <description><![CDATA["
        + "<img src=\"" + app.image + "\">"
        + "<b>Publisher</b>: " + app.publisher
        + "<br/><br/><b>Price</b>: " + "{:.1f}".format(app.price)
        + "<br/><br/><b>Description</b>: " + app.description.replace('\n', '<br/>').replace('\r', '<br/>')
        + "<br/><br/><b>Architecture(s)</b>: " + ', '.join(app.architecture)
        + "<br/><br/><b>Framework(s)</b>: " + ', '.join(app.framework)
        + "<br/><br/><b>Keyword(s)</b>: " + ', '.join(app.keywords)
        + "<br/><br/><b>Whitelisted countries</b>: " + ', '.join(app.whitelist_country_codes)
        + "<br/><br/><b>Changelog</b>: "
        + (" " if app.changelog is None else app.changelog)
        + "]]></description>\n")
    f.write("  </item>\n")
    
  f.write("</channel>\n")
  f.write("</rss>\n")
    



if __name__ == '__main__':
  if(len(sys.argv) != 2):
    usage()
    sys.exit()
  
  applist = fetch_app_list()
  applist = sort_app_list_by_date(applist)
  write_rss_feed(sys.argv[1], applist)
