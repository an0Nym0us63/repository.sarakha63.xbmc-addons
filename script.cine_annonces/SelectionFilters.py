from datetime import datetime
import time
class SelectionFilters(object):
  _myfilters = {}
 
  def __init__(self):
           
    # Year - filter by years
    yeardict = {}
    yeardict["enabled"] = False
    yeardict["testname"] = "TestYear"
    self._myfilters["year"] = yeardict
    # Year - filter by download date
    lastdict = {}
    lastdict["enabled"] = False
    lastdict["testname"] = "TestLast"
    self._myfilters["last"] = lastdict
    # Duree - filter by runtime
    rundict = {}
    rundict["enabled"] = False
    rundict["testname"] = "TestRuntime"
    self._myfilters["runtime"] = rundict
    
    # Genre - filter by movie genre
    genredict = {}
    genredict["enabled"] = False
    genredict["testname"] = "TestGenre"
    self._myfilters["genre"] = genredict
    
    # Unwatched - filter by unwatched movies
    unwatcheddict = {}
    unwatcheddict["enabled"] = False
    unwatcheddict["testname"] = "TestUnwatched"
    self._myfilters["unwatched"] = unwatcheddict
    
    #Disney - filter by Disney
    disneydict = {}
    disneydict["enabled"] = False
    disneydict["testname"] = "Testdisney"
    self._myfilters["disney"] = disneydict
    
    
    # _mpaa = False
    # _genre = False
    # _year = False
    # _watched = False

# Standard functions    
    
  def HasActiveFilter(self):
    a = 0
    for filter in self._myfilters:
      if self._myfilters[filter]["enabled"]:
        a += 1
    
    if a > 0:
      return True
    else:
      return False
      
  def MeetsCriteria(self, movie):
    meets = True
    
    for filter in self._myfilters:
      if self._myfilters[filter]["enabled"]:
        test = getattr(self, self._myfilters[filter]["testname"])
        if not test(movie):
          meets = False
          break
          
    return meets
        
  def SetFilter(self, filterName, enabled, **kwargs):
    success = False
    
    if filterName in self._myfilters:
      self._myfilters[filterName]["enabled"] = enabled
      if kwargs and enabled:
        self._myfilters[filterName]["params"] = kwargs
    success = True

    return success

  def GetFilter(self, filterName):
    if filterName in self._myfilters:
      return self._myfilters[filterName]    
    else:
      return False
      
  def FilterEnabled(self, filterName):
    if filterName in self._myfilters:
      return self._myfilters[filterName]["enabled"]
    else:
      return False
  
  def __str__(self):
    return str(self._myfilters)

# Specific filter tests - named as per _init_ (above).

  def TestYear(self, movie):
    success = False
    if int(movie["year"]) >= self._myfilters["year"]["params"]["year"]:
      success = True
    return success
  def TestLast(self, movie):
    start_date = datetime.fromtimestamp(time.mktime(time.strptime(movie["dateadded"], "%Y-%m-%d %H:%M:%S")))
    end_date = datetime.now()
    success = False
    if int(abs((end_date-start_date).days)) <= self._myfilters["last"]["params"]["last"]:
      success = True
    return success
  def TestRuntime(self, movie):
    success = False
    if int(movie["runtime"]) <= self._myfilters["runtime"]["params"]["runtime"]:
      success = True
    return success
  def TestGenre(self, movie):
    success = False
    if self._myfilters["genre"]["params"]["genre"] != "3D":
        if self._myfilters["genre"]["params"]["genre"] in movie["genre"]:
            success = True
    else:
        if "3DBD" in movie["file"]:
            success = True
    return success
  def TestUnwatched(self, movie):
    success = False
    if movie["playcount"] == 0:
      success = True
    return success
  def Testdisney(self, movie):
    success = False
    if self._myfilters["disney"]["params"]["disney"] != movie["set"]:
      success = True
    return success
  
