from ._anvil_designer import RSAKPITemplate
from anvil.js.window import navigator
import anvil.server
from Transport import Cargo
import sys


class RSAKPI(RSAKPITemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    print (sys.modules)

    # Any code you write here will run before the form opens.
    self.month.items = [("January", 1),("February",2),("March",3),("April",4),("May",5),("June",6),("July",7),("August",8),("September",9),("October",10),("November",11),("December",12)]
    self.year.items = [("2023", 2023),("2024",2024),("2025",2025)]

  def exit_btn_click(self, **event_args):
    """This method is called when the button is clicked"""
    return

  def sifter_btn_click(self, **event_args):
    """This method is called when the sifter button is clicked"""
  
    critical = Cargo()
    high = Cargo()
    mormal = Cargo()
    low = Cargo()
    trivial = Cargo()
    
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

    if self.total_incidents.text != 0: 
      self.percentage_incidents_in_sla.text = (1 - (len(self.sifterrows.items) / self.total_incidents.text)) * 100
    else:
      self.percentage_incidents_in_sla.text = 100      
    
    self.open.text = anvil.server.call('GetRSASIFTER_status',status=137089)
    self.reopened.text = anvil.server.call('GetRSASIFTER_status',status=137090)
    self.followup.text = anvil.server.call('GetRSASIFTER_status',status=177215)
    self.resolved.text = anvil.server.call('GetRSASIFTER_status',status=137091)
    self.closed.text = anvil.server.call('GetRSASIFTER_status',status=137092)
    self.total.text = self.open.text +self.reopened.text+self.followup.text+self.resolved.text+self.closed.text

  
  def save_btn_click(self, **event_args):
    """This method is called when the save button is clicked"""
    #No file interaction from the browser....
    #with open('c:\\temp\\kpi_report_'+str(self.month.selected_value)+'_'+str(self.year.selected_value)+'.txt', 'a') as report:
    HC_NEWLINE = '\n'
    HC_TAB = '\t'
    report = ''
    report.join( 'RSA KPI Report for '+'Test Month' +HC_NEWLINE)
    report.join( HC_NEWLINE )
    report.join( 'Incident Management'+HC_NEWLINE )
    report.join( HC_NEWLINE )
    report.join( '1. Number of Incidents in month'+HC_NEWLINE )

    report.join( HC_NEWLINE )
    report.join( 'Critical  ' + HC_TAB + str(self.critical.text) + HC_NEWLINE )
    report.join( 'High  '  + HC_TAB+HC_TAB + str(self.high.text) + HC_NEWLINE)	
    report.join( 'Normal  ' + HC_TAB + str(self.normal.text)+ HC_NEWLINE)
    report.join( 'Low  '  + HC_TAB+HC_TAB + str(self.low.text)+ HC_NEWLINE)
    report.join( 'Trivial  ' + HC_TAB + str(self.trivial.text)+ HC_NEWLINE)

    report.join( HC_NEWLINE +'Failed SLAs on SIFTER response time for: ' + HC_NEWLINE)
           
    if len(self.sifterrows.items) == 0:
        report.join( HC_NEWLINE +'None.' + HC_NEWLINE)
    else:
        report.join( HC_NEWLINE )
        for kpifailure in self.failedresponse:
            report.join( 'SIFTER  ' + HC_TAB + kpifailure + HC_NEWLINE )

    report.join( HC_NEWLINE )
    report.join( '1.1 SIFTER Volumes'+HC_NEWLINE )

    report.join( HC_NEWLINE )
    report.join( 'Open' + HC_TAB + HC_TAB+ str(self.open.text) + HC_NEWLINE )
    report.join( 'Reopened'  + HC_TAB + str(self.reopened.text) + HC_NEWLINE)    
    report.join( 'Followup' + HC_TAB + str(self.followup.text)+ HC_NEWLINE)
    report.join( 'Resolved'  + HC_TAB + str(self.resolved.text)+ HC_NEWLINE)
    report.join( 'Closed' + HC_TAB +HC_TAB+ str(self.closed.text)+ HC_NEWLINE)    
    report.join( 'Total' + HC_TAB +HC_TAB+ str(self.total.text)+ HC_NEWLINE)    

    report.join( HC_NEWLINE )
    report.join( '2. Percentage of incidents that met service levels (where no dependance on DVCSD)' +HC_NEWLINE)
    report.join( HC_NEWLINE )    
    report.join( 'Percentage  ' + HC_TAB +  str(self.percentage_incidents_in_sla.text) + '%' +HC_NEWLINE )
    report.join( HC_NEWLINE )
    report.join( '3. First contact resolution rate' +HC_NEWLINE)    
    report.join( HC_NEWLINE )
    report.join( 'Not Applicable  All incidents raised through SIFTER'+HC_NEWLINE)
    report.join( HC_NEWLINE )
    report.join( '4. Number of incident backlog/aged tickets less than 10 days old (where no dependency on DVCSD)' +HC_NEWLINE)    
    report.join( HC_NEWLINE )
    report.join( 'Tickets  ' + str(self.tickets_less_than_ten_days.text)+HC_NEWLINE)        
    report.join( HC_NEWLINE )
    report.join( '5. Unplanned Outages split into DVCSD and Vendor issues' +HC_NEWLINE)    
    report.join( HC_NEWLINE )
    report.join( 'Not Applicable, Production is managed by DVCSD'+HC_NEWLINE)
    report.join( HC_NEWLINE )
    report.join( '6. Number of Service requests' +HC_NEWLINE)
    report.join( HC_NEWLINE )    
    report.join( 'Tickets  ' + str(self.service_requests.text)+HC_NEWLINE)    
    report.join( HC_NEWLINE )
    report.join( '7. Percentage of service requests that met service levels.' +HC_NEWLINE)    
    report.join( HC_NEWLINE )
    report.join( 'Not Applicable, There is no SLA for service requests'+HC_NEWLINE)    
    report.join( HC_NEWLINE )
    report.join( '8. Number of SR aged tickets 60 days (where no dependency on DVCSD)' +HC_NEWLINE)
    report.join( HC_NEWLINE )
    report.join( 'Tickets  ' + str(self.tickets_more_than_sixty.text)+HC_NEWLINE)    
    report.join( HC_NEWLINE )
    report.join( '9. Number of issues identified from system logs' +HC_NEWLINE)
    report.join( HC_NEWLINE )
    report.join( 'Tickets  ' + str(self.system_logs.text)+HC_NEWLINE)    
    report.join( HC_NEWLINE )        
    report.join( '10. Number of alerts/communications from DVCSD actioned' +HC_NEWLINE)
    report.join( HC_NEWLINE )
    report.join( 'Tickets  ' + str(self.dvcsd_contacts.text)+HC_NEWLINE)        
    report.join( HC_NEWLINE )    
    report.join( '11. System up time clarify what is DVCSD and Vendor related on downtime.' +HC_NEWLINE)
    report.join( HC_NEWLINE )
    report.join( 'Not Applicable' +HC_NEWLINE)                

    report.join( HC_NEWLINE )
    report.join( 'Release Management'+HC_NEWLINE )
    report.join( HC_NEWLINE )            


    report.join( '1. Hypercare Exit on deployments major releases - Exit of hypercare after 1 month dependent no P1 or P2 raised by customer/ business in the last 7 days.' +HC_NEWLINE)
    report.join( HC_NEWLINE )
    report.join( 'N/A' +     HC_NEWLINE )
    report.join( '2. Minor releases will have related hypercare of 2 weeks - no P1 or P2 raised by customer/business in the last 4 days to close that hypercare period.' +HC_NEWLINE)    
    report.join( HC_NEWLINE )
    report.join( 'N/A' + HC_NEWLINE )  

    print (report)

    #navigator.clipboard.writeText(report)

















