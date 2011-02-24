import datetime

from Scheduler.utils import translations

def translate(object):
  """
  Translates the object into the slovenian language.
    object: the object that will be translated
    return: an unicode string
  """
  
  if   isinstance(object, datetime.time):
    return translations.translate_time(object)
  elif isinstance(object, datetime.date):
    return translations.translate_date(object)
  elif isinstance(object, datetime.datetime):
    return translations.translate_datetime(object)
  elif isinstance(object, datetime.timedelta):
    return translations.translate_timedelata(object)
  elif isinstance(object, bool):
    return translations.translate_boolean(object)
  else:
    return translations.translate_string(object)