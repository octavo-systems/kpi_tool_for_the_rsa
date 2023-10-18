import anvil.server
# This is a module.
# You can define variables and functions here, and use them from any form. For example, in a top-level form:
#
#    from . import Module1
#
#    Module1.say_hello()
#

@anvil.server.portable_class
class KPITRANS():
  
  #Parameters in.
  month = 0
  year = 0

  #Parameters out
  critical = 0
  high = 0
  normal = 0
  low = 0
  trivial = 0
  #Dict
  failedresponse = []
  
  service_requests = 0
  system_logs = 0
  dvcsd_contacts = 0
  tickets_less_than_ten_days = 0
  tickets_more_than_sixty = 0

  open = 0
  reopened = 0
  followup = 0
  resolved = 0
  closed = 0
  total= 0
  percentage_incidents_in_sla = 0

  def __init__(self):
    pass
