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

class UpdateContactData:

  def __init__(self, email, password, contact):
    self.gd_client = gdata.spreadsheet.service.SpreadsheetsService()
    self.gd_client.email = email
    self.gd_client.password = password
    self.gd_client.source = 'Spreadsheets GData Sample'
    self.gd_client.ProgrammaticLogin()
    self.curr_key = ''
    self.curr_wksht_id = ''
    self.list_feed = None
    self.spreadsheet = 'Contacts'
    self.worksheet = 'Phone'
    self.singlecontact = contact

  def Run(self):
    self._ProcessSpreadsheet()
    self._ProcessWorksheet()
    result = self._ListUpdateAction()
    return result


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
        
  def _ListUpdateAction(self):
    row_data = 'firstname='+self.singlecontact.firstname
    row_data += ' lastname='+self.singlecontact.lastname
    row_data += ' phonenumber='+self.singlecontact.phonenumber
    row_data += ' email='+self.singlecontact.email
    self.list_feed = self.gd_client.GetListFeed(self.curr_key, self.curr_wksht_id)
    entry = self.gd_client.UpdateRow(self.list_feed.entry[string.atoi(self.singlecontact.index)], self._StringToDictionary(row_data))
    if isinstance(entry, gdata.spreadsheet.SpreadsheetsList):
      print 'Updated!'



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
	x.firstname = entry.custom['firstname'].text
	x.lastname = entry.custom['lastname'].text
	x.phonenumber = entry.custom['phonenumber'].text
	x.email = entry.custom['email'].text
	self.contacts.append(x)
	
        
  def _InvalidCommandError(self, input):
    print 'Invalid input: %s\n' % (input)


class UpdateContact(webapp.RequestHandler):
  def get(self):
    
    username = self.request.get("un")
    password = self.request.get("pw")

    x = ContactData()
    x.index = self.request.get("index")
    x.firstname = self.request.get("first")
    x.lastname = self.request.get("last")
    x.phonenumber = self.request.get("phone")
    x.email = self.request.get("email")  

    prog = UpdateContactData(username, password, x)
    result = prog.Run()
    self.response.out.write(result);
