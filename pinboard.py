#!/usr/bin/env python
"""Python-Pinboard

Python module for access to pinboard <http://pinboard.com/> via
its web interface
"""

__version__ = "1.0.0"
__license__ = "BSD"
__copyright__ = "Copyright 2011, Pratik Dam"
__author__ = "Pratik Dam <http://pratikdam.wordpress.com/>"

_debug = 1

# The user agent string sent to pinboard.com when making requests. If you are
# using this module in your own application, you should probably change this.
USER_AGENT = "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; InfoPath.2; .NET CLR 2.0.50727; .NET CLR 3.0.04506.648; .NET CLR 3.5.21022; .NET CLR 1.1.4322)2011-10-16 20:22:33"



import time
import string
import sys
import getopt
import urllib
import urllib2
import logging
import sys
import re
import json
from ConfigParser import ConfigParser
import time
import random
## added to handle gzip compression from server
import StringIO
import gzip
import os
import mechanize

from xml.dom import minidom
import httplib, mimetypes
import logging
import urllib2
FORMAT = '%(asctime)-15s  %(message)s'
logging.basicConfig(format=FORMAT)


class Spintax:
  def __init__(self):
        pass

  def spin(self , cont ):
      spun_string =  cont
      while True:
            spun_string, n = re.subn('{([^{}]*)}',
                           lambda m: random.choice(m.group(1).split("|")),
                           spun_string)
            if n == 0:
                break

      return spun_string.strip()


def retry(ExceptionToCheck, tries=4, delay=3, backoff=2, logger=None):
    """Retry calling the decorated function using an exponential backoff.

    http://www.saltycrane.com/blog/2009/11/trying-out-retry-decorator-python/
    original from: http://wiki.python.org/moin/PythonDecoratorLibrary#Retry

    :param ExceptionToCheck: the exception to check. may be a tuple of
        excpetions to check
    :type ExceptionToCheck: Exception or tuple
    :param tries: number of times to try (not retry) before giving up
    :type tries: int
    :param delay: initial delay between retries in seconds
    :type delay: int
    :param backoff: backoff multiplier e.g. value of 2 will double the delay
        each retry
    :type backoff: int
    :param logger: logger to use. If None, print
    :type logger: logging.Logger instance
    """
    def deco_retry(f):
        def f_retry(*args, **kwargs):
            mtries, mdelay = tries, delay
            try_one_last_time = True
            while mtries > 1:
                try:
                    return f(*args, **kwargs)
                    try_one_last_time = False
                    break
                except ExceptionToCheck, e:
                    msg = "%s, Retrying in %d seconds..." % (str(e), mdelay)
                    if logger:
                        logger.warning(msg)
                    else:
                        print msg
                    time.sleep(mdelay)
                    mtries -= 1
                    mdelay *= backoff
            if try_one_last_time:
                return f(*args, **kwargs)
            return
        return f_retry  # true decorator
    return deco_retry




import urllib, urllib2, cookielib
from mechanize import Browser, _http
#from BeautifulSoup import BeautifulSoup
# The URL of the Pinboard 
PINBOARD_URL = "https://pinterest.com/login"
PIN_USER = "lizoleson70@yahoo.com"
PIN_PASSWORD ="mark2242"
LOCATION_IMAGES = os.path.join(os.pardir, "images")


def aopen(username, password,refid):
    """Open a connection to a pinboard.com account"""
    return PinboardAccount(username, password,refid)

def aconnect(username, password,refid):
    """Open a connection to a pinboard.com account"""
    return open(username, password,refid)

