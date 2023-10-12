from ._anvil_designer import RSAKPITemplate
from anvil import *
#import requests
import anvil.http
import json
import datetime
import dateutil.parser 


class Category(object):
    """Representation of a Category in Sifter"""
    def __init__(self, category):
        self.name = category['name']
        self.issues_url = category['issues_url']
        self.api_issues_url = category['api_issues_url']

class Comment(object):
    """Representation of an Issue in Sifter"""
    def __init__(self, issue):
        self.category = issue['category']
        self.body = issue['body']
        self.priority = issue['priority']
        self.commenter = issue['commenter']
        self.milestone_name = issue['milestone_name']
        self.assignee_name = issue['assignee_name']
        self.status = issue['status']
        self.created_at = issue['created_at']
        self.updated_at = issue['updated_at']

class User(object):
    """Representation of a User in Sifter"""
    def __init__(self, user):
        self.username = user['username']
        self.first_name = user['first_name']
        self.last_name = user['last_name']
        self.email = user['email']
        self.issues_url = user['issues_url']
        self.api_issues_url = user['api_issues_url']

class Milestone(object):
    """Representation of a Milestone in Sifter"""
    def __init__(self, milestone):
        self.name = milestone['name']
        self.due_date = milestone['due_date']
        self.issues_url = milestone['issues_url']
        self.api_issues_url = milestone['api_issues_url']


class Issue(object):
    """Representation of an Issue in Sifter"""
    def __init__(self, issue, account):
        self._account = account
        self.number = issue['number']
        self.subject = issue['subject']
        self.description = issue['description']
        self.priority = issue['priority']
        self.status = issue['status']
        self.assignee_name = issue['assignee_name']
        self.category_name = issue['category_name']
        self.milestone_name = issue['milestone_name']
        self.opener_name = issue['opener_name']
        self.url = issue['url']
        self.api_url = issue['api_url']
        self.comment_count = issue['comment_count']
        self.created_at = issue['created_at']
        self.updated_at = issue['updated_at']
        #Lets make it store the stuff rather than get it each time.
        self.comments = []

    def getComments(self):
        """Gets Comments for a given Issue"""
        if len(self.comments) == 0:        
            json_raw = self._account.request(self.api_url)
            raw_issue = json_raw['issue']
            raw_comments = raw_issue['comments']
            for raw_comment in raw_comments:
                c = Comment(raw_comment)
                self.comments.append(c)

            
        return self.comments

class Project(object):
    """Representation of a project in Sifter"""
    def __init__(self, project, account):
        self._account = account
        self.issues_url = project['issues_url']
        self.archived = project['archived']
        self.url = project['url']
        self.api_url = project['api_url']
        self.milestones_url = project['milestones_url']
        self.api_people_url = project['api_people_url']
        self.api_issues_url = project['api_issues_url']
        self.api_milestones_url = project['api_milestones_url']
        self.api_categories_url = project['api_categories_url']
        self.name = project['name']
        self.primary_company_name = project['primary_company_name']

    def issues(self):
        """Gets all the issues for a given project"""
        issues = []

        # Sort by updated to get most recent activity - added per_page = 10 for debug
        first_page = self.api_issues_url + '?srt=updated&per_page=40'

        # Get page one
        json_raw = self._account.request(first_page)

        # Set the next page
        next_page = json_raw['next_page_url']

        # Set the number of pages
        number_of_pages = json_raw['total_pages']
        print("Num Pages: ",number_of_pages)
        #for current_page in range(number_of_pages):
        for current_page in range(1):
         
            # Create a wrapper for each issue, add it to the list
            raw_issues = json_raw['issues']
            for raw_issue in raw_issues:
                i = Issue(raw_issue, self._account)
                i.getComments()
                issues.append(i)

            # Make a request for the next page
            if current_page < number_of_pages - 1:
                # store the results
                json_raw = self._account.request(next_page)

            # set the next page
            next_page = json_raw['next_page_url']

        return issues

    def milestones(self):
        """Gets all the milestones for a given project"""
        milestones = []
        json_raw = self._account.request(self.api_milestones_url)

        raw_milestones = json_raw['milestones']
        for raw_milestone in raw_milestones:
            m = Milestone(raw_milestone)
            milestones.append(m)

        return milestones

    def categories(self):
        """Gets all the categories for a given project"""
        categories = []
        json_raw = self._account.request(self.api_categories_url)

        raw_categories = json_raw['categories']
        for raw_category in raw_categories:
            c = Category(raw_category)
            categories.append(c)

        return categories

    def people(self):
        """Gets all the people for a given project"""
        people = []
        json_raw = self._account.request(self.api_people_url)

        raw_people = json_raw['people']
        for raw_user in raw_people:
            u = User(raw_user)
            people.append(u)

        return people


