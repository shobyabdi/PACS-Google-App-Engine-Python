#!/usr/bin/python
#
# Copyright (C) 2008 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""ContactsService extends the GDataService to streamline Google Contacts operations.

  ContactsService: Provides methods to query feeds and manipulate items. Extends 
                GDataService.

  DictionaryToParamList: Function which converts a dictionary into a list of 
                         URL arguments (represented as strings). This is a 
                         utility function used in CRUD operations.
"""

__author__ = 'dbrattli (Dag Brattli)'


import gdata
import atom.service
import gdata.service
import gdata.calendar
import atom

DEFAULT_BATCH_URL = ('http://www.google.com/m8/feeds/contacts/default/full'
                     '/batch')

class Error(Exception):
  pass

class RequestError(Error):
  pass

class ContactsService(gdata.service.GDataService):
  """Client for the Google Contats service."""

  def __init__(self, email=None, password=None, source=None, 
               server='www.google.com', 
               additional_headers=None):
    gdata.service.GDataService.__init__(self, email=email, password=password,
                                        service='cp', source=source, 
                                        server=server, 
                                        additional_headers=additional_headers)

  def GetContactsFeed(self, 
      uri='http://www.google.com/m8/feeds/contacts/default/full'):
    return self.Get(uri, converter=gdata.contacts.ContactsFeedFromString)

  def GetContact(self, uri):
    return self.Get(uri, converter=gdata.contacts.ContactEntryFromString)

  def CreateContact(self, new_contact, 
      insert_uri='/m8/feeds/contacts/default/full', url_params=None, 
      escape_params=True):
    """Adds an new contact to Google Contacts.

    Args: 
      new_contact: atom.Entry or subclass A new contact which is to be added to
                Google Contacts.
      insert_uri: the URL to post new contacts to the feed
      url_params: dict (optional) Additional URL parameters to be included
                  in the insertion request. 
      escape_params: boolean (optional) If true, the url_parameters will be
                     escaped before they are included in the request.

    Returns:
      On successful insert,  an entry containing the contact created
      On failure, a RequestError is raised of the form:
        {'status': HTTP status code from server, 
         'reason': HTTP reason from the server, 
         'body': HTTP body of the server's response}
    """
    return self.Post(new_contact, insert_uri, url_params=url_params,
        escape_params=escape_params,
        converter=gdata.contacts.ContactEntryFromString)

      
  def UpdateContact(self, edit_uri, updated_contact, url_params=None, 
                    escape_params=True):
    """Updates an existing contact.

    Args:
      edit_uri: string The edit link URI for the element being updated
      updated_contact: string, atom.Entry or subclass containing
                    the Atom Entry which will replace the contact which is 
                    stored at the edit_url 
      url_params: dict (optional) Additional URL parameters to be included
                  in the update request.
      escape_params: boolean (optional) If true, the url_parameters will be
                     escaped before they are included in the request.

    Returns:
      On successful update,  a httplib.HTTPResponse containing the server's
        response to the PUT request.
      On failure, a RequestError is raised of the form:
        {'status': HTTP status code from server, 
         'reason': HTTP reason from the server, 
         'body': HTTP body of the server's response}
    """
    url_prefix = 'http://%s/' % self.server
    if edit_uri.startswith(url_prefix):
      edit_uri = edit_uri[len(url_prefix):]
    return self.Put(updated_contact, '/%s' % edit_uri,
                    url_params=url_params, 
                    escape_params=escape_params, 
                    converter=gdata.contacts.ContactEntryFromString)

  def DeleteContact(self, edit_uri, extra_headers=None, 
      url_params=None, escape_params=True):
    """Removes an contact with the specified ID from Google Contacts.

    Args:
      edit_uri: string The edit URL of the entry to be deleted. Example:
               'http://www.google.com/m8/feeds/contacts/default/full/xxx/yyy'
      url_params: dict (optional) Additional URL parameters to be included
                  in the deletion request.
      escape_params: boolean (optional) If true, the url_parameters will be
                     escaped before they are included in the request.

    Returns:
      On successful delete,  a httplib.HTTPResponse containing the server's
        response to the DELETE request.
      On failure, a RequestError is raised of the form:
        {'status': HTTP status code from server, 
         'reason': HTTP reason from the server, 
         'body': HTTP body of the server's response}
    """
    url_prefix = 'http://%s/' % self.server
    if edit_uri.startswith(url_prefix):
      edit_uri = edit_uri[len(url_prefix):]
    return self.Delete('/%s' % edit_uri,
                       url_params=url_params, escape_params=escape_params)

  def GetGroupsFeed(self,
      uri='http://www.google.com/m8/feeds/groups/default/full'):
    return self.Get(uri, converter=gdata.contacts.GroupsFeedFromString)

  def CreateGroup(self, new_group, 
      insert_uri='/m8/feeds/groups/default/full', url_params=None, 
      escape_params=True):
    return self.Post(new_group, insert_uri, url_params=url_params,
        escape_params=escape_params,
        converter=gdata.contacts.GroupEntryFromString)

  def UpdateGroup(self, edit_uri, updated_group, url_params=None, 
                  escape_params=True):
    url_prefix = 'http://%s/' % self.server
    if edit_uri.startswith(url_prefix):
      edit_uri = edit_uri[len(url_prefix):]
    return self.Put(updated_group, '/%s' % edit_uri,
                    url_params=url_params, 
                    escape_params=escape_params, 
                    converter=gdata.contacts.GroupEntryFromString)

  def DeleteGroup(self, edit_uri, extra_headers=None, 
      url_params=None, escape_params=True):
    url_prefix = 'http://%s/' % self.server
    if edit_uri.startswith(url_prefix):
      edit_uri = edit_uri[len(url_prefix):]
    return self.Delete('/%s' % edit_uri,
                       url_params=url_params, escape_params=escape_params)

  def ChangePhoto(self, media, contact_entry_or_url, content_type=None, 
      content_length=None):
    """Change the photo for the contact by uploading a new photo.

    Performs a PUT against the photo edit URL to send the binary data for the
    photo.

    Args:
      media: filename, file-like-object, or a gdata.MediaSource object to send.
      contact_entry_or_url: ContactEntry or str If it is a ContactEntry, this
                            method will search for an edit photo link URL and
                            perform a PUT to the URL.
      content_type: str (optional) the mime type for the photo data. This is
                    necessary if media is a file or file name, but if media
                    is a MediaSource object then the media object can contain
                    the mime type. If media_type is set, it will override the
                    mime type in the media object.
      content_length: int or str (optional) Specifying the content length is
                      only required if media is a file-like object. If media
                      is a filename, the length is determined using 
                      os.path.getsize. If media is a MediaSource object, it is
                      assumed that it already contains the content length.
    """
    if isinstance(contact_entry_or_url, gdata.contacts.ContactEntry):
      url = contact_entry_or_url.GetPhotoEditLink().href
    else:
      url = contact_entry_or_url
    if isinstance(media, gdata.MediaSource):
      payload = media
    # If the media object is a file-like object, then use it as the file
    # handle in the in the MediaSource.
    elif hasattr(media, 'read'):
      payload = gdata.MediaSource(file_handle=media, 
          content_type=content_type, content_length=content_length)
    # Assume that the media object is a file name.
    else:
      payload = gdata.MediaSource(content_type=content_type, 
          content_length=content_length, file_path=media)
    return self.Put(payload, url)

  def GetPhoto(self, contact_entry_or_url):
    """Retrives the binary data for the contact's profile photo as a string.
    
    Args:
      contact_entry_or_url: a gdata.contacts.ContactEntry objecr or a string
         containing the photo link's URL. If the contact entry does not 
         contain a photo link, the image will not be fetched and this method
         will return None.
    """
    # TODO: add the ability to write out the binary image data to a file, 
    # reading and writing a chunk at a time to avoid potentially using up 
    # large amounts of memory.
    url = None
    if isinstance(contact_entry_or_url, gdata.contacts.ContactEntry):
      photo_link = contact_entry_or_url.GetPhotoLink()
      if photo_link:
        url = photo_link.href
    else:
      url = contact_entry_or_url
    if url:
      return self.Get(url, converter=str)
    else:
      return None

  def DeletePhoto(self, contact_entry_or_url):
    url = None
    if isinstance(contact_entry_or_url, gdata.contacts.ContactEntry):
      url = contact_entry_or_url.GetPhotoEditLink().href
    else:
      url = contact_entry_or_url
    if url:
      self.Delete(url)

  def ExecuteBatch(self, batch_feed, url,
                   converter=gdata.contacts.ContactsFeedFromString):
    """Sends a batch request feed to the server.
    
    Args:
      batch_feed: gdata.contacts.ContactFeed A feed containing batch
          request entries. Each entry contains the operation to be performed
          on the data contained in the entry. For example an entry with an
          operation type of insert will be used as if the individual entry
          had been inserted.
      url: str The batch URL to which these operations should be applied.
      converter: Function (optional) The function used to convert the server's
          response to an object. The default value is ContactsFeedFromString.
    
    Returns:
      The results of the batch request's execution on the server. If the
      default converter is used, this is stored in a ContactsFeed.
    """
    return self.Post(batch_feed, url, converter=converter)

class ContactsQuery(gdata.service.Query):

  def __init__(self, feed=None, text_query=None, params=None,
      categories=None, group=None):
    self.feed = feed or '/m8/feeds/contacts/default/full'
    if group:
      self._SetGroup(group)
    gdata.service.Query.__init__(self, feed=self.feed, text_query=text_query,
        params=params, categories=categories)

  def _GetGroup(self):
    if 'group' in self:
      return self['group']
    else:
      return None

  def _SetGroup(self, group_id):
    self['group'] = group_id

  group = property(_GetGroup, _SetGroup, 
      doc='The group query parameter to find only contacts in this group')

class GroupsQuery(gdata.service.Query):
  
  def __init__(self, feed=None, text_query=None, params=None,
      categories=None):
    self.feed = feed or '/m8/feeds/groups/default/full'
    gdata.service.Query.__init__(self, feed=self.feed, text_query=text_query,
        params=params, categories=categories)
