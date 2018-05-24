"""The operate command."""

import os

import re

import sys

import math

import time

import getpass

import create

import datetime

from random import randint

from keystoneclient.auth.identity import v3

from keystoneclient import session

from keystoneclient.v3 import client

from novaclient import client as novaClient

from novaclient import exceptions

from keystoneauth1 import exceptions as e

from prettytable import PrettyTable

from json import dumps

from json import loads

from json import load

from .base import Base


class Operate(Base):
    """Perform operations for the virtual Instances"""

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

            if key == '--destroy':
               if value is not None:
                  destroy     = True
                  destroy_id  = value
               else:
                   destroy    = False
                   destroy_id = ''

            if key == '--suspend':
               if value is not None:
                  suspend    = True
                  suspend_id = value
               else:
                   suspend    = False
                   suspend_id = ''

            if key == '--resume':
               if value is not None:
                  resume     = True
                  resume_id  = value
               else:
                   resume    = False
                   resume_id = '' 

            if key == '--poweroff':
               if value is not None:
                  poweroff    = True
                  poweroff_id = value
               else:
                   poweroff    = False
                   poweroff_id = ''

            if key == '--poweron':
               if value is not None:
                  poweron     = True
                  poweron_id  = value
               else:
                   poweron    = False
                   poweron_id = ''

            if key == '--pause':
               if value is not None:
                  pause    = True
                  pause_id = value
               else:
                   pause    = False
                   pause_id = ''

            if key == '--unpause':
               if value is not None:
                  unpause    = True
                  unpause_id = value
               else:
                   unpause    = False
                   unpause_id = '' 

            if key == '--expire':
               if value is not None:
                  expire      = True
                  expire_id   = value
               else:
                   expire     = False
                   expire_id  = '' 

            if key == '--shutdown':
               if value is not None:
                  shutdown    = True
                  shutdown_id = value
               else:
                   shutdown    = False
                   shutdown_id = ''

            if key == '--reboot':
               if value is not None:
                  reboot    = True
                  reboot_id = value
               else:
                   reboot    = False
                   reboot_id = ''

            if key == '--reset':
               if value is not None:
                  reset       = True
                  reset_id    = value
               else:
                   reset      = False
                   reset_id   = ''

            if key == '--status':
               if value is not None:
                  status_id   = value
               else:
                   status_id = ''

            if key == '--changelease':
               if value is not None:
                  changelease    = True
                  changelease_id = value
               else:
                   changelease    = False
                   changelease_id = ''

            if key == '--extend':
               if value is not None:
                  extend       = True
                  extend_id    = value
               else:
                   extend    = False
                   extend_id = ''

            if key == '--flag':
               if value is not None:
                  flag    = True
                  flag_id = value
               else:
                   flag    = False
                   flag_id = ''

            if key == '--property':
                if value is not None:
                    property = True
                    meta_data = value
                else:
                    property = False
                    meta_data = None

            if key == '--instance':
                if value is not None:
                    metadata_instance = True
                    metadata_instance_id = value
                else:
                    metadata_instance = False
                    metadata_instance_id = ''

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
        except(ValueError,IOError):
            print("- Error: Could not find credentials file in:" + os.environ["HOME"])
            return False

        if len(cacheFiles) == 0:
           print '- Error: You need to login to create Instances.'
           sys.exit()
        else:
            if len(cacheFiles) > 1:
               userDisplay = PrettyTable(["NO.", "USERNAME", "ID"])
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
                      if destroy == True:
                         self.destroyInstance(region, singleRecord, destroy_id)
                      if suspend == True:
                         self.suspendInstance(region, singleRecord, suspend_id)
                      if resume == True:
                         self.resumeInstance(region, singleRecord, resume_id)
                      if reboot == True:
                         self.rebootInstance(region, singleRecord, reboot_id)
                      if poweroff == True:
                         self.poweroffInstance(region, singleRecord, poweroff_id)
                      if poweron == True:
                         self.poweronInstance(region, singleRecord, poweron_id)
                      if pause == True:
                         self.pauseInstance(region, singleRecord, pause_id)
                      if unpause == True:
                         self.unpauseInstance(region, singleRecord, unpause_id)
                      if expire == True:
                         self.expireInstance(region, singleRecord, expire_id)
                      if shutdown == True:
                         self.shutdownInstance(region, singleRecord, shutdown_id)
                      if reset == True:
                         self.resetInstance(region, singleRecord, reset_id, status_id)
                      if changelease == True:
                         self.changeleaseInstance(region, singleRecord, changelease_id, extend_id, flag_id)
                      if property == True:
                         self.updateMeta(region, singleRecord, metadata_instance_id, meta_data)
               else:
                   while True:
                       srNo = raw_input('Please enter the NO. of your username:')
                       getNo = self.processNumber(srNo,records)
                       if isinstance(getNo, dict):
                          serial = True
                          break;
                   if serial == True:
                      getToken = getNo

                      timeout = self.timer(region, getToken['username'])
                      if timeout == False:
                         print '- Error: Your session timed out, Please login again.'
                         sys.exit()
                      else:
                          if destroy == True:
                             self.destroyInstance(region, getToken, destroy_id)
                          if suspend == True:
                             self.suspendInstance(region, getToken, suspend_id)
                          if resume == True:
                             self.resumeInstance(region, getToken, resume_id)
                          if reboot == True:
                             self.rebootInstance(region, getToken, reboot_id)
                          if poweroff == True:
                             self.poweroffInstance(region, getToken, poweroff_id)
                          if poweron == True:
                             self.poweronInstance(region, getToken, poweron_id)
                          if pause == True:
                             self.pauseInstance(region, getToken, pause_id)
                          if unpause == True:
                             self.unpauseInstance(region, getToken, unpause_id)
                          if expire == True:
                             self.expireInstance(region, getToken, expire_id)
                          if shutdown == True:
                             self.shutdownInstance(region, getToken, shutdown_id)
                          if reset == True:
                             self.resetInstance(region, getToken, reset_id, status_id)
                          if changelease == True:
                             self.changeleaseInstance(region, getToken, changelease_id, extend_id, flag_id)
                          if property == True:
                             self.updateMeta(region, getToken, metadata_instance_id, meta_data)


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

        
    def destroyInstance(self,datacenter,auth,instance):
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

            prompt = '- Error: Unable to authenticate or validate the existing authorization token ' + ' for ' + username + ' at ' + time.strftime("%d/%m/%Y") + ' ' + time.strftime("%I:%M:%S") + '.'
            self.log(self.datacenter,username,prompt)
            print(prompt)
            return 1
        except(exceptions.Unauthorized): 

            self.progress()
            print ' [DONE]'
            print('\n')

            prompt = '- Error: Authentication failed due to invalid token ' + ' for ' + username + ' at ' + time.strftime("%d/%m/%Y") + " " + time.strftime("%I:%M:%S") + '.'
            self.log(self.datacenter,username,prompt)
            print(prompt)
            return 1

        try:
            servers = nova.servers.list(search_opts={'all_tenants': 1})
        except(exceptions.NotFound):
            
            self.progress()
            print ' [DONE]'
            print('\n')

            prompt = '- Error: Instance fetch failed for ' + username + ' at ' + time.strftime("%d/%m/%Y") + ' ' + time.strftime("%I:%M:%S") + '.'
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
                   instance_id   = s.id
                   instance_name = s.name
                   break
        except(IOError,IndexError,KeyError,NameError,OSError,RuntimeError,SyntaxError,IndentationError,TypeError,UnboundLocalError,ValueError):
            
            self.progress()
            print ' [DONE]'
            print('\n')

            fileToDelete = self.deleteInstanceRecord(self.datacenter,self.instance,username)
            if fileToDelete == False:
               prompt  = '- Info: Instance :' + self.instance + ' is already deleted or does not exists.'
               error   = '- Info: Destroy Instance :' + self.instance + ' failed for user ' + username + ' at ' + time.strftime("%d/%m/%Y") + ' ' + time.strftime("%I:%M:%S") + '.'
               self.log(self.datacenter,username,error)
               print(prompt)
               return 1

        try:
            destroy = nova.servers.delete(instance_id)
        except(IOError,IndexError,KeyError,NameError,OSError,RuntimeError,SyntaxError,IndentationError,TypeError,UnboundLocalError,ValueError):
            
            self.progress()
            print ' [DONE]'
            print('\n')

            fileToDelete = self.deleteInstanceRecord(self.datacenter,self.instance,username)
            if fileToDelete == False:
               prompt  = '- Info: Instance :' + self.instance + ' is already deleted or does not exists.'
               error   = '- Info: Destroy Instance :' + self.instance + ' failed for user ' + username + ' at ' + time.strftime("%d/%m/%Y") + ' ' + time.strftime("%I:%M:%S") + '.'
               self.log(self.datacenter,username,error)
               print(prompt)
               return 1
        except(exceptions.NotFound):
            
            self.progress()
            print ' [DONE]'
            print('\n')

            prompt = '- Error: Instance ' + str(self.instance) + ' could not be found ' + ' for ' + username + ' at ' + time.strftime("%d/%m/%Y") + ' ' + time.strftime("%I:%M:%S") + '.'
            self.log(self.datacenter,username,prompt)
            print(prompt)
            return 1

        self.progress()
        print ' [DONE]'
        print('\n')

        try:
            display = nova.servers.get(instance_id)
        except(exceptions.NotFound):
            
            prompt = '- Info: Instance ' + str(self.instance) + ' deletion successful for ' + username + ' at ' + time.strftime("%d/%m/%Y") + ' ' + time.strftime("%I:%M:%S") + '.'
            self.log(self.datacenter,username,prompt)
            print(prompt)
            print('\n')
            
            self.deleteInstanceRecord(self.datacenter,self.instance,username)

            return 0
        else:

            self.progress()
            print ' [DONE]'
            print('\n')

            if display:
               prompt =  '- Error: Instance ' + str(display.name) + ' deletion failed for ' + username + ' at ' + time.strftime("%d/%m/%Y") + ' ' + time.strftime("%I:%M:%S") + '.'
               self.log(self.datacenter,username,prompt)
               print(prompt)
               return 1



    def suspendInstance(self,datacenter,auth,instance):
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
                   instance_id   = s.id
                   instance_name = s.name
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
            instanceState = nova.servers.get(instance_id)
        except(exceptions.NotFound):

            self.progress()
            print ' [DONE]'
            print('\n')

            prompt = '- Error: Instance ' + str(self.instance) + ' could not be found for ' + username + ' at ' + time.strftime("%d/%m/%Y") + ' ' + time.strftime("%I:%M:%S") + '.'
            self.log(self.datacenter,username,prompt)
            print(prompt)
            return 1
        except(IOError,IndexError,KeyError,NameError,OSError,RuntimeError,SyntaxError,IndentationError,TypeError,UnboundLocalError,ValueError):

            self.progress()
            print ' [DONE]'
            print('\n')

            prompt = '- Error: Instance ' + str(self.instance) + ' could not be found for ' + username + ' at ' + time.strftime("%d/%m/%Y") + ' ' + time.strftime("%I:%M:%S") + '.'
            self.log(self.datacenter,username,prompt)
            print(prompt)
            return 1
        else:
            conflictMsg = instanceState.status
            conflictMsg = conflictMsg.upper()

        try:
            suspend = nova.servers.suspend(instance_id)
        except(exceptions.NotFound):

            self.progress()
            print ' [DONE]'
            print('\n')

            prompt = '- Error: Instance ' + str(self.instance) + ' could not be found to suspend for ' + username + ' at ' + time.strftime("%d/%m/%Y") + ' ' + time.strftime("%I:%M:%S") + '.'
            self.log(self.datacenter,username,prompt)
            print(prompt)
            return 1
        except(exceptions.Conflict):

            self.progress()
            print ' [DONE]'
            print('\n')

            prompt = '- Info: Instance ' + str(self.instance) + ' is in ' + str(conflictMsg) + ' state for ' + username + ' at ' + time.strftime("%d/%m/%Y") + ' ' + time.strftime("%I:%M:%S") + '.'
            self.log(self.datacenter,username,prompt)
            print(prompt)
            return 1

        self.progress()
        print ' [DONE]'
        print('\n')


        try:
            display = nova.servers.get(instance_id)
        except(exceptions.NotFound):

            self.progress()
            print ' [DONE]'
            print('\n')

            print '- Error: Instance ' + str(self.instance) + ' could not be found.'
            return 1
        else:
            for key, value in display.addresses.iteritems():
                for item in value:
                    for hay,stack in item.iteritems():
                        if hay == 'addr':
                           ip = stack

            userDisplay = PrettyTable(["ID", "INSTANCE NAME", "IP ADDRESS","STATUS"])
            userDisplay.align["ID"] = "l"
            userDisplay.align["INSTANCE NAME"] = "l"
            userDisplay.align["IP ADDRESS"] = "l"
            userDisplay.align["STATUS"] = "l"
            userDisplay.padding_width = 1

            userDisplay.add_row([display.id, display.name, ip, display.status])

            print(userDisplay)

            return 0



    def resumeInstance(self,datacenter,auth,instance):
        self.datacenter = datacenter
        self.auth       = auth
        self.instance   = instance
        displayCheck    = 0
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
                   instance_id   = s.id
                   instance_name = s.name
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
            instanceState = nova.servers.get(instance_id)
        except(IOError,IndexError,KeyError,NameError,OSError,RuntimeError,SyntaxError,IndentationError,TypeError,UnboundLocalError,ValueError):

            self.progress()
            print ' [DONE]'
            print('\n')

            prompt = '- Error: Instance ' + str(self.instance) + ' could not be found for ' + username + ' at ' + time.strftime("%d/%m/%Y") + ' ' + time.strftime("%I:%M:%S") + '.'
            self.log(self.datacenter,username,prompt)
            print(prompt)
            return 1
        except(exceptions.NotFound):

            self.progress()
            print ' [DONE]'
            print('\n')

            prompt = '- Error: Instance ' + str(self.instance) + ' could not be found for ' + username + ' at ' + time.strftime("%d/%m/%Y") + ' ' + time.strftime("%I:%M:%S") + '.'
            self.log(self.datacenter,username,prompt)
            print(prompt)
            return 1
        else:
            conflictMsg = instanceState.status
            conflictMsg = conflictMsg.upper()

        try:
            resume = nova.servers.resume(instance_id)
        except(exceptions.NotFound):

            self.progress()
            print ' [DONE]'
            print('\n')

            prompt = '- Error: Instance ' + str(self.instance) + ' could not be found for ' + username + ' at ' + time.strftime("%d/%m/%Y") + ' ' + time.strftime("%I:%M:%S") + '.'
            self.log(self.datacenter,username,prompt)
            print(prompt)
            return 1
        except(exceptions.Conflict):

            self.progress()
            print ' [DONE]'
            print('\n')

            prompt = '- Info: Instance ' + str(self.instance) + ' is in ' + str(conflictMsg) + ' state for ' + username + ' at ' + time.strftime("%d/%m/%Y") + ' ' + time.strftime("%I:%M:%S") + '.'
            self.log(self.datacenter,username,prompt)
            print(prompt)
            return 1

        self.progress()
        print ' [DONE]'
        print('\n')       

 
        try:
            display = nova.servers.get(instance_id)
        except(exceptions.NotFound):
        
            self.progress()
            print ' [DONE]'
            print('\n')

            prompt = '- Error: Instance ' + str(self.instance) + ' could not be found for ' + username + ' at ' + time.strftime("%d/%m/%Y") + ' ' + time.strftime("%I:%M:%S") + '.'
            self.log(self.datacenter,username,prompt)
            print(prompt)
            return 1
        else:
            if display.status == 'SHUTOFF':

               self.progress()
               print ' [DONE]'
               print('\n')


               try:
                  resume = nova.servers.start(instance_id)
               except(exceptions.NotFound):
               
                   self.progress()
                   print ' [DONE]'
                   print('\n')

                   prompt = '- Error: Instance ' + str(self.instance) + ' could not be found for ' + username + ' at ' + time.strftime("%d/%m/%Y") + ' ' + time.strftime("%I:%M:%S") + '.'
                   self.log(self.datacenter,username,prompt)
                   print(prompt)
                   return 1
               else:
                   try:
                       resumeDisplay = nova.servers.get(instance_id)
                       displayCheck = 1
                   except(exceptions.NotFound):
                   
                       self.progress()
                       print ' [DONE]'
                       print('\n')

                       prompt = '- Error: Instance ' + str(self.instance) + ' could not be found for ' + username + ' at ' + time.strftime("%d/%m/%Y") + ' ' + time.strftime("%I:%M:%S") + '.'
                       self.log(self.datacenter,username,prompt)
                       print(prompt)
                       return 1

                   if resumeDisplay.status == 'SHUTOFF':
                      prompt = '- Info: Instance ' + str(self.instance) + ' has expired, Extend the lease.'
                      self.log(self.datacenter,username,prompt)
                      print(prompt)
                      return 1

                   for key, value in resumeDisplay.addresses.iteritems():
                       for item in value:
                           for hay,stack in item.iteritems():
                               if hay == 'addr':
                                  ip_r = stack

            else:
                for key, value in display.addresses.iteritems():
                    for item in value:
                        for hay,stack in item.iteritems():
                            if hay == 'addr':
                               ip = stack

            userDisplay = PrettyTable(["ID", "INSTANCE NAME", "IP ADDRESS","STATUS","POWER STATE"])
            userDisplay.align["ID"] = "l"
            userDisplay.align["INSTANCE NAME"] = "l"
            userDisplay.align["IP ADDRESS"] = "l"
            userDisplay.align["STATUS"] = "l"
            userDisplay.align["POWER STATE"] = "l"            
            userDisplay.padding_width = 1

            powerState = 'SHUTOFF'

            if displayCheck == 0:
               userDisplay.add_row([display.id, display.name, ip, display.status, powerState])
            if displayCheck == 1:
               userDisplay.add_row([resumeDisplay.id, resumeDisplay.name, ip_r, resumeDisplay.status, powerState])

            print(userDisplay)

            return 0



    def rebootInstance(self,datacenter,auth,instance):
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
                   instance_id   = s.id
                   instance_name = s.name
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
            reboot = nova.servers.reboot(instance_id,reboot_type='HARD')

        except(IOError,IndexError,KeyError,NameError,OSError,RuntimeError,SyntaxError,IndentationError,TypeError,UnboundLocalError,ValueError):

            self.progress()
            print ' [DONE]'
            print('\n')

            prompt = '- Error: Instance ' + str(self.instance) + ' could not be found for ' + username + ' at ' + time.strftime("%d/%m/%Y") + ' ' + time.strftime("%I:%M:%S") + '.'
            self.log(self.datacenter,username,prompt)
            print(prompt)
            return 1

        except(exceptions.NotFound):

            self.progress()
            print ' [DONE]'
            print('\n')

            prompt = '- Error: Instance ' + str(self.instance) + ' could not be found for ' + username + ' at ' + time.strftime("%d/%m/%Y") + ' ' + time.strftime("%I:%M:%S") + '.'
            self.log(self.datacenter,username,prompt)
            print(prompt)
            return 1

        self.progress()
        print ' [DONE]'
        print('\n')


        try:
            display = nova.servers.get(instance_id)
        except(exceptions.NotFound):

            self.progress()
            print ' [DONE]'
            print('\n')

            prompt = '- Error: Instance ' + str(self.instance) + ' could not be found for ' + username + ' at ' + time.strftime("%d/%m/%Y") + ' ' + time.strftime("%I:%M:%S") + '.'
            self.log(self.datacenter,username,prompt)
            print(prompt)
            return 1
        else:
            for key, value in display.addresses.iteritems():
                for item in value:
                    for hay,stack in item.iteritems():
                        if hay == 'addr':
                           ip = stack

            userDisplay = PrettyTable(["ID", "INSTANCE NAME", "IP ADDRESS","STATUS"])
            userDisplay.align["ID"] = "l"
            userDisplay.align["INSTANCE NAME"] = "l"
            userDisplay.align["IP ADDRESS"] = "l"
            userDisplay.align["STATUS"] = "l"
            userDisplay.padding_width = 1

            userDisplay.add_row([display.id, display.name, ip, display.status])

            print(userDisplay)

            return 0



    def poweroffInstance(self,datacenter,auth,instance):
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
                   instance_id   = s.id
                   instance_name = s.name
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
            instanceState = nova.servers.get(instance_id)
        except(IOError,IndexError,KeyError,NameError,OSError,RuntimeError,SyntaxError,IndentationError,TypeError,UnboundLocalError,ValueError):

            self.progress()
            print ' [DONE]'
            print('\n')

            prompt = '- Error: Instance ' + str(self.instance) + ' could not be found for ' + username + ' at ' + time.strftime("%d/%m/%Y") + ' ' + time.strftime("%I:%M:%S") + '.'
            self.log(self.datacenter,username,prompt)
            print(prompt)
            return 1

        except(exceptions.NotFound):

            self.progress()
            print ' [DONE]'
            print('\n')

            prompt = '- Error: Instance ' + str(self.instance) + ' could not be found for ' + username + ' at ' + time.strftime("%d/%m/%Y") + ' ' + time.strftime("%I:%M:%S") + '.'
            self.log(self.datacenter,username,prompt)
            print(prompt)
            return 1
        else:
            conflictMsg = instanceState.status
            conflictMsg = conflictMsg.upper()

        try:
            poweroff = nova.servers.stop(instance_id)
        except(exceptions.NotFound):

            self.progress()
            print ' [DONE]'
            print('\n')

            prompt = '- Error: Instance ' + str(self.instance) + ' could not be found for ' + username + ' at ' + time.strftime("%d/%m/%Y") + ' ' + time.strftime("%I:%M:%S") + '.'
            self.log(self.datacenter,username,prompt)
            print(prompt)
            return 1
        except(exceptions.Conflict):

            self.progress()
            print ' [DONE]'
            print('\n')

            prompt = '- Info: Instance ' + str(self.instance) + ' is in ' + str(conflictMsg) + ' state for ' + username + ' at ' + time.strftime("%d/%m/%Y") + ' ' + time.strftime("%I:%M:%S") + '.'
            self.log(self.datacenter,username,prompt)
            print(prompt)
            return 1

        self.progress()
        print ' [DONE]'
        print('\n')

        try:
            display = nova.servers.get(instance_id)
        except(exceptions.NotFound):

            self.progress()
            print ' [DONE]'
            print('\n')

            prompt = '- Error: Instance ' + str(self.instance) + ' could not be found for ' + username + ' at ' + time.strftime("%d/%m/%Y") + ' ' + time.strftime("%I:%M:%S") + '.'
            self.log(self.datacenter,username,prompt)
            print(prompt)
            return 1
        else:
            for key, value in display.addresses.iteritems():
                for item in value:
                    for hay,stack in item.iteritems():
                        if hay == 'addr':
                           ip = stack

            userDisplay = PrettyTable(["ID", "INSTANCE NAME", "IP ADDRESS","STATUS"])
            userDisplay.align["ID"] = "l"
            userDisplay.align["INSTANCE NAME"] = "l"
            userDisplay.align["IP ADDRESS"] = "l"
            userDisplay.align["STATUS"] = "l"
            userDisplay.padding_width = 1

            userDisplay.add_row([display.id, display.name, ip, display.status])

            print(userDisplay)

            return 0



    def poweronInstance(self,datacenter,auth,instance):
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
                   instance_id   = s.id
                   instance_name = s.name
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
            instanceState = nova.servers.get(instance_id)
        except(IOError,IndexError,KeyError,NameError,OSError,RuntimeError,SyntaxError,IndentationError,TypeError,UnboundLocalError,ValueError):

            self.progress()
            print ' [DONE]'
            print('\n')

            prompt = '- Error: Instance ' + str(self.instance) + ' could not be found for ' + username + ' at ' + time.strftime("%d/%m/%Y") + ' ' + time.strftime("%I:%M:%S") + '.'
            self.log(self.datacenter,username,prompt)
            print(prompt)
            return 1

        except(exceptions.NotFound):

            self.progress()
            print ' [DONE]'
            print('\n')

            prompt = '- Error: Instance ' + str(self.instance) + ' could not be found for ' + username + ' at ' + time.strftime("%d/%m/%Y") + ' ' + time.strftime("%I:%M:%S") + '.'
            self.log(self.datacenter,username,prompt)
            print(prompt)
            return 1
        else:
            conflictMsg = instanceState.status
            conflictMsg = conflictMsg.upper()

        try:
            poweron = nova.servers.start(instance_id)
        except(exceptions.NotFound):

            self.progress()
            print ' [DONE]'
            print('\n')

            prompt = '- Error: Instance ' + str(self.instance) + ' could not be found for ' + username + ' at ' + time.strftime("%d/%m/%Y") + ' ' + time.strftime("%I:%M:%S") + '.'
            self.log(self.datacenter,username,prompt)
            print(prompt)
            return 1
        except(exceptions.Conflict):

            self.progress()
            print ' [DONE]'
            print('\n')

            prompt = '- Info: Instance ' + str(self.instance) + ' is in ' + str(conflictMsg) + ' state for ' + username + ' at ' + time.strftime("%d/%m/%Y") + ' ' + time.strftime("%I:%M:%S") + '.'
            self.log(self.datacenter,username,prompt)
            print(prompt)
            return 1

        self.progress()
        print ' [DONE]'
        print('\n')

        try:
            display = nova.servers.get(instance_id)
        except(exceptions.NotFound):

            self.progress()
            print ' [DONE]'
            print('\n')

            prompt = '- Instance ' + str(self.instance) + ' could not be found for ' + username + ' at ' + time.strftime("%d/%m/%Y") + ' ' + time.strftime("%I:%M:%S") + '.'
            self.log(self.datacenter,username,prompt)
            print(prompt)
            return 1
        else:
            if display.status == 'SHUTOFF':
               prompt = '- Instance ' + str(self.instance) + ' is Expired, Extend the Lease to POWER ON.'
               self.log(self.datacenter,username,prompt)
               print(prompt)
               return 1

            for key, value in display.addresses.iteritems():
                for item in value:
                    for hay,stack in item.iteritems():
                        if hay == 'addr':
                           ip = stack

            userDisplay = PrettyTable(["ID", "INSTANCE NAME", "IP ADDRESS","STATUS"])
            userDisplay.align["ID"] = "l"
            userDisplay.align["INSTANCE NAME"] = "l"
            userDisplay.align["IP ADDRESS"] = "l"
            userDisplay.align["STATUS"] = "l"
            userDisplay.padding_width = 1

            userDisplay.add_row([display.id, display.name, ip, display.status])

            print(userDisplay)

            return 0


    def pauseInstance(self,datacenter,auth,instance):
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
                   instance_id   = s.id
                   instance_name = s.name
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
            instanceState = nova.servers.get(instance_id)
        except(IOError,IndexError,KeyError,NameError,OSError,RuntimeError,SyntaxError,IndentationError,TypeError,UnboundLocalError,ValueError):

            self.progress()
            print ' [DONE]'
            print('\n')

            prompt = '- Error: Instance ' + str(self.instance) + ' could not be found for ' + username + ' at ' + time.strftime("%d/%m/%Y") + ' ' + time.strftime("%I:%M:%S") + '.'
            self.log(self.datacenter,username,prompt)
            print(prompt)
            return 1
        except(exceptions.NotFound):

            self.progress()
            print ' [DONE]'
            print('\n')

            prompt = '- Error: Instance ' + str(self.instance) + ' could not be found for ' + username + ' at ' + time.strftime("%d/%m/%Y") + ' ' + time.strftime("%I:%M:%S") + '.'
            self.log(self.datacenter,username,prompt)
            print(prompt)
            return 1
        else:
            conflictMsg = instanceState.status
            conflictMsg = conflictMsg.upper()


        try:
            pause = nova.servers.pause(instance_id)
        except(exceptions.NotFound):

            self.progress()
            print ' [DONE]'
            print('\n')

            prompt = '- Error: Instance ' + str(self.instance) + ' could not be found for ' + username + ' at ' + time.strftime("%d/%m/%Y") + ' ' + time.strftime("%I:%M:%S") + '.'
            self.log(self.datacenter,username,prompt)
            print(prompt)
            return 1
        except(exceptions.Conflict):

            self.progress()
            print ' [DONE]'
            print('\n')

            prompt = '- Info: Instance ' + str(self.instance) + ' is in ' + str(conflictMsg) + ' state for ' + username + ' at ' + time.strftime("%d/%m/%Y") + ' ' + time.strftime("%I:%M:%S") + '.'
            self.log(self.datacenter,username,prompt)
            print(prompt)
            return 1

        self.progress()
        print ' [DONE]'
        print('\n')

        try:
            display = nova.servers.get(instance_id)
        except(exceptions.NotFound):
        
            self.progress()
            print ' [DONE]'
            print('\n')

            prompt = '- Error: Instance ' + str(self.instance) + ' could not be found for ' + username + ' at ' + time.strftime("%d/%m/%Y") + ' ' + time.strftime("%I:%M:%S") + '.'
            self.log(self.datacenter,username,prompt)
            print(prompt)
            return 1
        else:
            for key, value in display.addresses.iteritems():
                for item in value:
                    for hay,stack in item.iteritems():
                        if hay == 'addr':
                           ip = stack

            userDisplay = PrettyTable(["ID", "INSTANCE NAME", "IP ADDRESS","STATUS"])
            userDisplay.align["ID"] = "l"
            userDisplay.align["INSTANCE NAME"] = "l"
            userDisplay.align["IP ADDRESS"] = "l"
            userDisplay.align["STATUS"] = "l"
            userDisplay.padding_width = 1

            userDisplay.add_row([display.id, display.name, ip, display.status])

            print(userDisplay)

            return 0


    def unpauseInstance(self,datacenter,auth,instance):
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
                   instance_id   = s.id
                   instance_name = s.name
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
            instanceState = nova.servers.get(instance_id)
        except(IOError,IndexError,KeyError,NameError,OSError,RuntimeError,SyntaxError,IndentationError,TypeError,UnboundLocalError,ValueError):        

            self.progress()
            print ' [DONE]'
            print('\n')

            prompt = '- Error: Instance ' + str(self.instance) + ' could not be found for ' + username + ' at ' + time.strftime("%d/%m/%Y") + ' ' + time.strftime("%I:%M:%S") + '.'
            self.log(self.datacenter,username,prompt)
            print(prompt)
            return 1
        except(exceptions.NotFound):

            self.progress()
            print ' [DONE]'
            print('\n')

            prompt = '- Error: Instance ' + str(self.instance) + ' could not be found for ' + username + ' at ' + time.strftime("%d/%m/%Y") + ' ' + time.strftime("%I:%M:%S") + '.'
            self.log(self.datacenter,username,prompt)
            print(prompt)
            return 1
        else:
            conflictMsg = instanceState.status
            conflictMsg = conflictMsg.upper()

        try:
            poweron = nova.servers.unpause(instance_id)
        except(exceptions.NotFound):
            
            self.progress()
            print ' [DONE]'
            print('\n')

            prompt = '- Error: Instance ' + str(self.instance) + ' could not be found for ' + username + ' at ' + time.strftime("%d/%m/%Y") + ' ' + time.strftime("%I:%M:%S") + '.'
            self.log(self.datacenter,username,prompt)
            print(prompt)
            return 1
        except(exceptions.Conflict):

            self.progress()
            print ' [DONE]'
            print('\n')

            prompt = '- Info: Instance ' + str(self.instance) + ' is in ' + str(conflictMsg) + ' state for ' + username + ' at ' + time.strftime("%d/%m/%Y") + ' ' + time.strftime("%I:%M:%S") + '.'
            self.log(self.datacenter,username,prompt)
            print(prompt)
            return 1
        
        self.progress()
        print ' [DONE]'
        print('\n')

        try:
            display = nova.servers.get(instance_id)
        except(exceptions.NotFound):

            self.progress()
            print ' [DONE]'
            print('\n')

            prompt = '- Error: Instance ' + str(self.instance) + ' could not be found for ' + username + ' at ' + time.strftime("%d/%m/%Y") + ' ' + time.strftime("%I:%M:%S") + '.'
            self.log(self.datacenter,username,prompt)
            print(prompt)
            return 1
        else:
            for key, value in display.addresses.iteritems():
                for item in value:
                    for hay,stack in item.iteritems():
                        if hay == 'addr':
                           ip = stack

            userDisplay = PrettyTable(["ID", "INSTANCE NAME", "IP ADDRESS","STATUS"])
            userDisplay.align["ID"] = "l"
            userDisplay.align["INSTANCE NAME"] = "l"
            userDisplay.align["IP ADDRESS"] = "l"
            userDisplay.align["STATUS"] = "l"
            userDisplay.padding_width = 1

            userDisplay.add_row([display.id, display.name, ip, display.status])

            print(userDisplay)

            return 0



    def shutdownInstance(self,datacenter,auth,instance):
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
        except(IOError,IndexError,KeyError,NameError,OSError,RuntimeError,SyntaxError,IndentationError,TypeError,UnboundLocalError,ValueError):

            self.progress()
            print ' [DONE]'
            print('\n')

            prompt = '- Error: Instance : ' + self.instance + ' could not be found for ' + username + ' at ' + time.strftime("%d/%m/%Y") + ' ' + time.strftime("%I:%M:%S") + '.'
            self.log(self.datacenter,username,prompt)
            print(prompt)
            return 1
        except(exceptions.NotFound):

            self.progress()
            print ' [DONE]'
            print('\n')

            prompt = '- Error: Instance : ' + self.instance + 'could not be found for ' + username + ' at ' + time.strftime("%d/%m/%Y") + ' ' + time.strftime("%I:%M:%S") + '.'
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
                   instance_id   = s.id
                   instance_name = s.name
                   break

        except(exceptions.NotFound):

            self.progress()
            print ' [DONE]'
            print('\n')

            prompt = '- Error: Instance : ' + self.instance + ' could not be found for ' + username + ' at ' + time.strftime("%d/%m/%Y") + ' ' + time.strftime("%I:%M:%S") + '.'
            self.log(self.datacenter,username,prompt)
            print(prompt)
            return 1


        try:
            instanceState = nova.servers.get(instance_id)
        except(IOError,IndexError,KeyError,NameError,OSError,RuntimeError,SyntaxError,IndentationError,TypeError,UnboundLocalError,ValueError):

            self.progress()
            print ' [DONE]'
            print('\n')

            prompt = '- Error: Instance : ' + str(self.instance) + ' could not be found for ' + username + ' at ' + time.strftime("%d/%m/%Y") + ' ' + time.strftime("%I:%M:%S") + '.'
            self.log(self.datacenter,username,prompt)
            print(prompt)
            return 1

        except(exceptions.NotFound):

            self.progress()
            print ' [DONE]'
            print('\n')

            prompt = '- Error: Instance : ' + str(self.instance) + ' could not be found for ' + username + ' at ' + time.strftime("%d/%m/%Y") + ' ' + time.strftime("%I:%M:%S") + '.'
            self.log(self.datacenter,username,prompt)
            print(prompt)
            return 1
        else:
            conflictMsg = instanceState.status
            conflictMsg = conflictMsg.upper()

        try:
            shutdown = nova.servers.stop(instance_id)
        except(exceptions.NotFound):

            self.progress()
            print ' [DONE]'
            print('\n')

            prompt = '- Error: Instance : ' + str(self.instance) + ' could not be found for ' + username + ' at ' + time.strftime("%d/%m/%Y") + ' ' + time.strftime("%I:%M:%S") + '.'
            self.log(self.datacenter,username,prompt)
            print(prompt)
            return 1
        except(exceptions.Conflict):

            self.progress()
            print ' [DONE]'
            print('\n')

            prompt = '- Info: Instance : ' + str(self.instance) + ' is in ' + str(conflictMsg) + ' state for ' + username + ' at ' + time.strftime("%d/%m/%Y") + ' ' + time.strftime("%I:%M:%S") + '.'
            self.log(self.datacenter,username,prompt)
            print(prompt)
            return 1

        self.progress()
        print ' [DONE]'
        print('\n')

        try:
            display = nova.servers.get(instance_id)
        except(exceptions.NotFound):

            self.progress()
            print ' [DONE]'
            print('\n')

            prompt = '- Error: Instance : ' + str(self.instance) + ' could not be found for ' + username + ' at ' + time.strftime("%d/%m/%Y") + ' ' + time.strftime("%I:%M:%S") + '.'
            self.log(self.datacenter,username,prompt)
            print(prompt)
            return 1
        else:
            for key, value in display.addresses.iteritems():
                for item in value:
                    for hay,stack in item.iteritems():
                        if hay == 'addr':
                           ip = stack


            userDisplay = PrettyTable(["ID", "INSTANCE NAME", "IP ADDRESS","STATUS"])
            userDisplay.align["ID"] = "l"
            userDisplay.align["INSTANCE NAME"] = "l"
            userDisplay.align["IP ADDRESS"] = "l"
            userDisplay.align["STATUS"] = "l"
            userDisplay.padding_width = 1

            userDisplay.add_row([display.id, display.name, ip, display.status])

            print(userDisplay)

            return 0



    def resetInstance(self,datacenter,auth,instance,status):
        self.datacenter = datacenter
        self.auth       = auth
        self.instance   = instance
        self.status     = status
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
        except(IOError,IndexError,KeyError,NameError,OSError,RuntimeError,SyntaxError,IndentationError,TypeError,UnboundLocalError,ValueError):

            self.progress()
            print ' [DONE]'
            print('\n')

            prompt = '- Error: Instance could not be found for ' + username + ' at ' + time.strftime("%d/%m/%Y") + ' ' + time.strftime("%I:%M:%S") + '.'
            self.log(self.datacenter,username,prompt)
            print(prompt)
            return 1

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
                   instance_id   = s.id
                   instance_name = s.name
                   break

        except(IOError,IndexError,KeyError,NameError,OSError,RuntimeError,SyntaxError,IndentationError,TypeError,UnboundLocalError,ValueError):

            self.progress()
            print ' [DONE]'
            print('\n')

            prompt = '- Error: Instance could not be found for ' + username + ' at ' + time.strftime("%d/%m/%Y") + ' ' + time.strftime("%I:%M:%S") + '.'
            self.log(self.datacenter,username,prompt)
            print(prompt)
            return 1

        except(exceptions.NotFound):

            self.progress()
            print ' [DONE]'
            print('\n')

            prompt = '- Error: Instance could not be found for ' + username + ' at ' + time.strftime("%d/%m/%Y") + ' ' + time.strftime("%I:%M:%S") + '.'
            self.log(self.datacenter,username,prompt)
            print(prompt)
            return 1


        try:
            instanceState = nova.servers.get(instance_id)
            conflictMsg   = instanceState.status
            conflictMsg   = conflictMsg.lower()
            if conflictMsg == self.status:

               self.progress()
               print ' [DONE]'
               print('\n')

               prompt = '- Info: Instance ' + str(self.instance) + ' is in ' + str(conflictMsg.upper()) + ' state for ' + username + ' at ' + time.strftime("%d/%m/%Y") + ' ' + time.strftime("%I:%M:%S") + '.'
               self.log(self.datacenter,username,prompt)
               print(prompt)
               return 1
        except(IOError,IndexError,KeyError,NameError,OSError,RuntimeError,SyntaxError,IndentationError,TypeError,UnboundLocalError,ValueError):

            self.progress()
            print ' [DONE]'
            print('\n')

            prompt = '- Error: Instance ' + str(self.instance) + ' could not be found for ' + username + ' at ' + time.strftime("%d/%m/%Y") + ' ' + time.strftime("%I:%M:%S") + '.'
            self.log(self.datacenter,username,prompt)
            print(prompt)
            return 1
               
        except(exceptions.NotFound):

            self.progress()
            print ' [DONE]'
            print('\n')

            prompt = '- Error: Instance ' + str(self.instance) + ' could not be found for ' + username + ' at ' + time.strftime("%d/%m/%Y") + ' ' + time.strftime("%I:%M:%S") + '.'
            self.log(self.datacenter,username,prompt)  
            print(prompt)
            return 1

        try:
            nova.servers.reset_state(instance_id,state=self.status)
        except(exceptions.NotFound):

            self.progress()
            print ' [DONE]'
            print('\n')

            prompt = '- Error: Instance ' + str(self.instance) + ' could not be found for ' + username + ' at ' + time.strftime("%d/%m/%Y") + ' ' + time.strftime("%I:%M:%S") + '.'
            self.log(self.datacenter,username,prompt)
            print(prompt)
            return 1

        except(exceptions.Conflict):

            self.progress()
            print ' [DONE]'
            print('\n')

            prompt = '- Error: Instance ' + str(self.instance) + ' is in ' + str(conflictMsg.upper()) + ' state for ' + username + ' at ' + time.strftime("%d/%m/%Y") + ' ' + time.strftime("%I:%M:%S") + '.'
            self.log(self.datacenter,username,prompt)
            print(prompt)
            return 1

        except(exceptions.BadRequest):

            self.progress()
            print ' [DONE]'
            print('\n')

            prompt = '- Error: Instance : ' + str(self.instance) + ' cannot be set to [' + str(self.status) + '] State. Valid states are (active | error).'
            self.log(self.datacenter,username,prompt)
            print(prompt)
            return 1



        self.progress()
        print ' [DONE]'
        print('\n')

        try:
            display = nova.servers.get(instance_id)
        except(exceptions.NotFound):

            self.progress()
            print ' [DONE]'
            print('\n')

            prompt = '- Error: Instance ' + str(self.instance) + ' could not be found for ' + username + ' at ' + time.strftime("%d/%m/%Y") + ' ' + time.strftime("%I:%M:%S") + '.'
            self.log(self.datacenter,username,prompt)
            return 1
        else:
            for key, value in display.addresses.iteritems():
                for item in value:
                    for hay,stack in item.iteritems():
                        if hay == 'addr':
                           ip = stack

            userDisplay = PrettyTable(["ID", "INSTANCE NAME", "IP ADDRESS","STATUS"])
            userDisplay.align["ID"] = "l"
            userDisplay.align["INSTANCE NAME"] = "l"
            userDisplay.align["IP ADDRESS"] = "l"
            userDisplay.align["STATUS"] = "l"
            userDisplay.padding_width = 1

            userDisplay.add_row([display.id, display.name, ip, display.status])

            print(userDisplay)

            return 0
               


    def expireInstance(self,datacenter,auth,instance):
        self.datacenter = datacenter
        self.auth       = auth
        self.instance   = instance
        lease           = 0
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
            self.log(username,prompt)
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
        except(IOError,IndexError,KeyError,NameError,OSError,RuntimeError,SyntaxError,IndentationError,TypeError,UnboundLocalError,ValueError):

            self.progress()
            print ' [DONE]'
            print('\n')

            prompt = '- Error: Instance :' + self.instance + ' could not be found for ' + username + ' at ' + time.strftime("%d/%m/%Y") + ' ' + time.strftime("%I:%M:%S") + '.'
            self.log(self.datacenter,username,prompt)
            print(prompt)
            return 1

        except(exceptions.NotFound):

            self.progress()
            print ' [DONE]'
            print('\n')

            prompt = '- Error: Instance :' + self.instance + ' could not be found for ' + username + ' at ' + time.strftime("%d/%m/%Y") + ' ' + time.strftime("%I:%M:%S") + '.'
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
                   instance_id   = s.id
                   instance_name = s.name
                   break

        except(exceptions.NotFound):

            self.progress()
            print ' [DONE]'
            print('\n')

            prompt = '- Error: Instance ' + self.instance + ' could not be found for ' + username + ' at ' + time.strftime("%d/%m/%Y") + ' ' + time.strftime("%I:%M:%S") + '.'
            self.log(self.datacenter,username,prompt)
            print(prompt)
            return 1


        try:
            instanceState = nova.servers.get(instance_id)
        except(IOError,IndexError,KeyError,NameError,OSError,RuntimeError,SyntaxError,IndentationError,TypeError,UnboundLocalError,ValueError):

            self.progress()
            print ' [DONE]'
            print('\n')

            prompt = '- Error: Instance ' + str(self.instance) + ' could not be found for ' + username + ' at ' + time.strftime("%d/%m/%Y") + ' ' + time.strftime("%I:%M:%S") + '.'
            self.log(self.datacenter,username,prompt)
            print(prompt)
            return 1

        except(exceptions.NotFound):

            self.progress()
            print ' [DONE]'
            print('\n')

            prompt = '- Error: Instance ' + str(self.instance) + ' could not be found for ' + username + ' at ' + time.strftime("%d/%m/%Y") + ' ' + time.strftime("%I:%M:%S") + '.'
            self.log(self.datacenter,username,prompt)
            print(prompt)
            return 1
        else:
            for k,v in instanceState.flavor.items():
                if k == 'id':
                   flavor_id = v
            try:
                getFlavor = nova.flavors.get(flavor_id)
                find      = '<Flavor:'
                replace   = ''
                flavor = re.sub(find, replace, str(getFlavor))
                flavor = re.sub('>','',str(flavor))
                flavor = flavor.strip()
            except(exceptions.NotFound):

                self.progress()
                print ' [DONE]'
                print('\n')

                prompt = '- Error: Flavor ' + str(flavor_id) + ' could not be found for ' + username + ' at ' + time.strftime("%d/%m/%Y") + ' ' + time.strftime("%I:%M:%S") + '.'
                self.log(self.datacenter,username,prompt)
                print(prompt)
                return 1
            else:
                createObj = create.Create(Base)
                response  = createObj.expireNotify(username,instanceState.name,lease,flavor)           
                if response == 'Success':

                   self.progress()
                   print ' [DONE]'
                   print('\n')

                   prompt = '- Info: Instance Expire request submitted for ' + str(self.instance) + ' for ' + username + ' at ' + time.strftime("%d/%m/%Y") + ' ' + time.strftime("%I:%M:%S") + '.'
                   self.log(self.datacenter,username,prompt)
                   print(prompt)
                   print('\n')
                   return 0
                else:

                    self.progress()
                    print ' [DONE]'
                    print('\n')

                    prompt = '- Error: Instance Expire request submission failed for ' + str(self.instance) + ' for ' + username + ' at ' + time.strftime("%d/%m/%Y") + ' ' + time.strftime("%I:%M:%S") + '.'
                    self.log(self.datacenter,username,prompt)
                    print(prompt)
                    print('\n')
                    return 1
                   

    def changeleaseInstance(self,datacenter,auth,instance,lease,flag):
        self.datacenter = datacenter
        self.auth       = auth
        self.instance   = instance
        self.lease      = lease
        self.flag       = flag
        current_dir     = os.environ["HOME"]       
        change          = ('d','h')

        try:
            if not int(self.lease):
               print '- Error: Lease ' + str(self.lease) + ' should be an Integer. Please try again.'
               return 1
        except(ValueError):
            print '- Error: Lease [' + str(self.lease) + '] is not an Integer. Please try again.'
            return 1

        try:
            if self.flag.strip() not in change:
               print '- Error: Flag [' + str(self.flag) + '] should be either [d | h]. Please try again.'
               return 1
        except(ValueError):
            print '- Error: Flag ' + str(self.flag) + ' should be either [d | h]. Please try again.'
            return 1


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
        except(IOError,IndexError,KeyError,NameError,OSError,RuntimeError,SyntaxError,IndentationError,TypeError,UnboundLocalError,ValueError):

            self.progress()
            print ' [DONE]'
            print('\n')

            prompt = '- Error: Instance :' + self.instance + ' could not be found for ' + username + ' at ' + time.strftime("%d/%m/%Y") + ' ' + time.strftime("%I:%M:%S") + '.'
            self.log(self.datacenter,username,prompt)
            print(prompt)
            return 1

        except(exceptions.NotFound):

            self.progress()
            print ' [DONE]'
            print('\n')

            prompt = '- Error: Instance :' + self.instance + ' could not be found for ' + username + ' at ' + time.strftime("%d/%m/%Y") + ' ' + time.strftime("%I:%M:%S") + '.'
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
                   instance_id   = s.id
                   instance_name = s.name
                   break

        except(exceptions.NotFound):

            self.progress()
            print ' [DONE]'
            print('\n')

            prompt = '- Error: Instance :' + self.instance + ' could not be found for ' + username + ' at ' + time.strftime("%d/%m/%Y") + ' ' + time.strftime("%I:%M:%S") + '.'
            self.log(self.datacenter,username,prompt)
            print(prompt)
            return 1


        try:
            instanceState = nova.servers.get(instance_id)
        except(IOError,IndexError,KeyError,NameError,OSError,RuntimeError,SyntaxError,IndentationError,TypeError,UnboundLocalError,ValueError):

            self.progress()
            print ' [DONE]'
            print('\n')

            prompt = '- Error: Instance ' + str(self.instance) + ' could not be found for ' + username + ' at ' + time.strftime("%d/%m/%Y") + ' ' + time.strftime("%I:%M:%S") + '.'
            self.log(self.datacenter,username,prompt)
            print(prompt)
            return 1

        except(exceptions.NotFound):

            self.progress()
            print ' [DONE]'
            print('\n')

            prompt = '- Error: Instance ' + str(self.instance) + ' could not be found for ' + username + ' at ' + time.strftime("%d/%m/%Y") + ' ' + time.strftime("%I:%M:%S") + '.'
            self.log(self.datacenter,username,prompt)
            print(prompt)
            return 1
        else:
            for k,v in instanceState.flavor.items():
                if k == 'id':
                   flavor_id = v
            try:
                getFlavor = nova.flavors.get(flavor_id)
                find      = '<Flavor:'
                replace   = ''
                flavor = re.sub(find, replace, str(getFlavor))
                flavor = re.sub('>','',str(flavor))
                flavor = flavor.strip()
            except(exceptions.NotFound):

                self.progress()
                print ' [DONE]'
                print('\n')

                prompt = '- Error: Flavor ' + str(flavor_id) + ' could not be found for ' + username + ' at ' + time.strftime("%d/%m/%Y") + ' ' + time.strftime("%I:%M:%S") + '.'
                self.log(self.datacenter,username,prompt)
                print(prompt)
                return 1
            else:
                createObj = create.Create(Base)
                response  = createObj.changeLeaseNotify(username,instanceState.name,self.lease,self.flag,flavor)
                if response == 'Success':

                   self.progress()
                   print ' [DONE]'
                   print('\n')

                   prompt = '- Info: Lease change request submitted for Instance : ' + str(self.instance) + ' for ' + username + ' at ' + time.strftime("%d/%m/%Y") + ' ' + time.strftime("%I:%M:%S") + '.'
                   self.log(self.datacenter,username,prompt)
                   print(prompt)
                   print('\n')
                   return 0
                else:

                    self.progress()
                    print ' [DONE]'
                    print('\n')

                    prompt = '- Error: Lease change request failed for Instance : ' + str(self.instance) + ' for ' + username + ' at ' + time.strftime("%d/%m/%Y") + ' ' + time.strftime("%I:%M:%S") + '.'
                    self.log(self.datacenter,username,prompt)
                    print(prompt)
                    print('\n')
                    return 1



    def deleteInstanceRecord(self,datacenter,instance,username):
        self.datacenter = datacenter
        self.instance   = instance
        self.user       = username
        createFiles     = []
        create          = 0

        self.user = self.user.lower()

        chk  = self.user.find('@')
        if chk != -1:
           storeusername = self.user.split('@')
           uname = storeusername[0]
        if chk == -1:
           uname = self.user


        try:
            current_dir = os.environ["HOME"] 
            for file in os.listdir(current_dir + "/" + '.' + self.datacenter + "/" + '.' + uname):
                if file.endswith(".create"):
                   createFiles.insert(create,file)
                   create = create + 1

            for c in createFiles:
                fileSize = os.stat(current_dir + "/" + '.' + self.datacenter + "/" + '.' + uname + "/" + c).st_size != 0
                if fileSize:
                   with open(current_dir + "/" + '.' + self.datacenter + "/" + '.' + uname + "/" + c, 'r') as f:
                      data = load(f)

                      k = 0
                      for item in data:
                          for key, value in item.items():
                              if key == 'name' and value == self.instance:
                                 filename = c
                                 break
            filename = current_dir + "/" + '.' + self.datacenter + "/" + '.' + uname + "/" + filename
        except(IOError,IndexError,KeyError,NameError,OSError,RuntimeError,SyntaxError,IndentationError,TypeError,UnboundLocalError,ValueError):
            return False
        if filename:
            os.remove(filename)
            return False


    def updateMeta(self,datacenter,auth,instance,metadata_str):
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
                    instance_id   = s.id
                    instance_name = s.name
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
            instanceState = nova.servers.get(instance_id)
        except(exceptions.NotFound):

            self.progress()
            print ' [DONE]'
            print('\n')

            prompt = '- Error: Instance ' + str(self.instance) + ' could not be found for ' + username + ' at ' + time.strftime("%d/%m/%Y") + ' ' + time.strftime("%I:%M:%S") + '.'
            self.log(self.datacenter,username,prompt)
            print(prompt)
            return 1
        except(IOError,IndexError,KeyError,NameError,OSError,RuntimeError,SyntaxError,IndentationError,TypeError,UnboundLocalError,ValueError):

            self.progress()
            print ' [DONE]'
            print('\n')

            prompt = '- Error: Instance ' + str(self.instance) + ' could not be found for ' + username + ' at ' + time.strftime("%d/%m/%Y") + ' ' + time.strftime("%I:%M:%S") + '.'
            self.log(self.datacenter,username,prompt)
            print(prompt)
            return 1
        else:
            conflictMsg = instanceState.status
            conflictMsg = conflictMsg.upper()

        try:
            meta_data = dict()
            for kvp in metadata_str.split(','):
                (k, v) = kvp.split('=')
                meta_data[k] = v
            set_meta = nova.servers.set_meta(instance_id, meta_data)

        except(exceptions.NotFound):
            self.progress()
            print ' [DONE]'
            print('\n')

            prompt = '- Error: Instance ' + str(self.instance) + ' could not be found to set meta data for ' + username + ' at ' + time.strftime("%d/%m/%Y") + ' ' + time.strftime("%I:%M:%S") + '.'
            self.log(self.datacenter,username,prompt)
            print(prompt)
            return 1
        except(exceptions.Conflict):

            self.progress()
            print ' [DONE]'
            print('\n')

            prompt = '- Info: Instance ' + str(self.instance) + ' is in ' + str(conflictMsg) + ' state for ' + username + ' at ' + time.strftime("%d/%m/%Y") + ' ' + time.strftime("%I:%M:%S") + '.'
            self.log(self.datacenter,username,prompt)
            print(prompt)
            return 1

        self.progress()
        print ' [DONE]'
        print('\n')


        try:
            display = nova.servers.get(instance_id)
        except(exceptions.NotFound):

            self.progress()
            print ' [DONE]'
            print('\n')

            print '- Error: Instance ' + str(self.instance) + ' could not be found.'
            return 1
        else:
            for key, value in display.addresses.iteritems():
                for item in value:
                    for hay,stack in item.iteritems():
                        if hay == 'addr':
                            ip = stack

            userDisplay = PrettyTable(["ID", "INSTANCE NAME", "IP ADDRESS","STATUS"])
            userDisplay.align["ID"] = "l"
            userDisplay.align["INSTANCE NAME"] = "l"
            userDisplay.align["IP ADDRESS"] = "l"
            userDisplay.align["STATUS"] = "l"
            userDisplay.padding_width = 1

            userDisplay.add_row([display.id, display.name, ip, display.status])

            print(userDisplay)

            return 0


    def timer(self,datacenter,username):
        self.datacenter = datacenter
        self.username   = username
        current_dir     = os.environ["HOME"]
        self.username   = self.username.lower()

        chk = self.username.find('@')

        if chk != -1:
           storeusername = self.username.split('@')
           uname = storeusername[0]
        if chk == -1:
           uname = self.username

        path    = current_dir + "/" + '.' + self.datacenter + "/" + '.' + uname + "/" + '.' + uname
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

               working_dir = current_dir + "/" + '.' + self.datacenter + "/" + '.' + uname

               log = current_dir + "/" + '.' + self.datacenter + "/" + '.' + uname +"/" + '.' + uname + '.log'

               if not os.path.exists(log):
                  return False

               os.chdir(working_dir)

               logFile = '.' + uname + '.log'

               mvFile = logFile + '.' + time.strftime("%d-%m-%Y") + "-" + time.strftime("%I:%M:%S")

               os.rename(logFile,mvFile)

               return False
            else:
                return True

   
    def progress(self):
        print '\b',
        sys.stdout.flush()
        time.sleep(10)

 
    def log(self,datacenter,username,prompt):
        self.datacenter = datacenter
        self.username   = username
        self.prompt     = prompt
        current_dir     = os.environ["HOME"]
        self.username   = self.username.lower()

        chk = self.username.find('@')
        if chk != -1:
           storeusername = self.username.split('@')
           uname = storeusername[0]
        if chk == -1:
           uname = self.username

        log = open(current_dir + "/" + '.' + self.datacenter + "/" + '.' + uname +"/" + '.' + uname + '.log','a')
        log.write(self.prompt + '\n')

        log.close()
