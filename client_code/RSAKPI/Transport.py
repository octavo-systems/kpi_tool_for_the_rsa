import anvil.server
# This is a module.
# You can define variables and functions here, and use them from any form. For example, in a top-level form:
#
#    from . import Module1
#
#    Module1.say_hello()
#
@anvil.server.portable_class
class Cargo():

  volume=0 
  service_requests=0
  system_logs=0
  dvcsd_contacts=0
  tickets_less_than_ten_days=0
  tickets_more_than_sixty=0
  failedresponse = {}

  def __init__(self):
    pass