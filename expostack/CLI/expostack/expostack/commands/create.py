"""The create command."""

import warnings

warnings.filterwarnings("ignore")

import os

import re

import sys

import math

import time

import getpass

from random import randint

import smtplib

import socket

import datetime

from email.mime.multipart import MIMEMultipart

from email.mime.text import MIMEText

from email.mime.image import MIMEImage

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

import io

os.environ['http_proxy'] = ''

os.environ['https_proxy'] = ''

class Create(Base):
    """Create the virtual Instance or Instances"""


    def run(self):
        inputList   = {}
        cacheFiles  = []
        voltype     = ['Tier1-Prod-ISCSI-Storage','Tier1-Dev-ISCSI-Storage']	
        region      = ''
        search      = False 
        i           = 0

        values = self.options
        for key, value in values.iteritems():
            if key == '--region':
               region = value.upper()
               if region not in ('SCL1','LA1'):
                  search = True
                  break 
               else:
                   inputList.update({'region': value})

            if key == '--name':
               if value[0] == 'v' and value[1] == 'i':
                  instanceName  = value
               else:
                   instanceName = 'vi' + value

               inputList.update({'instanceName': instanceName})


            if key == '--instances':
               inputList.update({'instances': value})
            if key == '--tag':
               inputList.update({'tag': value})
            if key == '--flavor':
               inputList.update({'flavor': value})
            if key == '--catalog':
               inputList.update({'image': value})
            if key == '--lease':
               inputList.update({'lease': value})
            if key == '--property':
               inputList.update({'property': value})
            if key == '--user-data':
               inputList.update({'user-data': value})
            if key == '-boot-volume':
               inputList.update({'boot-volume': value})
            if key == '--vol-name':
               inputList.update({'vol-name': value})
            if key == '--vol-type':
               inputList.update({'vol-type': value})
            if key == '--size':
               inputList.update({'size': value})

        if search == True:
           print('- Error: Region Name doesn\'t exists, Please try again!')
           return 1

        validateName = self.existencyCheck(instanceName)
        validateVolName = self.existencyCheck(volumeName)

        if not validateName:
           print('Error: --name should only contain [a-z][A-Z][0-9][-]')
           sys.exit()

        if not validateVolName:
           print('Error: --vol-name should only contain [a-z][A-Z][0-9][-]')
           sys.exit()

        if not int(inputList['instances']):
           print('Error: --instances should be an integer. Please try again.')
           sys.exit()

        if not int(inputList['size']):
           print('Error: --size should be an integer. Please try again.')
           sys.exit()

        if not int(inputList['lease']):
           print('Error: --lease should be an integer. Please try again.')
           sys.exit()

        if inputList['lease'] == 0:
           print('Error: --lease should be > 0. Please try again.')
           sys.exit()

        if len(inputList['lease']) > 60:
           print('Error: --lease should be <= 60. Please try again')
           sys.exit()

	if inputList['vol-type-name'] not in volname:
	   print ('Error: --vol-type-name has wrong values')
           sys.exit()


        restrict_users = ('sysadmin', 'root')

        ldap_user = getpass.getuser()

        if ldap_user in restrict_users:
           print("- Error: Login using LDAP username/password only.")
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
                      self.createInstance(region,singleRecord,**inputList)
               else:
                   while True:
                       srNo = raw_input('Please enter the NO. of your username:')
                       getNo = self.processNumber(srNo,records)
                       if isinstance(getNo, dict):
                          serial = True
                          break;
                   if serial == True:
                      getToken = getNo

                      timeout = self.timer(region,getToken['username'])
                      if timeout == False:
                         print '- Error: Your session timed out, Please login again.'
                         sys.exit()
                      else:
                          self.createInstance(region,getToken,**inputList)        


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
        

    def createInstance(self,datacenter,auth,**command):
        self.auth       = auth
        self.datacenter = datacenter 
        self.command    = command
        current_dir     = os.environ["HOME"]

        property_dict = None
        user_data = None

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

            prompt = "- Error: Unable to authenticate or validate the existing authorization token for user: " + username + " at " + time.strftime("%d/%m/%Y") + " " + time.strftime("%I:%M:%S") + '.'
            self.log(self.datacenter,username,prompt)
            print(prompt)
            return 1

        except(exceptions.Unauthorized): 
            
            self.progress()
            print ' [DONE]'
            print('\n')

            prompt = "- Error: Authentication failed due to invalid token for user: " + username + " at " + time.strftime("%d/%m/%Y") + " " + time.strftime("%I:%M:%S") + '.'
            self.log(self.datacenter,username,prompt)
            print(prompt)
            return 1

        for hay, stack in self.command.iteritems():
            if hay == 'instanceName':
               instanceName = stack
            if hay == 'instances':
               instance     = stack
            if hay == 'tag':
               tag          = stack
            if hay == 'flavor':
               flv          = stack
            if hay == 'image':
               image        = stack
            if hay == 'lease':
               lease        = stack
            if hay == 'user-data':
               user_data_file = stack
            if hay == 'property':
               property = stack


        if property:
            property_dict = dict()
            # assume kvp's separated by ,
            for kvp in property.split(','):
                (k, v) = kvp.split('=')
                property_dict[k] = v

        if instance > 1:
           min_count = 1
           max_count = instance

        if instance == 1:
           min_count = 1
           max_count = 1


        try:
           servers = nova.servers.list(search_opts={'all_tenants': 1})
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


        find         = '<Server:'
        replace      = ''
        listServer   = []
        createFiles  = []
        create       = 0
        ser          = 0
        exists       = False
        myFile       = ''
        p            = 0
        processNodes = []
        hyfen        = []
        current_dir = os.environ["HOME"]       
 
        chk = username.find('@')
        
        if chk != -1:
           storeusername = username.split('@')
           uname = storeusername[0]
        if chk == -1:
           uname = username 


        try:
            for server in servers:
                host = re.sub(find, replace, str(server))
                host = re.sub('>','',str(host))
                listServer.insert(ser,host)
                ser = ser + 1

            findNode = instanceName.strip()
            findNode = findNode[2:]

            userDisplay = PrettyTable(["S.NO","INSTANCE NAME"])
            userDisplay.align["S.NO"] = "m"
            userDisplay.align["INSTANCE NAME"] = "m"
            userDisplay.padding_width = 20

            id_inst = 1
            for node in listServer:
                v = node.rfind('-')
                if v != -1:
                   verifyNode = node[:v]
                   verifyNode = verifyNode[3:]
                   if verifyNode.strip() == findNode:
                      userDisplay.add_row([id_inst,node])
                      hyfen.append(node)
                      id_inst = id_inst + 1

            if len(hyfen) > 0:
               print ' [DONE]'

               print('\n')
               print("- Info: Instances with the same name exists, please try again.")
               print(userDisplay)
               print('\n')
               return False

        except(IOError,IndexError,KeyError,NameError,OSError,RuntimeError,SyntaxError,IndentationError,TypeError,UnboundLocalError,ValueError):

            prompt = "- Error: Instances could not be found for user: " + username + " at " + time.strftime("%d/%m/%Y") + " " + time.strftime("%I:%M:%S") + '.'
            self.log(self.datacenter,username,prompt)
            return 1


        try:
            img  = nova.images.find(name=image)
        except(exceptions.NotFound):

            self.progress()
            print ' [DONE]'
            print('\n')

            prompt = "- Error: Image : " + image + " could not be found for user: " + username + " at " + time.strftime("%d/%m/%Y") + " " + time.strftime("%I:%M:%S") + '.'
            self.log(self.datacenter,username,prompt)
            print(prompt)
            return 1

        try:
            fl   = nova.flavors.find(name=flv)
        except(exceptions.NotFound):

            self.progress()
            print ' [DONE]'
            print('\n')

            prompt = "- Error: Flavor : " + flv + " could not be found for user: " + username + " at " + time.strftime("%d/%m/%Y") + " " + time.strftime("%I:%M:%S") + '.'
            self.log(self.datacenter,username,prompt)
            print(prompt)
            return 1

        try:
            nets  = nova.networks.list()
        except(exceptions.NotFound):

            self.progress()
            print ' [DONE]'
            print('\n')

            prompt = "- Error: Network : " + nic + " could not be found for user: " + username + " at " + time.strftime("%d/%m/%Y") + " " + time.strftime("%I:%M:%S") + '.'
            self.log(self.datacenter,username,prompt)
            print(prompt)
            return 1

        nics = list()
        # find nic to apply
        # [XXX] find a way to do it automatically
        itprojects = ['ITOps', 'IT LAB']
        if project_name in itprojects:
            pseudo_project_name = 'Dev'
        else:
            pseudo_project_name = project_name

        for net in nets:
            proj = net.label.split('-')[0]
            if proj.lower() in pseudo_project_name.lower():
                nics = [{'net-id': net.id}]

        if user_data_file:
            try:
                user_data = io.open(user_data_file)
            except IOError:
                self.progress()
                print ' [DONE]'
                print('\n')

                prompt = '- Error: Login into Region: ' + self.datacenter + ' to perform this Operation.'
                self.log(self.datacenter,username,prompt)
                print(prompt)
                return 1
        try:
            initialize = nova.servers.create(name=instanceName, image=img,
                                             flavor=fl, min_count=min_count,
                                             max_count=max_count, nics=nics,
                                             userdata=user_data,
                                             meta=property_dict)
            if hasattr(user_data, 'close'):
                user_data.close()

        except(exceptions.Unauthorized):
            self.progress()
            print ' [DONE]'
            print('\n')

            prompt = "- Error: Access denied, Please provide valid credentials for user: " + username + " at " + time.strftime("%d/%m/%Y") + " " + time.strftime("%I:%M:%S") + '.'
            self.log(self.datacenter,username,prompt)
            print(prompt)
            return 1
        except(exceptions.BadRequest):

            self.progress()
            print ' [DONE]'
            print('\n')

            prompt = "- Error: Supplied data is Invalid for user: " + username + " at " + time.strftime("%d/%m/%Y") + " " + time.strftime("%I:%M:%S") + '.'
            self.log(self.datacenter,username,prompt)
            print(prompt)
            return 1
        except(exceptions.Conflict):

            self.progress()
            print ' [DONE]'
            print('\n')

            prompt = "- Info: Instance Name provided already exists for user: " + username + " at " + time.strftime("%d/%m/%Y") + " " + time.strftime("%I:%M:%S") + '.'
            self.log(self.datacenter,username,prompt)           
            print(prompt)
            return 1
        except(exceptions.Forbidden):

            self.progress()
            print ' [DONE]'
            print('\n')

            prompt = "- Error: Quota exceeded for instances for user: " + username + " at " + time.strftime("%d/%m/%Y") + " " + time.strftime("%I:%M:%S") + '.'
            self.log(self.datacenter,username,prompt)
            print(prompt)
            return 1

        else:
            uname  = uname.lower()
            path   = current_dir + "/" + '.' + self.datacenter + "/" + '.' + uname
            chkDir = os.path.dirname(path)
            if not os.path.exists(path):
               os.chdir(current_dir)
               os.mkdir('.' + self.datacenter)
               os.chdir('.' + self.datacenter)
               os.mkdir('.' + uname)
               
            
            if os.path.exists(chkDir):
               for myNode in range(int(max_count)):
                   fileName = self.random_with_N_digits(4)
                   fopen = open(current_dir + "/" + '.' + self.datacenter + "/" + '.' + uname + "/" + '.' + str(fileName) + '.create', 'w')
                   fopen.write('[')
                   s = nova.servers.list()[myNode]
                   d = dumps(s._info, sort_keys=True, indent=4, separators=(',', ': '))
                   fopen.write(d)
                   fopen.write(']')
                   fopen.close()
                   processNodes.insert(p,s)
                   p = p + 1

               hold = Base(object)
               hold.hold_server(processNodes)

               userDisplay = PrettyTable(["ID", "INSTANCE NAME", "STATUS"])
               userDisplay.align["ID"] = "l"
               userDisplay.align["INSTANCE NAME"] = "l"
               userDisplay.align["STATUS"] = "l"
               userDisplay.padding_width = 1

               current_dir = current_dir = os.environ["HOME"] 
               for file in os.listdir(current_dir + "/" + '.' + self.datacenter + "/" + '.' + uname):
                   if file.endswith(".create"):
                      createFiles.insert(create,file)
                      create = create + 1

               for c in createFiles:
                   fileSize = os.stat(current_dir + "/" + '.' + self.datacenter + "/" + '.' + uname + "/" + c).st_size != 0
                   if fileSize:
                      with open(current_dir + "/" + '.' + self.datacenter + "/" + '.' + uname + "/" + c, 'r') as f:
                           data = load(f)
                           for item in data:
                               for key, value in item.items():
                                   if key == 'id':
                                      instance_id = value        
                                   if key == 'name':
                                      instances = value
                                   if key == 'status':
                                      instance_s = value
                               userDisplay.add_row([instance_id,instances,instance_s])
           
               self.progress()
               print ' [DONE]'
               print('\n')

               print(userDisplay)
              
               leaseRegion = self.datacenter
 
               self.addLease(leaseRegion, lease, username, fl, instances)

               return data



    def existencyCheck(self, name):
        self.name = name
        if re.match('^[a-zA-Z0-9\-]+$',self.name):
           return True
        else:
            return False



    def random_with_N_digits(self,n):
        self.n = n
        range_start = 10**(self.n-1)
        range_end = (10**self.n)-1
        return randint(range_start, range_end)



    def addLease(self, leaseRegion, lease, username, fl, *hostnames):
        self.lregion   = leaseRegion
        self.lease     = lease
        self.username  = username
        self.fl        = fl
        self.hostnames = hostnames
        listFlavor     = []
        start          = 'Create'
        msg            = MIMEMultipart('related')
        newServer      = []
        findNode       = '<Server:'
        replaceNode    = ''
        j              = 0

        chk = self.username.find('@')
        if chk != -1:
           storeusername = self.username.split('@')
           uname = storeusername[0]
        if chk == -1:
           uname = self.username

        hold = Base(object)

        find    = '<Flavor:'
        replace = ''
        flavor = re.sub(find, replace, str(self.fl))
        flavor = re.sub('>','',str(flavor))
        listFlavor.insert(0,flavor)

        listFlavor     = ''.join(listFlavor)
        listFlavor     = listFlavor.strip()
        self.hostnames = self.hostnames

        for item in self.hostnames:
            leaseNodes = item

        newNodes = hold.newInstance
        for new in newNodes:
            host = re.sub(findNode, replace, str(new))
            host = re.sub('>','',str(host))
            newServer.insert(j,host.strip())
            j = j + 1

        for node in newServer:
            resp = self.notify(self.username,node,self.lease,listFlavor)
            if resp == 'Success':
               prompt = "- Info: Instance request has been submitted for Instance : " + node + " for user: " + self.username + " at " + time.strftime("%d/%m/%Y") + " " + time.strftime("%I:%M:%S") + '.'
               self.log(self.lregion,self.username,prompt)
               print(prompt)
            else:
                prompt = "- Error: Instance request failed with the reason: " + resp + " for user: " + self.username + " at " + time.strftime("%d/%m/%Y") + " " + time.strftime("%I:%M:%S") + '.'
                self.log(self.lregion,self.username,prompt)
                print(prompt)


    def notify(self,receiver,vmname,hours,flavor):
        try:
            self.receiver = receiver
            self.vmname   = vmname
            self.hours    = hours
            self.flavor   = flavor

            me = self.receiver
            msg = MIMEMultipart('related')
            msgAlternative = MIMEMultipart('alternative')
            msg['Subject'] = "Create " + self.vmname + " " + str(self.hours) + " " + self.receiver + " " + self.flavor
            msg['From'] = me
            you = "expostack@expostack.dev.scl1.us.mydomain.net"
            msg['To'] = "expostack@expostack.dev.scl1.us.mydomain.net"
            msg.preamble = 'This is a multi-part message in MIME format.'
            ipaddress = socket.gethostbyname(socket.gethostname())

            text = "Hi!"
            html1 = "<html><head></head><body></body>"
            htmlfinal = []
            htmlb = ''.join(htmlfinal)
            html = ''.join(str(x) for x in (html1,htmlb))
            part1 = MIMEText(text, 'plain')
            part2 = MIMEText(html, 'html')
            msg.attach(msgAlternative)
            msgAlternative.attach(part1)
            msgAlternative.attach(part2)

            s = smtplib.SMTP('mail.mydomain.com')
            s.sendmail(me, you, msg.as_string())
            s.quit()

        except(smtplib.SMTPAuthenticationError):
            response = 'Authentication error.'
        except(smtplib.SMTPConnectError):
            response = 'Error during connection establishment.'
        except(smtplib.SMTPDataError):
            response = 'The SMTP server didn\'t accept the data.'
        except(smtplib.SMTPHeloError):
            response = 'The server refused our HELO reply.'
        except(smtplib.SMTPRecipientsRefused):
            response = 'All recipient addresses refused.'
        except(smtplib.SMTPSenderRefused):
            response = 'Sender address refused.'
        except(smptplib.SMTPServerDisconnected):
            response = 'Not connected to any SMTP server.'
        else:
            response = 'Success'
        return response   



    def expireNotify(self,receiver,vmname,hours,flavor):
        try:
            self.receiver = receiver
            self.vmname   = vmname
            self.hours    = hours
            self.flavor   = flavor
            flag          = 'h'


            me = self.receiver
            msg = MIMEMultipart('related')
            msgAlternative = MIMEMultipart('alternative')
            msg['Subject'] = "RE: Reminder: " + self.vmname + "." + " will expire after 2 hours " + "+" + str(self.hours) + str(flag)
            msg['From'] = me
            you = "expostack@expostack.dev.scl1.us.mydomain.net"
            msg['To'] = "expostack@expostack.dev.scl1.us.mydomain.net"
            msg.preamble = 'This is a multi-part message in MIME format.'
            ipaddress = socket.gethostbyname(socket.gethostname())

            text = "Hi!"
            html1 = "<html><head></head><body></body>"
            htmlfinal = []
            htmlb = ''.join(htmlfinal)
            html = ''.join(str(x) for x in (html1,htmlb))
            part1 = MIMEText(text, 'plain')
            part2 = MIMEText(html, 'html')
            msg.attach(msgAlternative)
            msgAlternative.attach(part1)
            msgAlternative.attach(part2)

            s = smtplib.SMTP('mail.mydomain.com')
            s.sendmail(me, you, msg.as_string())
            s.quit()

        except(smtplib.SMTPAuthenticationError):
            response = 'Authentication error.'
        except(smtplib.SMTPConnectError):
            response = 'Error during connection establishment.'
        except(smtplib.SMTPDataError):
            response = 'The SMTP server didn\'t accept the data.'
        except(smtplib.SMTPHeloError):
            response = 'The server refused our HELO reply.'
        except(smtplib.SMTPRecipientsRefused):
            response = 'All recipient addresses refused.'
        except(smtplib.SMTPSenderRefused):
            response = 'Sender address refused.'
        except(smptplib.SMTPServerDisconnected):
            response = 'Not connected to any SMTP server.'
        else:
            response = 'Success'
        return response


    def changeLeaseNotify(self,username,instancename,lease,flag,flavor):
        try:
            self.receiver = username
            self.vmname   = instancename
            self.hours    = lease
            self.flavor   = flavor
            self.flag     = flag

            me = self.receiver
            msg = MIMEMultipart('related')
            msgAlternative = MIMEMultipart('alternative')
            msg['Subject'] = "RE: Reminder: " + self.vmname + "." + " will expire after 2 hours " + "+" + str(self.hours) + str(flag)
            msg['From'] = me
            you = "expostack@expostack.dev.scl1.us.mydomain.net"
            msg['To'] = "expostack@expostack.dev.scl1.us.mydomain.net"
            msg.preamble = 'This is a multi-part message in MIME format.'
            ipaddress = socket.gethostbyname(socket.gethostname())

            text = "Hi!"
            html1 = "<html><head></head><body></body>"
            htmlfinal = []
            htmlb = ''.join(htmlfinal)
            html = ''.join(str(x) for x in (html1,htmlb))
            part1 = MIMEText(text, 'plain')
            part2 = MIMEText(html, 'html')
            msg.attach(msgAlternative)
            msgAlternative.attach(part1)
            msgAlternative.attach(part2)

            s = smtplib.SMTP('mail.mydomain.com')
            s.sendmail(me, you, msg.as_string())
            s.quit()

        except(smtplib.SMTPAuthenticationError):
            response = 'Authentication error.'
        except(smtplib.SMTPConnectError):
            response = 'Error during connection establishment.'
        except(smtplib.SMTPDataError):
            response = 'The SMTP server didn\'t accept the data.'
        except(smtplib.SMTPHeloError):
            response = 'The server refused our HELO reply.'
        except(smtplib.SMTPRecipientsRefused):
            response = 'All recipient addresses refused.'
        except(smtplib.SMTPSenderRefused):
            response = 'Sender address refused.'
        except(smptplib.SMTPServerDisconnected):
            response = 'Not connected to any SMTP server.'
        else:
            response = 'Success'
        return response


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

        path    = current_dir + "/" + '.' + self.region + "/" + '.' + uname + '.cred'
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
