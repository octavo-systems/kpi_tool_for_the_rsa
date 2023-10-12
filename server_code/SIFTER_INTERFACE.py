from anvil import *
import anvil.server
import requests
#import anvil.http
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




@anvil.server.callable
def GetRSASIFTER(form):

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

        if kpi_created.year == int(form.year.selected_value) and kpi_created.month == int(form.month.selected_value):
            print(str(kpi.number) + ' included in this month')

            failedresponse = []

            if kpi.priority == "Critical": 
                form.critical.text = form.critical.text + 1
                if exceedsResponse(kpi,P1):
                    print(str(kpi.number)+' Exceeds response time')
                    failedresponse.append('P1 : '+str(kpi.number))
            elif kpi.priority == "High":
                form.high.text = form.high.text + 1
                if exceedsResponse(kpi,P2):
                    print(str(kpi.number)+' Exceeds response time')
                    failedresponse.append('P2 : '+str(kpi.number))                
            elif kpi.priority == "Normal": 
                form.normal.text = form.normal.text + 1                
                if exceedsResponse(kpi,P3):
                    print(str(kpi.number)+' Exceeds response time')  
                    failedresponse.append('P3 : '+str(kpi.number))                                  

            elif kpi.priority == "Low":
                form.low.text = form.low.text + 1                
                if exceedsResponse(kpi,P4):
                    print(str(kpi.number)+' Exceeds response time') 
                    failedresponse.append('P4 : '+str(kpi.number))                                    
            elif kpi.priority == "Trivial":                
                form.trivial.text = form.trivial.text + 1
            else: 
                print('Unexpected Priority found : '+ kpi.priority)

            if kpi.category_name == "Service Request":
                form.service_requests.text = form.service_requests.text + 1

            if kpi.subject[1:17].lower == "application error":
                form.system_logs.text = form.system_logs.text + 1

            if kpi.subject[1:5].lower == "dvcsd":
                form.dvcsd_contacts.text = form.dvcsd_contacts.text + 1

            if dateutil.parser.parse(kpi.created_at) + datetime.timedelta(days=10) >= datetime.datetime.now(tz):
                form.tickets_less_than_ten_days.text = form.tickets_less_than_ten_days.text + 1

            if dateutil.parser.parse(kpi.created_at) + datetime.timedelta(days=60) <= datetime.datetime.now(tz):
                form.tickets_more_than_sixty.text = form.tickets_more_than_sixty.text + 1 

            if kpi.status == "Open":
                form.open.text = form.open.text +1
            elif kpi.status == "Reopened":
                form.reopened.text = form.reopened.text + 1
            elif kpi.status == "Follow Up":
                form.followup.text = form.followup.text + 1
            elif kpi.status == "Resolved":
                form.resolved.text = form.resolved.text + 1
            elif kpi.status == "Closed":
                form.closed.text = form.closed.text + 1
            else: 
                print('Unexpected status found : '+ kpi.status)  

            form.total.text = form.open.text + form.reopened.text + form.followup.text + form.resolved.text + form.closed.text



    print("New this month:")
    print("Critical : " + str(form.critical.text))
    print("High : " + str(form.high.text))
    print("Normal : " + str(form.normal.text))
    print("Low : " + str(form.low.text))
    print("Trivial : " + str(form.trivial.text))

    return