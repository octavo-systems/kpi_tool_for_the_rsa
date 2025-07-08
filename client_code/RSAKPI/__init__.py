import anvil.server
from .. import Transport
from ._anvil_designer import RSAKPITemplate
from anvil import is_server_side
if not is_server_side():
    from anvil.js.window import navigator




class RSAKPI(RSAKPITemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.

    # Any code you write here will run before the form opens.
    self.month.items = [("January", 1),("February",2),("March",3),("April",4),("May",5),("June",6),("July",7),("August",8),("September",9),("October",10),("November",11),("December",12)]
    self.year.items = [("2023", 2023),("2024",2024),("2025",2025),("2026",2026)]

  def exit_btn_click(self, **event_args):
    """This method is called when the button is clicked"""
    return

  def sifter_btn_click(self, **event_args):
    """This method is called when the sifter button is clicked"""
  
    critical = Transport.Cargo()
    high = Transport.Cargo()
    normal = Transport.Cargo()
    low = Transport.Cargo()
    trivial = Transport.Cargo()
    days = Transport.Cargo()
    
    critical = anvil.server.call('GetRSASIFTER_MonthKPI',year = self.year.selected_value,month = self.month.selected_value, priority = 1 )
    self.critical.text = critical.volume
    
    high = anvil.server.call('GetRSASIFTER_MonthKPI',year = self.year.selected_value,month = self.month.selected_value, priority = 2 ) 
    self.high.text  = high.volume
    
    normal = anvil.server.call('GetRSASIFTER_MonthKPI',year = self.year.selected_value,month = self.month.selected_value, priority = 3 )   
    self.normal.text = normal.volume
    
    low = anvil.server.call('GetRSASIFTER_MonthKPI',year = self.year.selected_value,month = self.month.selected_value, priority = 4 )   
    self.low.text = low.volume
    
    trivial = anvil.server.call('GetRSASIFTER_MonthKPI',year = self.year.selected_value,month = self.month.selected_value, priority = 5 )   
    self.trivial.text = trivial.volume
    
    self.total_incidents.text = critical.volume + high.volume+normal.volume+low.volume+trivial.volume
    self.dvcsd_contacts.text = critical.dvcsd_contacts + high.dvcsd_contacts+normal.dvcsd_contacts+low.dvcsd_contacts+trivial.dvcsd_contacts

    self.sifterrows.items = critical.failedresponse+high.failedresponse+normal.failedresponse+low.failedresponse+trivial.failedresponse

    if len(self.sifterrows.items) == 0:
      self.failed_response_list.text =self.failed_response_list.text + " (None this month)"
    # 2
    if self.total_incidents.text != 0: 
      self.percentage_incidents_in_sla.text = (1 - (len(self.sifterrows.items) / self.total_incidents.text)) * 100
    else:
      self.percentage_incidents_in_sla.text = 100      

    # 1.1    
    self.open.text = anvil.server.call('GetRSASIFTER_status',status=137089)
    self.reopened.text = anvil.server.call('GetRSASIFTER_status',status=137090)
    self.followup.text = anvil.server.call('GetRSASIFTER_status',status=177215)
    self.resolved.text = anvil.server.call('GetRSASIFTER_status',status=137091)
    self.closed.text = anvil.server.call('GetRSASIFTER_status',status=137092)
    self.total.text = self.open.text +self.reopened.text+self.followup.text+self.resolved.text+self.closed.text

    # 4 less than 10 days
    days = anvil.server.call('GetRSASIFTER_FirstPage', sort='d', numdays = 10)
    self.tickets_less_than_ten_days.text = days.tickets_less_than_ten_days
    # 6 service requests
    self.service_requests.text = anvil.server.call('GetRSASIFTER_ByCategory',self.year.selected_value,month = self.month.selected_value,category = 'Service Request' )
    # 8 Number of SR aged tickets 60 day - Total Open over sixty days.
    days= anvil.server.call('GetRSASIFTER_FirstPage', sort='a', numdays = 60)
    self.tickets_more_than_sixty.text = days.tickets_more_than_sixty
    # 9 Number of issues identified from system logs
    self.system_logs.text = anvil.server.call('GetRSASIFTER_ByTitlePart',self.year.selected_value,month = self.month.selected_value,titlepart = 'application error')
    # 10 Number of alerts/communications from DVCSD actioned
    self.dvcsd_contacts.text = anvil.server.call('GetRSASIFTER_ByTitlePart',self.year.selected_value,month = self.month.selected_value,titlepart = 'dvcsd')
    
  
  def save_btn_click(self, **event_args):
    """This method is called when the save button is clicked"""
    #No file interaction from the browser....
    #with open('c:\\temp\\kpi_report_'+str(self.month.selected_value)+'_'+str(self.year.selected_value)+'.txt', 'a') as report:
    report: str = ''
    print ('Starting Report section')
    HC_NEWLINE = '\n'
    HC_TAB = '\t'
    HC_SPACE= ' '

    report=report+ 'RSA KPI Report for '+ str(self.month.selected_value)+HC_SPACE+str(self.year.selected_value) +HC_NEWLINE
    report=report+ HC_NEWLINE 
    report=report+ 'Incident Management'+HC_NEWLINE 
    report=report+ HC_NEWLINE 
    report=report+ '1. Number of Incidents in month'+HC_NEWLINE 
    report=report+ HC_NEWLINE 
    report=report+ 'Critical  ' + HC_TAB + str(self.critical.text) + HC_NEWLINE
    report=report+ 'High  '  + HC_TAB+HC_TAB + str(self.high.text) + HC_NEWLINE
    report=report+ 'Normal  ' + HC_TAB + str(self.normal.text)+ HC_NEWLINE
    report=report+ 'Low  '  + HC_TAB+HC_TAB + str(self.low.text)+ HC_NEWLINE
    report=report+ 'Trivial  ' + HC_TAB+HC_TAB + str(self.trivial.text)+ HC_NEWLINE

    report=report+ HC_NEWLINE +'Failed SLAs on SIFTER response time for: ' + HC_NEWLINE

    if self.sifterrows.items is None or len(self.sifterrows.items) == 0:
        report=report+ HC_NEWLINE +'None.' + HC_NEWLINE
    else:
        report=report+ HC_NEWLINE 
        for kpifailure in self.failedresponse:
            report=report+ 'SIFTER  ' + HC_TAB + kpifailure + HC_NEWLINE 

    report=report+ HC_NEWLINE 
    report=report+ '1.1 SIFTER Volumes'+HC_NEWLINE 

    report=report+ HC_NEWLINE 
    report=report+ 'Open' + HC_TAB + HC_TAB+ str(self.open.text) + HC_NEWLINE
    report=report+ 'Reopened'  + HC_TAB + str(self.reopened.text) + HC_NEWLINE
    report=report+ 'Followup' + HC_TAB + str(self.followup.text)+ HC_NEWLINE
    report=report+ 'Resolved'  + HC_TAB + str(self.resolved.text)+ HC_NEWLINE
    report=report+ 'Closed' + HC_TAB +HC_TAB+ str(self.closed.text)+ HC_NEWLINE
    report=report+ 'Total' + HC_TAB+HC_TAB +HC_TAB+ str(self.total.text)+ HC_NEWLINE
    report=report+ HC_NEWLINE 
    report=report+ '2. Percentage of incidents that met service levels (where no dependance on DVCSD)' +HC_NEWLINE

    report=report+ HC_NEWLINE 
    report=report+ 'Percentage  ' + HC_TAB +  str(self.percentage_incidents_in_sla.text) + '%' +HC_NEWLINE 
    report=report+ HC_NEWLINE 
    report=report+ '3. First contact resolution rate' +HC_NEWLINE
    report=report+ HC_NEWLINE 
    report=report+ 'Not Applicable  All incidents raised through SIFTER'+HC_NEWLINE
    report=report+ HC_NEWLINE 
    report=report+ '4. Number of incident backlog/aged tickets less than 10 days old (where no dependency on DVCSD)' +HC_NEWLINE
    report=report+ HC_NEWLINE 
    report=report+ 'Tickets  ' + str(self.tickets_less_than_ten_days.text)+HC_NEWLINE
    report=report+ HC_NEWLINE 
    report=report+ '5. Unplanned Outages split into DVCSD and Vendor issues' +HC_NEWLINE
    report=report+ HC_NEWLINE 
    report=report+ 'Not Applicable, Production is managed by DVCSD'+HC_NEWLINE
    report=report+ HC_NEWLINE 
    report=report+ '6. Number of Service requests' +HC_NEWLINE
    report=report+ HC_NEWLINE 
    report=report+ 'Tickets  ' + str(self.service_requests.text)+HC_NEWLINE
    report=report+ HC_NEWLINE 
    report=report+ '7. Percentage of service requests that met service levels.' +HC_NEWLINE
    report=report+ HC_NEWLINE 
    report=report+ 'Not Applicable, There is no SLA for service requests'+HC_NEWLINE
    report=report+ HC_NEWLINE 
    report=report+ '8. Number of SR aged tickets 60 days (where no dependency on DVCSD)' +HC_NEWLINE
    report=report+ HC_NEWLINE 
    report=report+ 'Tickets  ' + str(self.tickets_more_than_sixty.text)+HC_NEWLINE
    report=report+ HC_NEWLINE 
    report=report+ '9. Number of issues identified from system logs' +HC_NEWLINE
    report=report+ HC_NEWLINE 
    report=report+ 'Tickets  ' + str(self.system_logs.text)+HC_NEWLINE
    report=report+ HC_NEWLINE 
    report=report+ '10. Number of alerts/communications from DVCSD actioned' +HC_NEWLINE
    report=report+ HC_NEWLINE 
    report=report+ 'Tickets  ' + str(self.dvcsd_contacts.text)+HC_NEWLINE
    report=report+ HC_NEWLINE 
    report=report+ '11. System up time clarify what is DVCSD and Vendor related on downtime.' +HC_NEWLINE
    report=report+ HC_NEWLINE
    report=report+ 'Not Applicable' +HC_NEWLINE              

    report=report+ HC_NEWLINE 
    report=report+ 'Release Management'+HC_NEWLINE 
    report=report+ HC_NEWLINE             
    report=report+ '1. Hypercare Exit on deployments major releases - Exit of hypercare after 1 month dependent no P1 or P2 raised by customer/ business in the last 7 days.' +HC_NEWLINE
    report=report+ HC_NEWLINE 
    report=report+ 'N/A' +     HC_NEWLINE 
    report=report+ '2. Minor releases will have related hypercare of 2 weeks - no P1 or P2 raised by customer/business in the last 4 days to close that hypercare period.' +HC_NEWLINE  
    report=report+ HC_NEWLINE 
    report=report+ 'N/A' + HC_NEWLINE   

    print ('Printing report:')
    print (report)
    print ('Report copied to clipboard.')
    navigator.clipboard.writeText(report)

















