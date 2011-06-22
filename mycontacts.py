import cgi

try:
  from xml.etree import ElementTree
except ImportError:
  from elementtree import ElementTree
import gdata.spreadsheet.service
import gdata.service
import atom.service
import gdata.alt.appengine
import gdata.spreadsheet
import atom
import gdata.urlfetch
# Use urlfetch instead of httplib
gdata.service.http_request_handler = gdata.urlfetch
import getopt
import sys
import string
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.ext.webapp.util import run_wsgi_app
import os
from google.appengine.ext.webapp import template

class ContactData:

     def __init__(self=None, index=None, firstname=None, lastname=None, phonenumber=None, email=None):
	self.index = index	
	self.lastname = lastname
	self.phonenumber = phonenumber
     	self.firstname = firstname
	self.email = email

     def to_xml(self):
	str = """<contact>
		 <index>%s</index>
		 <firstname>%s</firstname>
		 <lastname>%s</lastname>
		 <phonenumber>%s</phonenumber>
		 <email>%s</email>
	</contact>"""
	return str % (self.index, self.firstname, self.lastname, self.phonenumber, self.email) 



class GetContactsData:

  def __init__(self, email, password):
    self.gd_client = gdata.spreadsheet.service.SpreadsheetsService()
    self.gd_client.email = email
    self.gd_client.password = password
    self.gd_client.source = 'Spreadsheets GData Sample'
    self.gd_client.ProgrammaticLogin()
    self.curr_key = ''
    self.curr_wksht_id = ''
    self.list_feed = None
    self.contacts = []
    self.spreadsheet = 'Contacts'
    self.worksheet = 'Phone'

  def Run(self):
    self._ProcessSpreadsheet()
    self._ProcessWorksheet()
    self._ListGetAction()

  def GetContacts(self):
     return self.contacts

  def _ProcessSpreadsheet(self):
    # Get the list of spreadsheets
    feed = self.gd_client.GetSpreadsheetsFeed()
    for i, entry in enumerate(feed.entry):
	if (entry.title.text == self.spreadsheet):
		id_parts = feed.entry[i].id.text.split('/')
    		self.curr_key = id_parts[len(id_parts) - 1]
  
  def _ProcessWorksheet(self):
    # Get the list of worksheets
    feed = self.gd_client.GetWorksheetsFeed(self.curr_key)
    for i, entry in enumerate(feed.entry):
	if(entry.title.text == self.worksheet):
		id_parts = feed.entry[i].id.text.split('/')
    		self.curr_wksht_id = id_parts[len(id_parts) - 1]
        
  def _ListGetAction(self):
    # Get the list feed
    self.list_feed = self.gd_client.GetListFeed(self.curr_key, self.curr_wksht_id)
    self._ProcessFeed(self.list_feed) 

  def _StringToDictionary(self, row_data):
    dict = {}
    for param in row_data.split():
      temp = param.split('=')
      dict[temp[0]] = temp[1]
    return dict

  def _ProcessFeed(self, feed):
    for i, entry in enumerate(feed.entry):
      if isinstance(feed, gdata.spreadsheet.SpreadsheetsListFeed):
        x = ContactData()
        x.index = i
	x.firstname = entry.custom['firstname'].text
	x.lastname = entry.custom['lastname'].text
	x.phonenumber = entry.custom['phonenumber'].text
	x.email = entry.custom['email'].text
	self.contacts.append(x)
	
        
  def _InvalidCommandError(self, input):
    print 'Invalid input: %s\n' % (input)


class ContactsSpreadsheetXML(webapp.RequestHandler):
  def get(self):
    
    username = self.request.get("un")
    password = self.request.get("pw")
    prog = GetContactsData(username, password)
    prog.Run()
    contacts = prog.GetContacts()

    self.response.headers['content-type'] = 'text/xml'
    str = u"""<?xml version="1.0" encoding="utf-8"?><shobyscontacts>"""
    for entry in contacts:
        str += entry.to_xml()
    str += "</shobyscontacts>"
    self.response.out.write(str)
