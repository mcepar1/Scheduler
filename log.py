"""
This class intercepts and discards log messages, if no log was given to the
the logging class.
"""
class DummyLog:
  def send_message(self, *args, **kwargs):
    pass
