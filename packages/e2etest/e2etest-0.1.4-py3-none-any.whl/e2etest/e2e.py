from requests_html import HTMLSession

class E2E(object):
   """E2E Test for Web Including Javascript"""
   def __init__(self, url):
      self.url = url
      session = HTMLSession()
      r = session.get(self.url)
      self.r = r
   def exists(self, tag):
      if self.r.html.find(tag):
         return True
      else:
         return False
   def get_text(self, tag):
      if not self.r.html.find(tag):
         return None
      return [t.text for t in self.r.html.find(tag)]