class Account(object):
    """Account wrapper for Sifter"""
    def __init__(self, host, token):
        self.host = host
        self.token = token
        self.url = self.host 

    def request(self, url):
        """Requests JSON object from Sifter URL"""
        #req = requests.get(url, headers={'X-Sifter-Token': self.token,'Accept': 'application/json'})
        anvil.http.request(url, headers={'X-Sifter-Token': self.token,'Accept': 'application/json'})
        try:
            loadcontent =  json.loads(req.content)
        except ValueError:
            return loadcontent['issue']
        else:
            return loadcontent

    def project(self):
        """Gets the project from RSA sifter account"""

        json_raw = self.request(self.url)
        print(json_raw)
        raw_project = json_raw['project']
        proj = Project(raw_project, self)


        return proj
    

def exceedsResponse(iss, priority):
    rational = 'MarkKennedy,AdrianWilliamson,RoyHann,WojtekRappak,PatJennings'

    #Lets Squeeze the name as my name has two space for some reason
    commentor = ''.join(iss.opener_name.split())

    if commentor in rational:
        return False
    else:
        responseDue = dateutil.parser.parse(iss.created_at) + priority
        for comment in iss.comments[1:]:
            commentor = ''.join(comment.commenter.split())
            if commentor in rational:
                if dateutil.parser.parse(comment.created_at) > responseDue:
                    return True
                else:
                    return False


