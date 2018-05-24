"""The status command."""

import warnings

warnings.filterwarnings("ignore")

import os

import re

import sys

import math

import time

import getpass

import datetime

import requests

import prettytable

from random import randint

from keystoneclient.auth.identity import v3

from keystoneclient import session

from keystoneclient.v3 import client

from novaclient import client as novaClient

from novaclient import exceptions

from keystoneauth1 import exceptions as e

from json import dumps

from json import loads

from json import load

from .base import Base


class Status(Base):
    """Display Status of the virtual Instance or Instances"""

    def run(self):
        cacheFiles = []
        i          = 0
        region     = ''
        search     = False

        values = self.options
        for key, value in values.iteritems():
            if key == '--region':
               region = value.upper()
               if region not in ('SCL1','LA1'):
                  search = True
                  break
            if key == '--instance':
               if value is not None:
                  instance    = True
                  instance_id = value
               else:
                   instance    = False
                   instance_id = ''
            if key == '--list':
               if value is not None:
                  instanceList    = True
                  instanceList_id = value
               else:
                   instanceList    = False
                   instanceList_id = ''   
            if key == '--expiry':
               if value is not None:
                  expiryList    = True
                  expiryList_id = value
               else:
                  expiryList    = False
                  expiryList_id = '' 


        restrict_users = ('sysadmin', 'root')

        ldap_user = getpass.getuser()

        if ldap_user in restrict_users:
           print("- Error: Login using LDAP username/password only.")
           return False

        if search == True:
           print('- Error: Region Name doesn\'t exists, Please try again!')
           return False

        current_dir = os.environ["HOME"]

        try:
            for file in os.listdir(current_dir + "/" + '.' + region):
                if file.endswith(".cred"):
                   cacheFiles.insert(i,file)
                   i = i + 1
                else:
                    continue
        except(ValueError,IOError,OSError):
            print("- Error: Could not find credentials file in:" + os.environ["HOME"])
            return False

        if len(cacheFiles) == 0:
           print '- Error: You need to login to list/create Instances.'
           sys.exit()
        else:
            if len(cacheFiles) > 1:
               userDisplay = prettytable.PrettyTable(["NO.", "USERNAME", "ID"])
               userDisplay.align["USERNAME"] = "l"
               userDisplay.align["ID"] = "l"
               userDisplay.padding_width = 1

            if len(cacheFiles) > 0:
               l = 0
               user_dict = {}
               for file in cacheFiles:
                   fileSize = os.stat(current_dir + "/" + '.' + region + "/" + file).st_size != 0
                   if fileSize:
                      with open(current_dir + "/" + '.' + region + "/" + file) as cred:
                           credentials = cred.readlines()
                           d  = ','.join(credentials)
                           myDict = eval(d)
                           l = l + 1
                           for j,k in myDict.items():

                               if j == 'username':
                                  username = str(k)

                               if j == 'token':
                                  token = str(k)

                               if j == 'id':
                                  id = str(k)

                               if j == 'project_name':
                                  project_name = str(k)

                               if j == 'region':
                                  region = str(k)

                               if j == 'project_domain_name':
                                  project_domain_name = str(k)

                                  if len(cacheFiles) > 1:
                                     userDisplay.add_row([l, username, id])

                                  record = {'project_name': project_name, 'project_domain_name': project_domain_name, 'username': username, 'token': token, 'id': id, 'region': region}
                                  user_dict[l] = record
               records = user_dict
               evaluate = l
               if len(cacheFiles) > 1:
                  print(userDisplay)

               if evaluate == 1:
                  for key,value in records.iteritems():
                      singleRecord = value

                  timeout = self.timer(region,singleRecord['username'])

                  if timeout == False:
                     print '- Error: Your session timed out, Please login again.'
                     sys.exit()
                  else:
                      if instance == True:
                         self.displayInstance(region, singleRecord, instance_id)
                      if instanceList == True:
                         self.displayInstances(region, singleRecord, instanceList_id) 
                      if expiryList == True:
                         self.expiryInstances(region, singleRecord, expiryList_id)
               else:
                   while True:
                       srNo = raw_input('Please enter the NO. of your username:')
                       getNo = self.processNumber(srNo,records)
                       if isinstance(getNo, dict):
                          serial = True
                          break;
                   if serial == True:
                      getToken = getNo

                      timeout = self.timer(getToken['username'])
                      if timeout == False:
                         print '- Error: Your session timed out, Please login again.'
                         sys.exit()
                      else:
                          if instance == True:
                             self.displayInstance(region, getToken, instance_id)
                          if instanceList == True:
                             self.displayInstances(region, getToken, instanceList_id)
                          if expiryList == True:
                             self.expiryInstances(region, singleRecord, expiryList_id)


    def processNumber(self,serialNo,rec):
        s = False
        self.rec = rec
        self.serialNo = serialNo
        try:
            for key,value in self.rec.iteritems():
                if (int(key) == int(self.serialNo)):
                   s = True
                   getAuth = value
		   break
                else:
                    s = False
            if s == True:
               return getAuth
            else:
                return False
        except(ValueError):
            return False
        

    def displayInstance(self, datacenter, auth,instance):
        self.datacenter = datacenter
        self.auth       = auth
        self.instance   = instance
        current_dir     = os.environ["HOME"]       

 
        for key, value in self.auth.iteritems():
            if key == 'token':
               token = value

            if key == 'username':
               username = value

            if key == 'project_name':
               project_name = value

            if key == 'region':
               region = value

            if key == 'project_domain_name':
               project_domain_name = value
        

        print('\n')
        print '- LOADING : ........ ',
        sys.stdout.flush()


        try: 
            if region == 'SCL1':
               novaauth    = v3.Token(auth_url='http://expostack.tf-net.mydomain.com:35357/v3',token=token,project_name=project_name,project_domain_name=project_domain_name)
            if region == 'LA1':
               novaauth    = v3.Token(auth_url='http://expostack-02.tf-net.mydomain.com:35357/v3',token=token,project_name=project_name,project_domain_name=project_domain_name)

            novasession = session.Session(auth=novaauth)
            keystone    = client.Client(session=novasession)
            nova        = novaClient.Client('2', session=novasession)
        except(exceptions.AuthorizationFailure):
        
            self.progress()
            print ' [DONE]'
            print('\n')

            prompt = '- Error: Unable to authenticate or validate the existing authorization token for ' + username + ' at ' + time.strftime("%d/%m/%Y") + ' ' + time.strftime("%I:%M:%S") + '.' 
            self.log(self.datacenter,username,prompt)
            print(prompt)
            return 1
        except(exceptions.Unauthorized): 
            
            self.progress()
            print ' [DONE]'
            print('\n')

            prompt = '- Error: Authentication failed due to invalid token for ' + username + ' at ' + time.strftime("%d/%m/%Y") + ' ' + time.strftime("%I:%M:%S") + '.'
            self.log(self.datacenter,username,prompt) 
            print(prompt)           
            return 1
    

        try:
            servers = nova.servers.list(search_opts={'all_tenants': 1})
        except(exceptions.NotFound):
            
            self.progress()
            print ' [DONE]'
            print('\n')

            prompt = '- Error: Instance could not be found for ' + username + ' at ' + time.strftime("%d/%m/%Y") + ' ' + time.strftime("%I:%M:%S") + '.'
            self.log(self.datacenter,username,prompt)
            print(prompt)
            return 1

        except(e.Unauthorized):
            self.progress()
            print ' [DONE]'
            print('\n')

            prompt = '- Error: Login into Region: ' + self.datacenter + ' to perform this Operation.'
            self.log(self.datacenter,username,prompt)
            print(prompt)
            return 1

        except(e.from_response):
            self.progress()
            print ' [DONE]'
            print('\n')

            prompt = '- Error: Login into Region: ' + self.datacenter + ' to perform this Operation.'
            self.log(self.datacenter,username,prompt)
            print(prompt)
            return 1

        try:
            for myNode in range(len(servers)):
                s = servers[myNode]
                if s.name.lstrip() == self.instance.strip():
                   instance_id = s.id
                   break
             
        except(exceptions.NotFound): 
            
            self.progress()
            print ' [DONE]'
            print('\n')

            prompt = '- Error: Instance could not be found for ' + username + ' at ' + time.strftime("%d/%m/%Y") + ' ' + time.strftime("%I:%M:%S") + '.'
            self.log(self.datacenter,username,prompt)
            print(prompt)
            return 1

        try:
            display = nova.servers.get(instance_id)
        except(exceptions.NotFound):
            
            self.progress()
            print ' [DONE]'
            print('\n')

            prompt = '- Error: Instance could not be found for ' + username + ' at ' + time.strftime("%d/%m/%Y") + ' ' + time.strftime("%I:%M:%S") + '.'
            self.log(self.datacenter,username,prompt)
            print(prompt)
            return 1
        except(IOError,IndexError,KeyError,NameError,OSError,RuntimeError,SyntaxError,IndentationError,TypeError,UnboundLocalError,ValueError):
            
            self.progress()
            print ' [DONE]'
            print('\n')

            error  = '- Error: Instance Name : ' + self.instance + ' is Invalid. Please try Again.'
            prompt = '- Error: Instance could not be found for ' + username + ' at ' + time.strftime("%d/%m/%Y") + ' ' + time.strftime("%I:%M:%S") + '.'
            self.log(self.datacenter,username,prompt)
            print(error)
            return 1



        try:
            d = dumps(display._info, sort_keys=True, indent=4, separators=(',', ': '))

            username = username.lower()

            chk = username.find('@')

            if chk != -1:
               storeusername = username.split('@')
               uname = storeusername[0]
            if chk == -1:
               uname = username

            fileName = self.random_with_N_digits(4)
            fopen    = open(current_dir + "/" + '.' + self.datacenter + "/" + '.' + uname + "/" + '.' + str(fileName), 'w')
            fopen.write('[')
            fopen.write(d)
            fopen.write(']')
            fopen.close()

            userDisplay = prettytable.PrettyTable(["INSTANCE ID", "INSTANCE NAME", "IP ADDRESS", "STATUS"])
            userDisplay.align["INSTANCE ID"]   = "l"
            userDisplay.align["INSTANCE NAME"] = "l"
            userDisplay.align["IP ADDRESS"]    = "l"
            userDisplay.align["STATUS"]        = "l" 
            userDisplay.padding_width = 1

            fileSize = os.stat(current_dir + "/" + '.' + self.datacenter + "/" + '.' + uname + "/" + '.' + str(fileName)).st_size != 0
            if fileSize:
               with open(current_dir + "/" + '.' + self.datacenter + "/" + '.' + uname + "/" + '.' + str(fileName), 'r') as f:
                    data = load(f)
                    j             = 0
                    ipAddr        = []
                    instance_id   = []
                    instance_name = []
                    stat          = []
                    for item in data:
                        for key, value in item.items():
                            if key == 'addresses':
                               for k, v in value.iteritems():
                                   if type(k):
                                      for each in v:
                                          for column, row in each.items():
                                              if column == 'addr':
                                                 ipAddr.insert(j,row)
                            if key == 'id':
                               instance_id.insert(j,value)
                            if key == 'name':
                               instance_name.insert(j,value)
                            if key == 'status':
                               stat.insert(j,value)
                               j = j + 1
            

               for j,k,l,m in map(None,instance_id,instance_name,ipAddr,stat):
                   userDisplay.add_row([j,k,l,m])

               self.progress()
               print ' [DONE]'
               print('\n')

               print(userDisplay)
          
               fileToRemove = current_dir + "/" + '.' + self.datacenter + "/" + '.' + uname + "/" + '.' + str(fileName)
               os.remove(fileToRemove)

        except(IOError,IndexError,KeyError,NameError,OSError,RuntimeError,SyntaxError,IndentationError,TypeError,UnboundLocalError,ValueError):

            prompt = '- Error: Unknown Error, Instance could not be found for ' + username + ' at ' + time.strftime("%d/%m/%Y") + ' ' + time.strftime("%I:%M:%S") + '.'
            self.log(self.datacenter,username,prompt)
            print(prompt)

            return 1
        else:
            return 0


    def random_with_N_digits(self,n):
        self.n = n
        range_start = 10**(self.n-1)
        range_end = (10**self.n)-1
        return randint(range_start, range_end)


    def timer(self,region,username):
        self.region   = region
        self.username = username
        current_dir   = os.environ["HOME"]

        self.username = self.username.lower()

        chk = self.username.find('@')

        if chk != -1:
           storeusername = self.username.split('@')
           uname = storeusername[0]
        if chk == -1:
           uname = self.username

        path    = current_dir + "/" + '.' + self.region + "/" + '.' + uname + "/" + '.' + uname
        chkFile = os.path.dirname(path)
        if not os.path.exists(path):
           return False
        else:
            stack    = '%Y-%m-%d %H:%M:%S'

            fileTime = os.path.getmtime(path)
            now      = datetime.datetime.now()

            y = now.year
            d = now.day
            m = now.month
            h = now.hour
            i = now.minute
            s = now.second

            file    = datetime.datetime.fromtimestamp(int(fileTime)).strftime('%Y-%m-%d %H:%M:%S')
            sysTime = str(y) + '-' + str(m) + '-' + str(d) + ' ' + str(h) + ':' + str(i) + ':' + str(s)

            d1 = datetime.datetime.strptime(sysTime, stack)
            d2 = datetime.datetime.strptime(file, stack)
            daysDiff = d1 - d2
            daysDiff = str(daysDiff)
            minutesDiff = daysDiff.split(':')
        
            if int(minutesDiff[1]) > 60:

               working_dir = current_dir + "/" + '.' + self.region + "/" + '.' + uname

               log = current_dir + "/" + '.' + self.region + "/" + '.' + uname + "/" + '.' + uname + '.log'

               if not os.path.exists(log):
                  return False

               os.chdir(working_dir)

               logFile = '.' + uname + '.log'

               mvFile = logFile + '.' + time.strftime("%d-%m-%Y") + "-" + time.strftime("%I:%M:%S")

               os.rename(logFile,mvFile)

               return False
            else:
                return True



    def displayInstances(self,datacenter,auth,instance):
        self.datacenter = datacenter
        self.auth       = auth
        self.instance   = instance
        current_dir     = os.environ["HOME"]

        if self.instance != 'all':
           print '- Error: Invalid Command, Please try again.'
           sys.exit()

        for key, value in self.auth.iteritems():
            if key == 'token':
               token = value

            if key == 'id':
               userid = value

            if key == 'username':
               username = value

            if key == 'project_name':
               project_name = value

            if key == 'region':
               region = value

            if key == 'project_domain_name':
               project_domain_name = value

        print('\n')
        print '- LOADING : ........ ',
        sys.stdout.flush()

        try:
            if region == 'SCL1':
               novaauth    = v3.Token(auth_url='http://expostack.tf-net.mydomain.com:35357/v3',token=token,project_name=project_name,project_domain_name=project_domain_name)
            if region == 'LA1':
               novaauth    = v3.Token(auth_url='http://expostack-02.tf-net.mydomain.com:35357/v3',token=token,project_name=project_name,project_domain_name=project_domain_name)

            novasession = session.Session(auth=novaauth)
            keystone    = client.Client(session=novasession)
            nova        = novaClient.Client('2', session=novasession)
        except(exceptions.AuthorizationFailure):
    
            self.progress()
            print ' [DONE]'
            print('\n')

            prompt = '- Error: Unable to authenticate or validate the existing authorization token for ' + username + ' at ' + time.strftime("%d/%m/%Y") + ' ' + time.strftime("%I:%M:%S") + '.'
            self.log(self.datacenter,username,prompt)
            print(prompt)
            return 1
        except(exceptions.Unauthorized):
            
            self.progress()
            print ' [DONE]'
            print('\n')

            prompt = '- Error : Authentication failed due to invalid token for ' + username + ' at ' + time.strftime("%d/%m/%Y") + ' ' + time.strftime("%I:%M:%S") + '.'
            self.log(self.datacenter,username,prompt)
            print(prompt)
            return 1


        userDisplay = prettytable.PrettyTable(["INSTANCE ID", "INSTANCE NAME", "IP ADDRESS", "STATUS"])
        userDisplay.align["INSTANCE ID"]   = "l"
        userDisplay.align["INSTANCE NAME"] = "l"
        userDisplay.align["IP ADDRESS"]    = "l"
        userDisplay.align["STATUS"]        = "l"
        userDisplay.padding_width = 1


        try:
            servers = nova.servers.list(search_opts={'all_tenants': 1})
        except(exceptions.NotFound):

            self.progress()
            print ' [DONE]'
            print('\n')

            prompt = '- Error: Instance could not be found for ' + username + ' at ' + time.strftime("%d/%m/%Y") + ' ' + time.strftime("%I:%M:%S") + '.'
            self.log(self.datacenter,username,prompt)
            print(prompt)
            return 1

        except(e.Unauthorized):
            self.progress()
            print ' [DONE]'
            print('\n')

            prompt = '- Error: Login into Region: ' + self.datacenter + ' to perform this Operation.'
            self.log(self.datacenter,username,prompt)
            print(prompt)
            return 1

        except(e.from_response):
            self.progress()
            print ' [DONE]'
            print('\n')

            prompt = '- Error: Login into Region: ' + self.datacenter + ' to perform this Operation.'
            self.log(self.datacenter,username,prompt)
            print(prompt)
            return 1


        try:
            for myNode in range(len(servers)):
                s = servers[myNode]
                if userid == s.user_id:
                   for key, value in s.addresses.iteritems():
                       for item in value:
                           for hay,stack in item.iteritems():
                               if hay == 'addr':
                                  ip = stack
                   userDisplay.add_row([s.id,s.name,ip,s.status])

            self.progress()
            print ' [DONE]'
            print('\n')

            print(userDisplay)
        except(IOError,IndexError,KeyError,NameError,OSError,RuntimeError,SyntaxError,IndentationError,TypeError,UnboundLocalError,ValueError):

            self.progress()
            print ' [DONE]'
            print('\n')

            prompt = '- Error : Unknown Error Occured while fetching Lease for ' + username + ' at ' + time.strftime("%d/%m/%Y") + ' ' + time.strftime("%I:%M:%S") + '.'
            self.log(self.datacenter,username,prompt)
            print(prompt)
            return 1          
        else:
            return 0


    def progress(self):
        print '\b',
        sys.stdout.flush()
        time.sleep(10)


    def log(self,region,username,prompt):
        self.region   = region
        self.username = username
        self.prompt   = prompt
        current_dir   = os.environ["HOME"]

        self.username = self.username.lower()

        chk = self.username.find('@')
        if chk != -1:
           storeusername = self.username.split('@')
           uname = storeusername[0]
        if chk == -1:
           uname = self.username

        log = open(current_dir + "/" + '.' + self.region + "/" + '.' + uname +"/" + '.' + uname + '.log','a')
        log.write(self.prompt + '\n')

        log.close()



    def expiryInstances(self,datacenter,auth,instance):
        self.datacenter = datacenter
        self.auth       = auth
        self.instance   = instance
        current_dir     = os.environ["HOME"]

        if self.instance != 'list':
           print '- Error: Invalid Command, Please try again.'
           sys.exit()

        for key, value in self.auth.iteritems():
            if key == 'token':
               token = value

            if key == 'id':
               userid = value

            if key == 'username':
               username = value

            if key == 'project_name':
               project_name = value

            if key == 'region':
               region = value 

            if key == 'project_domain_name':
               project_domain_name = value

        print('\n')
        print '- LOADING : ........ ',
        sys.stdout.flush()

        try:
            if region == 'SCL1':
               novaauth    = v3.Token(auth_url='http://expostack.tf-net.mydomain.com:35357/v3',token=token,project_name=project_name,project_domain_name=project_domain_name)
            if region == 'LA1':
               novaauth    = v3.Token(auth_url='http://expostack-02.tf-net.mydomain.com:35357/v3',token=token,project_name=project_name,project_domain_name=project_domain_name)           

            novasession = session.Session(auth=novaauth)
            keystone    = client.Client(session=novasession)
            nova        = novaClient.Client('2', session=novasession)

        except(exceptions.AuthorizationFailure):

            self.progress()
            print ' [DONE]'
            print('\n')

            prompt = '- Error: Unable to authenticate or validate the existing authorization token for ' + username + ' at ' + time.strftime("%d/%m/%Y") + ' ' + time.strftime("%I:%M:%S") + '.'
            self.log(self.datacenter,username,prompt)
            print(prompt)
            return 1

        except(exceptions.Unauthorized):

            self.progress()
            print ' [DONE]'
            print('\n')

            prompt = '- Error : Authentication failed due to invalid token for ' + username + ' at ' + time.strftime("%d/%m/%Y") + ' ' + time.strftime("%I:%M:%S") + '.'
            self.log(self.datacenter,username,prompt)
            print(prompt)
            return 1

        userDisplay = prettytable.PrettyTable(["INSTANCE ID", "INSTANCE NAME", "IP ADDRESS", "STATUS", "LEASE", "LEASE TYPE","CREATED ON"])
        userDisplay.align["INSTANCE ID"]   = "l"
        userDisplay.align["INSTANCE NAME"] = "l"
        userDisplay.align["IP ADDRESS"]    = "l"
        userDisplay.align["STATUS"]        = "l"
        userDisplay.align["LEASE"]         = "l"
        userDisplay.align["LEASE TYPE"]    = "l"
        userDisplay.align["CREATED ON"]    = "l"
        userDisplay.padding_width = 1

        try:
            servers = nova.servers.list(search_opts={'all_tenants': 1})
        except(exceptions.NotFound):
            self.progress()
            print ' [DONE]'
            print('\n')

            prompt = '- Error: Instance could not be found for ' + username + ' at ' + time.strftime("%d/%m/%Y") + ' ' + time.strftime("%I:%M:%S") + '.'
            self.log(self.datacenter,username,prompt)
            print(prompt)
            return 1

        except(exceptions.Unauthorized):

            self.progress()
            print ' [DONE]'
            print('\n')

            prompt = '- Error : Authentication failed due to invalid token for ' + username + ' at ' + time.strftime("%d/%m/%Y") + ' ' + time.strftime("%I:%M:%S") + '.'
            self.log(self.datacenter,username,prompt)
            print(prompt)
            return 1

        except(e.Unauthorized):
            self.progress()
            print ' [DONE]'
            print('\n')

            prompt = '- Error: Login into Region: ' + self.datacenter + ' to perform this Operation.'
            self.log(self.datacenter,username,prompt)
            print(prompt)
            return 1

        except(e.from_response):
            self.progress()
            print ' [DONE]'
            print('\n')

            prompt = '- Error: Login into Region: ' + self.datacenter + ' to perform this Operation.'
            self.log(self.datacenter,username,prompt)
            print(prompt)
            return 1


        callLease = self.callExpiryTime(self.datacenter,username)

        if callLease != False:
           try:
               for myNode in range(len(servers)):
                   s = servers[myNode]

                   if userid == s.user_id:

                      for key, value in s.addresses.iteritems():
                          for item in value:
                              for hay,stack in item.iteritems():
                                  if hay == 'addr':
                                     ip = stack                     
 
                      for item in callLease:
                          for key, value in item.items():                    
                              if key == 'hostname':
                                 node = value
                              if key == 'ipaddress':
                                 ipaddr = value
                              if key == 'leasedays':
                                 lease = value
                              if key == 'requesttype':
                                 request = value
                              if key == 'created_on':
                                 create = value

                          if str(node.strip()) == str(s.name.strip()):
                             server = str(node.strip())
                             ipadd  = str(ip)

                             userDisplay.add_row([s.id,server,ipadd,s.status,str(lease),str(request),str(create)])


               self.progress()
               print ' [DONE]'
               print('\n') 

               print(userDisplay) 

           except(IOError,IndexError,KeyError,NameError,OSError,RuntimeError,SyntaxError,IndentationError,TypeError,UnboundLocalError,ValueError):

               self.progress()
               print ' [DONE]'
               print('\n')

               prompt = '- Error : Unknown Error Occured while fetching Lease for ' + username + ' at ' + time.strftime("%d/%m/%Y") + ' ' + time.strftime("%I:%M:%S") + '.'
               self.log(self.datacenter,username,prompt)
               print(prompt)
               return 1
           else:
               prompt = '- Info : Lease Information fetch successful for ' + username + ' at ' + time.strftime("%d/%m/%Y") + ' ' + time.strftime("%I:%M:%S") + '.'
               self.log(self.datacenter,username,prompt)
               print(prompt)
               return 0
        else:

            self.progress()
            print ' [DONE]'
            print('\n')

            prompt = '- Error : Unknown Error Occured while fetching Lease for ' + username + ' at ' + time.strftime("%d/%m/%Y") + ' ' + time.strftime("%I:%M:%S") + '.'
            self.log(self.datacenter,username,prompt)
            print(prompt)
            return 1



    def callExpiryTime(self,region,username):

        self.region = region
        chk = self.username.find('@')

        if chk != -1:
           storeusername = self.username.split('@')
           uname         = storeusername[0]
        if chk == -1:
           uname = self.username

        if self.region == 'SCL1':
          payload = {'key': self.region}
          r = requests.get('https://vmreports.tf-net.mydomain.com/curl/expiry.php',verify=False, params=payload)

        if self.region == 'LA1':
           payload = {'key': self.region}
           r = requests.get('https://vmreporting-03.dev.la1.us.mydomain.net/curl/expiry.php',verify=False, params=payload)

        if r.status_code == 200:
           current_dir = os.environ["HOME"]
           fopen = open(current_dir + "/" + '.' + self.region + "/" + '.' + uname + "/" + '.lease', 'w')
           fopen.write(r.text)
           fopen.close()
         
           path    = current_dir + "/" + '.' + self.region + "/" + '.' + uname + "/" + '.lease' 
           chkFile = os.path.dirname(path)
           if not os.path.exists(path):
              return False
           else:
               with open(current_dir + "/" + '.' + self.region + "/" + '.' + uname + "/" + '.lease', 'r') as f:
                    data = load(f)    
               return data
        else:
            return False
