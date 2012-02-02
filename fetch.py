# import os for file system functions
import os
# import flickrapi
# pip install flickrapi
import flickrapi
# import json
import json
# import regex
import re
# for date parsing
import time

def auth(frob, perms):
    print 'Please give us permission %s' % perms

# main program
def main():

  # get api key, secret and token from the user
  print "Enter your api key: ",
  api_key = raw_input()
  print "Enter your api secret: ",
  api_secret = raw_input()

  # create an unauthenticated flickrapi object
  flickr=flickrapi.FlickrAPI(api_key, api_secret)

  print "Open the following URL in your browser "
  print "This Url >>>> %s" % flickr.web_login_url(perms='read')

  print "When you're ready press ENTER",
  raw_input()

  print "Copy and paste the URL (from theopenphotoproject.org) here: ",
  frob_url = raw_input()

  print "\nThanks!"

  print "Parsing URL for the token...",
  match = re.search('frob=([^&]+)', frob_url)
  frob = match.group(1)
  token = flickr.get_token(frob)
  print "OK"

  # create an authenticated flickrapi object
  flickr = flickrapi.FlickrAPI(api_key, api_secret, token=token)

  # now we get the authenticated user's id
  print "Fetching user id...",
  user_resp = flickr.urls_getUserProfile()
  user_fields = user_resp.findall('user')[0]
  user_id = user_fields.get('nsid')
  print "OK"
  

# print "Enter your token: ",
# token = raw_input()
  per_page = 100

  (token, frob) = flickr.get_token_part_one('read')
  flickr.get_token_part_two((token, frob))

  # we'll paginate through the results
  # start at `page` and get `per_page` results at a time
  page=1

  # store everything in a list or array or whatever python calls this
  photos_out=[]

  # while True loop till we get no photos back
  while True:
    # call the photos.search API
    # http://www.flickr.com/services/api/flickr.photos.search.html
    print "Fetching page %d..." % page,
    photos_resp = flickr.people_getPhotos(user_id=user_id, per_page=per_page, page=page, extras='original_format,tags,geo,url_o,date_upload,date_taken,license,description')
    print "OK"

    # increment the page number before we forget so we don't endlessly loop
    page = page+1;

    # grab the first and only 'photos' node
    photo_list = photos_resp.findall('photos')[0]

    # if the list of photos is empty we must have reached the end of this user's library and break out of the while True
    if len(photo_list) == 0:
      break;

    # else we loop through the photos
    for photo in photo_list:
      # get all the data we can
      p = {}
      p['id'] = photo.get('id')
      p['permission'] = photo.get('ispublic')
      p['title'] = photo.get('title')
      p['license'] = getLicense(photo.get('license'))
      description = photo.findall('description')[0].text
      if description is not None:
        p['description'] = description

      if photo.get('latitude') != '0':
        p['latitude'] = photo.get('latitude')

      if photo.get('longitude') != '0':
        p['longitude'] = photo.get('longitude')

      if len(photo.get('tags')) > 0:
        p['tags'] = photo.get('tags').split(',')
      else:
        p['tags'] = []
      if photo.get('place_id') is not None:
        p['tags'].append("flickr:place_id=%s" % photo.get('place_id'))

      if photo.get('woe_id') is not None:
        p['tags'].append("geo:woe_id=%s" % photo.get('woe_id'))

      p['tags'] = ",".join(p['tags'])
      p['dateUploaded'] = photo.get('dateupload')
      p['dateTaken'] = "%d" % time.mktime(time.strptime(photo.get('datetaken'), '%Y-%m-%d %H:%M:%S'))
      p['photo'] = photo.get('url_o')

      print "  * Storing photo %s to fetched/%s.json..." % (p['id'], p['id']),
      f = open("fetched/%s.json" % p['id'], 'w')
      #f.write("%r" % {'id':photo_id,'title':photo_title,'url':constructUrl(photo)})
      f.write("%r" % p)
      f.close()
      print "OK"

# create a directory only if it doesn't already exist
def createDirectorySafe( name ):
  if not os.path.exists(name):
    os.makedirs(name)

# construct the url for the original photo
# currently this requires a pro account
def constructUrl( photo ):
  return "http://farm%s.staticflickr.com/%s/%s_%s_o.%s" % (photo.get('farm'), photo.get('server'), photo.get('id'), photo.get('originalsecret'), photo.get('originalformat'))

# map Flickr licenses to short names
def getLicense( num ):
  licenses = {}
  licenses['0'] = ''
  licenses['4'] = 'CC BY'
  licenses['5'] = 'CC BY-SA'
  licenses['6'] = 'CC BY-ND'
  licenses['2'] = 'CC BY-NC'
  licenses['1'] = 'CC BY-NC-SA'
  licenses['3'] = 'CC BY-NC-ND'

  if licenses[num] is None:
    return licenses[0]
  else:
    return licenses[num]

# check if a fetched, processed and errored directories exist
createDirectorySafe('fetched')
createDirectorySafe('processed')
createDirectorySafe('errored')
main()