class PinboardAccount(object):
    __allposts = 0
    __postschanged = 0

    # Time of last request so that the one second limit can be enforced.
    __lastrequest = None
    
    def __init__(self, username, password,refid):
            self.br = Browser()
            self.username=username
            self.password = password
            self.refid = refid
            self.br.set_handle_robots(False)
            
            # Browser options
            self.br.set_handle_equiv(True)
            self.br.set_handle_redirect(True)
            self.br.set_handle_referer(True)
            self.br.set_handle_robots(False)

            self.br.set_debug_http(True)
            self.br.set_debug_redirects(True)
            self.br.set_debug_responses(True)

            # Follows refresh 0 but not hangs on refresh > 0
            self.br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)

            self.br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]
            page = self.br.open(PINBOARD_URL)
            form = self.br.forms().next()  # the login form is unnamed...
            if _debug:
                print form.action        # prints form
            self.br.select_form(nr=0)
            self.br["email"]=username
            self.br["password"]=password
            resp  = self.br.submit()
            con = resp.read()
            matchExpr =  "csrfmiddlewaretoken' value='(.*[^']?)'"                 
            self.csrf=re.findall( matchExpr , con )[0]
            print "CSRF is %s "%self.csrf
            conn=self.br.open("http://pinterest.com/%s/"%refid).read()
                     
    @retry( Exception)
    def createaPin(self,  boardID , desc ,urlSite,  taglist): 
            print "Post data  is  %s  %s  %s  %s "%(boardID  , desc ,  urlSite , taglist)
            time.sleep(6)
            self.br.open("http://pinterest.com/%s/pins/"%self.refid)
            f=urllib.urlretrieve(urlSite)[0]
            postData = {'board': boardID,
                                         'details': desc   ,
                                         'link' : urlSite ,
                                         'img_url' : urlSite ,
                                         'tags' : taglist ,
                                         'replies' : '' ,
                                         'buyable' : '' ,
                                         'img' : open( f , "rb") , 
                                        'csrfmiddlewaretoken' : self.csrf}
            request = self.br.open("http://pinterest.com/pin/create/", urllib.urlencode(postData))
            content = json.loads(request.read()).get("url")
            pinID = string.replace( content , "/pin/" , "" ).replace("/" , "")
            return pinID

    def getAllBoardsForUser(self , refName):
            time.sleep(1)
            resp = self.br.open("http://pinterest.com/%s/"%refName)
            con = resp.read()
            jsonBoard="""var myboards =(.*?[^]]?)]"""
            m =  re.findAll( re.compile(jsonBoard), con )
            print  m
            content = json.loads(request.read()).get("url")
            pinID = string.replace( content , "/pin/" , "" ).replace("/" , "")
            return pinID
        

    def doAllGood(self ,userName , password   , comment, count , boardListStr):
        os.system("/Users/Mark/apache-jmeter-2.6/bin/jmeter.sh -JuserName=%s -Jpassword=%s -Jnthreads=%s   -JrefName=%s -JhostName=pinterest.com  -JtargetBoardList=%s -n  -t  doAllGood.jmx  " %(userName , password,   count , self.refid, boardListStr  ))
        #os.system("\"D:\\java\\apache-jmeter-2.6\\bin\\jmeter.bat\" -JuserName=%s -Jpassword=%s -Jnthreads=%s -JrefName=%s -JhostName=pinterest.com   -JtargetBoardList=%s -n  -t  doAllGood.jmx  " %(userName , password,   count , self.refid, boardListStr  ))
             
    def createBoard(self, csvFile):
          boardList = self.getBoardListForUser()
          print  boardList
          count  =  len([   x.strip()    for     x in   file(csvFile).readlines()  ])
          print count 
          os.system("\"D:\\java\\apache-jmeter-2.6\\bin\\jmeter.bat\" -JuserName=%s -Jpassword=%s -Jnthreads=%s -JrefName=%s -JhostName=pinterest.com  -n  -t  doCreateBoard.jmx  " %(self.username , self.password, count  ,self.refid  ))
    
    def getBoardListForUser(self ):
          urlBoard  =   self.br.open("http://pinterest.com/%s"%self.refid)
          #if re.compile(l.url).match("http://pinterest.com/%s/(.*?[^/]?)/"%self.refid)
          self.listBoards = [  l.text  for  l   in  self.br.links()  ]
          return  self.listBoards
          



      
class Usage(Exception):
    def __init__(self, msg):
        self.msg = msg
def main(argv=None):
    if argv is None:
        argv = sys.argv
   
    try:
        creator , creatorpass, creator_ref ,admirer, admirerpass ,admirer_ref   =  sys.argv[1] , sys.argv[2] ,sys.argv[3],sys.argv[4] , sys.argv[5] , sys.argv[6] 
    except:
        #creator , creatorpass, creator_ref ,admirer, admirerpass ,admirer_ref  = 'lizoleson70@yahoo.com' , 'mark2242' , 'lizole70' ,'izzylaizure@yahoo.com','mark2242' , 'izzylizz2'
        creator , creatorpass, creator_ref ,admirer, admirerpass ,admirer_ref  =  'donjameson77@yahoo.com' , 'mark2242' , 'donjameson77' ,'jessica.martin82@yahoo.com','mark2242' , 'jessicamartin82' 
        
    s = Spintax()
    f2 = open(os.path.abspath('pingen.csv') , 'w')
    f = open('content.txt' , 'r')
    f3 = open('complement.txt' , 'r')
    file_cont = f.read()
    complement_cont = f3.read()
    f.close()
    f3.close()
    print "Content  : %s" %file_cont
    print "Complement : %s" % complement_cont
    count=0
    p=PinboardAccount(creator , creatorpass, creator_ref)
                 

    listCreatorBoards =    [ ( x.strip().split(",")[0] ,  x.strip().split(",")[1] ,x.strip().split(",")[2] ,  x.strip().split(",")[3]  )  for  x  in  file('%s_blist.txt'%creator_ref).readlines() ]
    for (board , boardID , category, colabName ) in  listCreatorBoards :
            
            listImagesForBoard =   [ x.strip() for  x  in  file('%s_imglist.txt'%board).readlines() ]
            print  "Processing Board  %s  having   BoardID    %s    ImageList :%r"%( board  , boardID , listImagesForBoard)   
            for   img   in   listImagesForBoard :
                  count +=1
                  print  "Processing Board  %s  having   BoardID    %s    ImageList :%r"%( board  , boardID , img)
                  spun_string = s.spin(file_cont)
                  complement_str = s.spin(complement_cont)
                  imgURL =  "http://www.customizedwalls.com/%s"%(img)
                  print "Posting  image  %s  for  board %s" % ( imgURL , boardID)
                  pid =  p.createaPin( boardID , spun_string , imgURL , "Walls murals")
                  f2.write("%s,%s,%s\n"%(imgURL , pid, str(complement_str)))
                  print "Boards posted :%s   pinID : %s , Description:  %s   , URL   : %s " % ( boardID , pid ,  spun_string , imgURL )
                    
    f2.close() 
    lBoardsToRepin = ",".join([ x.strip() for  x  in  file('%s_blist.txt'%admirer_ref).readlines() ])
    print lBoardsToRepin
    print count
    p.doAllGood(admirer, admirerpass , admirer_ref ,count , lBoardsToRepin  )
      

      


if __name__ == "__main__":
    main()
