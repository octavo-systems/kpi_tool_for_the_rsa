from anvil import *
import anvil.server
import requests
#import anvil.http
import json
import datetime
import dateutil.parser
import sys
import platform


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

    def issuesPriority(self, priority: int) -> int:
        """Gets count of the issues for a given priority"""

        # Sort by updated to get most recent activity - added per_page = 1 reduce traffic
        first_page = self.api_issues_url + '?p='+str(priority)+'&srt=updated&per_page=1'
        # Get page one
        json_raw = self._account.request(first_page)
        # Get the headline count
        count = json_raw['results_count']
        print("Got Priority Count of " +str(count)+ " from "+self.api_issues_url+ '?p='+str(priority)+'&srt=updated&per_page=1')              
        return count

    def issuesStatus(self, status: int) -> int:
        """Gets count of the issues for a given status"""

        # Sort by updated to get most recent activity - added per_page = 1 reduce traffic
        # https://rsa.sifterapp.com/projects/23454/issues?s=137089&srt=updated&d=d is for Open
        first_page = self.api_issues_url + '?s='+str(status)+'&srt=updated&per_page=1' 
        # Get page one
        json_raw = self._account.request(first_page)
        # Get the headline count
        count = json_raw['results_count']
        print("Got Status Count of " +str(count)+ " from "+self.api_issues_url+'?s='+str(status)+'&srt=updated&per_page=1')        
        return count

    def issuesKPI(self,year: int,month: int, priority: int, volume: int, service_requests: int, system_logs: int, dvcsd_contacts: int, tickets_less_than_ten_days: int, tickets_more_than_sixty: int ) -> []:
        """Gets all the issues for a given project, month/year, priority"""

        # Sort by updated to get most recent activity - added per_page = 10 for debug
        first_page = self.api_issues_url + '?p='+str(priority)+'&srt=updated&per_page='+str(volume)

        # Get page one
        json_raw = self._account.request(first_page)

        # Set the next page - should not be needed....
        next_page = json_raw['next_page_url']

        # Set the number of pages - hoping for 1....
        number_of_pages = json_raw['total_pages']
        print("Num Pages: ",number_of_pages)

        if priority == 1:
            statusText = "Critical"
            KPIInterval = datetime.timedelta(minutes=30)
        elif priority == 2:
            statusText = "High"
            KPIInterval = datetime.timedelta(minutes=60)
        elif priority == 3:
            statusText = "Normal" 
            KPIInterval = datetime.timedelta(hours=4)  
        elif priority == 4:
            statusText = "Low"
            KPIInterval = datetime.timedelta(hours=24)    
        elif priority == 5:
            statusText = "Trivial"
            KPIInterval = datetime.timedelta(days=3650)                               
        failedresponse = []
        for current_page in range(number_of_pages): 
            # Create a wrapper for each issue, add it to the list
            raw_issues = json_raw['issues']
            for raw_issue in raw_issues:
                i = Issue(raw_issue, self._account)
                kpi_created = dateutil.parser.parse(i.created_at)
                tz = kpi_created.tzinfo

                if kpi_created.year == year and kpi_created.month == month:
                    i.getComments()

                    if i.priority == statusText: 
                        count = count + 1
                        if exceedsResponse(kpi,KPIInterval):
                            print(str(kpi.number)+' Exceeds response time')
                            failedresponse.append('P'+str(priority)+' : '+str(kpi.number))
                    else:
                        #Raise an exception? 
                        print('Unexpected Priority found : '+ kpi.priority)
                  
                    if i.category_name == "Service Request":
                      service_requests = service_requests + 1

                    if i.subject[1:17].lower == "application error":
                      system_logs = system_logs + 1
                      
                    if i.subject[1:5].lower == "dvcsd":
                      dvcsd_contacts = dvcsd_contacts + 1

                    if kpi_created + datetime.timedelta(days=10) >= datetime.datetime.now(tz):
                      tickets_less_than_ten_days = tickets_less_than_ten_days + 1

                    if kpi_created + datetime.timedelta(days=60) <= datetime.datetime.now(tz):
                      tickets_more_than_sixty = tickets_more_than_sixty + 1 
              
                else:
                    #should always exit here
                    return  failedresponse                  

            # Make a request for the next page - unlikely 
            if current_page < number_of_pages - 1:
                # store the results
                json_raw = self._account.request(next_page)

            # set the next page
            next_page = json_raw['next_page_url']
  
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
        req = requests.get(url, headers={'X-Sifter-Token': self.token,'Accept': 'application/json'})
        #anvil.http.request(url, headers={'X-Sifter-Token': self.token,'Accept': 'application/json'})
        try:
            loadcontent =  json.loads(req.content)
        except ValueError:
            return loadcontent['issue']
        else:
            return loadcontent

    def project(self):
        """Gets the project from RSA sifter account"""
        json_raw = self.request(self.url)
        raw_project = json_raw['project']
        proj = Project(raw_project, self)
        print("Got Project from "+self.url)      
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


@anvil.server.callable
def GetRSASIFTER_priority(priority: int ) -> int:
  # I wonder if I get the same server, in which case I guess I should check for a SIFTER session in play?
  a = Account("https://rsa.sifterapp.com/api/projects/23454", "8de196b4c23a45f62676e9c08aec5490")
  RSA = a.project()

  count = RSA.issuesPriority(priority)
  return count

@anvil.server.callable
def GetRSASIFTER_status(status: int ) -> int:
  
  a = Account("https://rsa.sifterapp.com/api/projects/23454", "8de196b4c23a45f62676e9c08aec5490")
  RSA = a.project()

  count = RSA.issuesStatus(status)
  return count

@anvil.server.callable
def GetRSASIFTER_MonthKPI(self,year: int,month: int, priority: int, volume: int, service_requests: int, system_logs: int, dvcsd_contacts: int, tickets_less_than_ten_days: int, tickets_more_than_sixty: int ) -> []:
  a = Account("https://rsa.sifterapp.com/api/projects/23454", "8de196b4c23a45f62676e9c08aec5490")
  RSA = a.project()

  return RSA.issuesKPI(year,month,priority,volume)
  
   