class RSAKPI(RSAKPITemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.

  def exit_btn_click(self, **event_args):
    """This method is called when the button is clicked"""
    return

  def sifter_btn_click(self, **event_args):
    """This method is called when the button is clicked"""
    P1 = datetime.timedelta(minutes=30)
    P2 = datetime.timedelta(minutes=60)
    P3 = datetime.timedelta(hours=4)
    P4 = datetime.timedelta(hours=24)

    a = Account("https://rsa.sifterapp.com/api/projects/23454", "8de196b4c23a45f62676e9c08aec5490")
    RSA = a.project()
    RSATickets = RSA.issues()

    c = RSATickets[0].getComments()
    print (c[0].commenter)

    print (len(RSATickets))

    failedresponse = []
    
    for kpi in RSATickets:

        kpi_created = dateutil.parser.parse(kpi.created_at)
        tz = kpi_created.tzinfo

        if kpi_created.year == int(self.year.selected_value) and kpi_created.month == int(self.month.selected_value):
            print(str(kpi.number) + ' included in this month')

            failedresponse = []

            if kpi.priority == "Critical": 
                self.critical.text = self.critical.text + 1
                if exceedsResponse(kpi,P1):
                    print(str(kpi.number)+' Exceeds response time')
                    failedresponse.append('P1 : '+str(kpi.number))
            elif kpi.priority == "High":
                self.high.text = self.high.text + 1
                if exceedsResponse(kpi,P2):
                    print(str(kpi.number)+' Exceeds response time')
                    failedresponse.append('P2 : '+str(kpi.number))                
            elif kpi.priority == "Normal": 
                self.normal.text = self.normal.text + 1                
                if exceedsResponse(kpi,P3):
                    print(str(kpi.number)+' Exceeds response time')  
                    failedresponse.append('P3 : '+str(kpi.number))                                  

            elif kpi.priority == "Low":
                self.low.text = self.low.text + 1                
                if exceedsResponse(kpi,P4):
                    print(str(kpi.number)+' Exceeds response time') 
                    failedresponse.append('P4 : '+str(kpi.number))                                    
            elif kpi.priority == "Trivial":                
                self.trivial.text = self.trivial.text + 1
            else: 
                print('Unexpected Priority found : '+ kpi.priority)

            if kpi.category_name == "Service Request":
                self.service_requests.text = self.service_requests.text + 1

            if kpi.subject[1:17].lower == "application error":
                self.system_logs.text = self.system_logs.text + 1

            if kpi.subject[1:5].lower == "dvcsd":
                self.dvcsd_contacts.text = self.dvcsd_contacts.text + 1

            if dateutil.parser.parse(kpi.created_at) + datetime.timedelta(days=10) >= datetime.datetime.now(tz):
                self.tickets_less_than_ten_days.text = self.tickets_less_than_ten_days.text + 1

            if dateutil.parser.parse(kpi.created_at) + datetime.timedelta(days=60) <= datetime.datetime.now(tz):
                self.tickets_more_than_sixty.text = self.tickets_more_than_sixty.text + 1 

            if kpi.status == "Open":
                self.open.text = self.open.text +1
            elif kpi.status == "Reopened":
                self.reopened.text = self.reopened.text + 1
            elif kpi.status == "Follow Up":
                self.followup.text = self.followup.text + 1
            elif kpi.status == "Resolved":
                self.resolved.text = self.resolved.text + 1
            elif kpi.status == "Closed":
                self.closed.text = self.closed.text + 1
            else: 
                print('Unexpected status found : '+ kpi.status)  

            self.total.text = self.open.text + self.reopened.text + self.followup.text + self.resolved.text + self.closed.text



    print("New this month:")
    print("Critical : " + str(self.critical.text))
    print("High : " + str(self.high.text))
    print("Normal : " + str(self.normal.text))
    print("Low : " + str(self.low.text))
    print("Trivial : " + str(self.trivial.text))

    return

  def save_btn_click(self, **event_args):
    """This method is called when the button is clicked"""
    with open('c:\\temp\\python_kpi_report.txt', 'a') as report:
        HC_NEWLINE = '\n'
        HC_TAB = '\t'
        report.write( 'RSA KPI Report for '+'Test Month' +HC_NEWLINE)
        report.write( HC_NEWLINE )
        report.write( 'Incident Management'+HC_NEWLINE )
        report.write( HC_NEWLINE )
        report.write( '1. Number of Incidents in month'+HC_NEWLINE )
  
        report.write( HC_NEWLINE )
        report.write( 'Critical  ' + HC_TAB + str(self.critical.text) + HC_NEWLINE )
        report.write( 'High  '  + HC_TAB+HC_TAB + str(self.high.text) + HC_NEWLINE)	
        report.write( 'Normal  ' + HC_TAB + str(self.normal.text)+ HC_NEWLINE)
        report.write( 'Low  '  + HC_TAB+HC_TAB + str(self.low.text)+ HC_NEWLINE)
        report.write( 'Trivial  ' + HC_TAB + str(self.trivial.text)+ HC_NEWLINE)
  
        report.write( HC_NEWLINE +'Failed SLAs on SIFTER response time for: ' + HC_NEWLINE)
  
        if len(self.failedresponse) == 0:
            report.write( HC_NEWLINE +'None.' + HC_NEWLINE)
        else:
            report.write( HC_NEWLINE )
            for kpifailure in self.failedresponse:
                report.write( 'SIFTER  ' + HC_TAB + kpifailure + HC_NEWLINE )
  
        report.write( HC_NEWLINE )
        report.write( '1.1 SIFTER Volumes'+HC_NEWLINE )
  
        report.write( HC_NEWLINE )
        report.write( 'Open' + HC_TAB + HC_TAB+ str(self.open.text) + HC_NEWLINE )
        report.write( 'Reopened'  + HC_TAB + str(self.reopened.text) + HC_NEWLINE)    
        report.write( 'Followup' + HC_TAB + str(self.followup.text)+ HC_NEWLINE)
        report.write( 'Resolved'  + HC_TAB + str(self.resolved.text)+ HC_NEWLINE)
        report.write( 'Closed' + HC_TAB +HC_TAB+ str(self.closed.text)+ HC_NEWLINE)    
        report.write( 'Total' + HC_TAB +HC_TAB+ str(self.total.text)+ HC_NEWLINE)    
  
        report.write( HC_NEWLINE )
        report.write( '2. Percentage of incidents that met service levels (where no dependance on DVCSD)' +HC_NEWLINE)
        report.write( HC_NEWLINE )    
        report.write( 'Percentage  ' + HC_TAB +  str(self.percentage_incidents_in_sla.text) + '%' +HC_NEWLINE )
        report.write( HC_NEWLINE )
        report.write( '3. First contact resolution rate' +HC_NEWLINE)    
        report.write( HC_NEWLINE )
        report.write( 'Not Applicable  All incidents raised through SIFTER'+HC_NEWLINE)
        report.write( HC_NEWLINE )
        report.write( '4. Number of incident backlog/aged tickets less than 10 days old (where no dependency on DVCSD)' +HC_NEWLINE)    
        report.write( HC_NEWLINE )
        report.write( 'Tickets  ' + str(self.tickets_less_than_ten_days.text)+HC_NEWLINE)        
        report.write( HC_NEWLINE )
        report.write( '5. Unplanned Outages split into DVCSD and Vendor issues' +HC_NEWLINE)    
        report.write( HC_NEWLINE )
        report.write( 'Not Applicable, Production is managed by DVCSD'+HC_NEWLINE)
        report.write( HC_NEWLINE )
        report.write( '6. Number of Service requests' +HC_NEWLINE)
        report.write( HC_NEWLINE )    
        report.write( 'Tickets  ' + str(self.service_requests.text)+HC_NEWLINE)    
        report.write( HC_NEWLINE )
        report.write( '7. Percentage of service requests that met service levels.' +HC_NEWLINE)    
        report.write( HC_NEWLINE )
        report.write( 'Not Applicable, There is no SLA for service requests'+HC_NEWLINE)    
        report.write( HC_NEWLINE )
        report.write( '8. Number of SR aged tickets 60 days (where no dependency on DVCSD)' +HC_NEWLINE)
        report.write( HC_NEWLINE )
        report.write( 'Tickets  ' + str(self.tickets_more_than_sixty.text)+HC_NEWLINE)    
        report.write( HC_NEWLINE )
        report.write( '9. Number of issues identified from system logs' +HC_NEWLINE)
        report.write( HC_NEWLINE )
        report.write( 'Tickets  ' + str(self.system_logs.text)+HC_NEWLINE)    
        report.write( HC_NEWLINE )        
        report.write( '10. Number of alerts/communications from DVCSD actioned' +HC_NEWLINE)
        report.write( HC_NEWLINE )
        report.write( 'Tickets  ' + str(self.dvcsd_contacts.text)+HC_NEWLINE)        
        report.write( HC_NEWLINE )    
        report.write( '11. System up time clarify what is DVCSD and Vendor related on downtime.' +HC_NEWLINE)
        report.write( HC_NEWLINE )
        report.write( 'Not Applicable' +HC_NEWLINE)                
  
        report.write( HC_NEWLINE )
        report.write( 'Release Management'+HC_NEWLINE )
        report.write( HC_NEWLINE )            
  
  
        report.write( '1. Hypercare Exit on deployments major releases - Exit of hypercare after 1 month dependent no P1 or P2 raised by customer/ business in the last 7 days.' +HC_NEWLINE)
        report.write( HC_NEWLINE )
        report.write( 'N/A' +     HC_NEWLINE )
        report.write( '2. Minor releases will have related hypercare of 2 weeks - no P1 or P2 raised by customer/business in the last 4 days to close that hypercare period.' +HC_NEWLINE)    
        report.write( HC_NEWLINE )
        report.write( 'N/A' + HC_NEWLINE )  
















