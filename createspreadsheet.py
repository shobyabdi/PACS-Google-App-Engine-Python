import cgi

try:
  from xml.etree import ElementTree
except ImportError:
  from elementtree import ElementTree
import gdata.spreadsheet.service
import gdata.service
import gdata
import atom.service
import gdata.alt.appengine
import gdata.spreadsheet
import gdata.docs.service
import gdata.docs
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

class CreateSpreadsheetRun:

  def __init__(self, email, password):
    self.gd_client = gdata.docs.service.DocsService()
    self.gd_client.email = email
    self.gd_client.password = password
    self.gd_client.source = 'Spreadsheets GData Sample'
    self.gd_client.ProgrammaticLogin()
    self.list_feed = None
    self.spreadsheet = 'Contacts'
    self.worksheet = 'Phone'

  def Run(self):
    self._GenerateSpreadsheet()
    # self._FindSpreadsheet()
    # self._ProcessWorksheet()
    return result


  def _GenerateSpreadsheet(self):
    # Get the list of spreadsheets
    feed = self.gd_client.GetDocumentListFeed()
    # new_entry = gdata.GDataEntry()
    # new_entry.title = gdata.atom.Title(text=self.spreadsheet)
    # category = gdata.atom.Category(scheme=gdata.docs.service.DATA_KIND_SCHEME, term=gdata.docs.service.SPREADSHEET_KIND_TERM)
    # new_entry.category.append(category)
    # created_entry = self.gd_client.Post(new_entry, '/feeds/documents/private/full')
    ms = gdata.MediaSource(file_path='Contacts.xls', content_type=gdata.docs.service.SUPPORTED_FILETYPES['XLS'])
    entry = self.gd_client.UploadSpreadsheet(ms, self.spreadsheet)
    print 'Spreadsheet now accessible online at:', entry.GetAlternateLink().href

  def _FindSpreadsheet(self):
    # Get the list of spreadsheets
    self.gd_client = gdata.spreadsheet.service.SpreadsheetsService()
    self.gd_client.ProgrammaticLogin()
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
		entry.row = 500
		entry.col = 20
		self.gd_client.UpdateWorksheet(entry);
		

       
  def _InvalidCommandError(self, input):
    print 'Invalid input: %s\n' % (input)


class CreateSpreadsheet(webapp.RequestHandler):
  def get(self):
    
    username = self.request.get("un")
    password = self.request.get("pw")
    prog = CreateSpreadsheetRun(username, password)
    result = prog.Run()
    self.response.out.write(result);
