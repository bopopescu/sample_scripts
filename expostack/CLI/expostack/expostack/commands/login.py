"""The login command."""

import warnings

warnings.filterwarnings("ignore")

import sys

import os

import time

import getpass

import base64

from prettytable import PrettyTable

from keystoneauth1.identity import v3

from keystoneauth1 import session

from keystoneauth1.exceptions.http import Unauthorized

from keystoneclient.v3 import client

from keystoneclient import exceptions

from keystoneclient.auth.identity import v3

from keystoneclient import session

from novaclient import client as novaClient

import glanceclient.v2.client as glclient

from neutronclient.v2_0 import client as nclient

from json import dumps

from json import dump

from json import loads

from json import load

from pprint import pprint

from .base import Base


class Login(Base):
    """Authenticate username and password of the user.!"""

    def run(self):
        password  = getpass.getpass('Enter Password:')

        inputList = []
        values    = self.options
        regions   = ('SCL1','LA1')
        rstatus   = False 

        for key, value in values.iteritems():
            if key == '--region':
               if value not in regions:
                  rstatus = True 
                  break               
               else:
                   inputList.insert(0,value)
            if key == '--project':
               inputList.insert(1,value)
            if key == '--username':
               inputList.insert(2,value)

        if rstatus == True:
           print('- Error: Region Name doesn\'t exists.')
           return False

        if password:
           inputList.insert(3,base64.b64encode(password))

        if not password:
           print '- Error: Empty password. Please try again.'
           sys.exit()


        restrict_users = ('sysadmin', 'root')

        ldap_user = getpass.getuser()

        if ldap_user in restrict_users:
           print("- Error: Login using LDAP username/password only.")
           return False


        current_dir = os.environ["HOME"]

        try: 
            cred_dir    = os.path.dirname(os.path.abspath(__file__)) 
 
            with open(cred_dir + "/" + '.credentials') as cred:
               credentials = cred.readlines()

        except(ValueError,IOError):
            print("- Error: Cound not find credentials file in:" + os.environ["HOME"])
            return False
        else: 
            user_domain    = credentials[0].split('=')
            project_domain = credentials[1].split('=')
            SCL_KEY        = credentials[2].split('=')[0]
            LA_KEY         = credentials[3].split('=')[0]
            SCL_VALUE      = credentials[2].split('=')[1]
            LA_VALUE       = credentials[3].split('=')[1]


            user  =  user_domain[1].rstrip()
            proj  =  project_domain[1].rstrip()


            REGION    = inputList[0].strip()
            project   = inputList[1].strip()
            username  = inputList[2].strip()
            passwrd   = base64.b64decode(inputList[3]).strip()

            region    = REGION.upper()

            if region.strip() == SCL_KEY.strip():
               link = SCL_VALUE.strip()

            if region.strip() == LA_KEY.strip():
               link = LA_VALUE.strip() 

            username = username.lower()

            chk = username.find('@')
            if chk != -1:
               storeusername = username.split('@')
               uname = storeusername[0]
            if chk == -1:
               uname = username

            checkFile = current_dir + "/" + '.' + region + "/" + '.' + uname
            jsonFile  = current_dir + "/" + '.' + region + "/" + '.' + uname + "/" + uname + '.json'
            cacheFile = current_dir + "/" + '.' + region + "/" + '.' + uname + '.cred'

        try:
            if checkFile or jsonFile or cacheFile:
               os.remove(checkFile)
               os.remove(jsonFile)
               os.remove(cacheFile)
        except(OSError):
            pass
     
        WPROJECT  = base64.b64encode("PROJECT_NAME") + "." + base64.b64encode(project)
        WUSERNAME = base64.b64encode("USER_NAME") + "." + base64.b64encode(uname)

        path   = current_dir + "/" + '.' + region + "/" + '.' + uname
        chkDir = os.path.dirname(path)
        if not os.path.exists(path):
           os.makedirs(path)

        try:
           fs = open(current_dir + "/" + '.' + region + "/" + '.' + uname +"/" + '.' + uname,'w')
           fs.write(WPROJECT + '\n')
           fs.write(WUSERNAME + '\n')
           fs.close()
        except(IOError):
            print("- Error - Expostack is unable to access your home directory, contact your system Administrator")
            return False 

        print('\n')

        print '- LOADING : ........ ',
        sys.stdout.flush()


        auth = v3.Password(user_domain_name=user,
                    username="'" + username + "'",
                    password="'" + passwrd + "'",
                    project_domain_name=proj,
                    project_name="'" + project + "'",
                    auth_url=link)
        sess = session.Session(auth=auth)
        keystone = client.Client(session=sess)

        try:
            sess     = session.Session(auth=auth)
            keystone = client.Client(session=sess)

            if region.strip() == SCL_KEY.strip():
               rawToken =  keystone.get_raw_token_from_identity_service('http://expostack.tf-net.mydomain.com:35357/v3',
                                                                        username=username,
                                                                        user_domain_name='mydomain',
                                                                        password=passwrd,
                                                                        project_name=project,
                                                                        project_domain_name='mydomain')

            if region.strip() == LA_KEY.strip():
               rawToken =  keystone.get_raw_token_from_identity_service('http://expostack-02.tf-net.mydomain.com:35357/v3',
                                                                        username=username,
                                                                        user_domain_name='mydomain',
                                                                        password=passwrd,
                                                                        project_name=project,
                                                                        project_domain_name='mydomain')

        except(exceptions.Unauthorized,exceptions.CommandError,exceptions.BadRequest,exceptions.EndpointNotFound,exceptions.AuthorizationFailure,exceptions.from_response,exceptions.InvalidResponse):
            self.progress()
            print ' [DONE]'
            print('\n')
 
            prompt = "- Error: Authentication failed for user: " + username + " at " + time.strftime("%d/%m/%Y") + " " + time.strftime("%I:%M:%S") + '.'
            self.log(region,username,prompt)
            print(prompt)
            self.errorMsg()
            return 1
        else:
            with open(current_dir + "/" + '.' + region + "/" + '.' + uname + "/" + '.' + uname + '.json', 'wt') as out:
                 sendJson = dump(rawToken, out, sort_keys=True, indent=4, separators=(',', ': '))

            with open(current_dir + "/" + '.' + region + "/" + '.' + uname + "/" + '.' + uname + '.json', 'r') as f:
                 data = load(f)

            for key, value in data.items():
                if key == "user":
                   user_values = value

                if key =="auth_token":
                   token_values = value

                if key =="project":
                   for subkey, subvalue in value.items():
                       if subkey == "name":
                          project_name = subvalue
                       if subkey == "domain":
                          for childkey, childvalue in subvalue.items():
                              if childkey == "name":
                                 project_domain_name = childvalue                  

            for i,j in user_values.items():
                if i == "id":
                   user_id =  j
                if i == "name":
                   user_name = j

            c_id   = user_id
            c_name = user_name

            cache = {}
            cache = {'token': token_values, 'id': c_id, 'username': c_name, 'project_name': project_name, 'project_domain_name': project_domain_name, 'region': region.strip()}
            fc = open(current_dir + "/" + '.' + region + "/" + '.' + uname + '.cred', 'w')
            fc.write(str(cache))

            self.progress()

            print ' [DONE]'


            self.message(REGION,uname)

            prompt = "Authentication successful for user: " + username + " at " + time.strftime("%d/%m/%Y") + " " + time.strftime("%I:%M:%S")
            self.log(REGION,c_name,prompt)


            return 0



    def message(self, regionName, username):
        self.username   = username
        self.regionName = regionName
        current_dir     = os.environ["HOME"]

        self.username = self.username.lower()

        chr = self.username.find('@')
        if chr != -1:
           name = self.username.split('@')
           user = name[0]
        if chr == -1:
           user = self.username

        msg  = '\n' + '- Welcome '+ user +', your authentication is successful.' + '\n' 
        msg += '- Logs are located at: ' + current_dir + "/" + '.' + self.regionName + "/" + '.' + user + "/" + '.' + user + '.log' + '\n'
        msg += '- Use: expostack -h to view full list of commands.' + '\n'
        print msg



    def errorMsg(self):
        error =  '\n' + '- Possible Reasons:' + '\n'
        error += '- Email Address or Password is Wrong.' + '\n'
        error += '- Access to expostack is Denied.' + '\n'
        error += '- Account is Disabled.' + '\n' 
        print error



    def displayImages_flavors_zones(self, region, c_name, userRecords):
        
        img     = []
        img_id  = []
        net_id  = []
        net_val = []
        v       = []
        flavor  = []
        content = []
        i = 0
        n = 0
        y = 0
        self.username = c_name
        self.region   = region
        self.imgId    = ''
        self.imgName  = ''
        self.visible  = ''

        region_val    = [] 
        current_dir   = os.environ["HOME"]

        chk = self.username.find('@')
        if chk != -1:
           storeusername = self.username.split('@')
           uname = storeusername[0]
        if chk == -1:
           uname = self.username

        self.auth = userRecords
        for key, value in self.auth.iteritems():
            if key == 'token':
               token = value

            if key == 'project_name':
               project_name = value

            if key == 'project_domain_name':
               project_domain_name = value
   

        print '- LOADING : ........ ',
        sys.stdout.flush()
 
        try:
           if self.region == 'SCL1':
              novaauth    = v3.Token(auth_url='http://expostack.tf-net.mydomain.com:35357/v3',token=token,project_name=project_name,project_domain_name=project_domain_name)
           if self.region == 'LA1':
              novaauth    = v3.Token(auth_url='http://expostack-02.tf-net.mydomain.com:35357/v3',token=token,project_name=project_name,project_domain_name=project_domain_name)

           session_id  = session.Session(auth=novaauth)
           keystone    = client.Client(session=session_id)
           nova        = novaClient.Client('2', session=session_id)
           glance      = glclient.Client('2', session=session_id)
           neutron     = nclient.Client(session=session_id)
        except(exceptions.AuthorizationFailure):

            self.progress()
            print ' [DONE]'
            print('\n')

            prompt = '- Error: Unable to authenticate or validate the existing authorization token for ' + uname + ' at ' + time.strftime("%d/%m/%Y") + ' ' + time.strftime("%I:%M:%S") + '.'
            self.log(self.region,c_name,prompt)
            print(prompt)
            return 1
        except(exceptions.Unauthorized):

            self.progress()
            print ' [DONE]'
            print('\n')

            prompt = '- Error: Authentication failed due to invalid token for ' + uname + ' at ' + time.strftime("%d/%m/%Y") + ' ' + time.strftime("%I:%M:%S") + '.'
            self.log(self.region,c_name,prompt)
            print(prompt)
            return 1

        try:
            userDisplay = PrettyTable(["CATALOG NAME","ACCESS","FLAVOR","ZONES","NETWORK NAME","REGION NAME"])
            userDisplay.align["CATALOG NAME"] = "l"
            userDisplay.align["ACCESS"]       = "l"
            userDisplay.align["FLAVOR"]       = "l"
            userDisplay.align["ZONES"]        = "l"
            userDisplay.align["NETWORK NAME"] = "l"
            userDisplay.align["REGION NAME"]  = "l" 
            userDisplay.padding_width = 1


            glanceImages = glance.images.list()
            images       = list(glanceImages)

            with open(current_dir + "/" + '.' + self.region + "/" + '.' + uname.lower() + "/" + '.' + 'images' + '.json', 'wt') as out:
                 sendJson = dump(images, out, sort_keys=True, indent=4, separators=(',', ': '))

            with open(current_dir + "/" + '.' + self.region + "/" + '.' + uname.lower() + "/" + '.' + 'images' + '.json', 'r') as f:
                 data = load(f)

            for item in data:
                for key, value in item.items():
                    if key == 'id':
                       self.imgId = value
                    if key == 'name':
                       self.imgName = value
                    if key == 'visibility':
                       self.visible = value

                       imgList    = self.makeImage(self.visible,self.imgName)
                       imgID      = self.makeImgId(self.visible,self.imgId)
                       imgVisible = self.makeVisible(self.visible)

                       if imgList:
                          img.insert(i,imgList)

                       if imgID:
                          img_id.insert(i,imgID) 

                       if imgVisible:
                          v.insert(i,imgVisible)

                          i = i + 1


            flavors = nova.flavors.list()

            for item in flavors:
                flavor.insert(n,item.name)
                n = n + 1

            if len(v) > len(flavor):
               first  = len(v)
               second = len(flavor)
               third = first - second
               for blank in range(third):
                   flavor.append('-')
                   third = third - 1

               fl = flavor

            zone = open(current_dir + "/" + '.' + self.region + "/" + '.' + uname.lower() + "/" + '.zones','w')
            zones = nova.availability_zones.list(detailed=True)
            for z in zones:
                one = str(z).replace('<AvailabilityZone:','')
                two = str(one).replace('>','')
                zone.write(str(two).lstrip() + ',')
            zone.close()

            with open(current_dir + "/" + '.' + self.region + "/" + '.' + uname.lower() + "/" + '.zones') as f:
               lines = f.read()
            content = lines.rstrip(',').split(',')
            
            if len(v) > len(content):
               init   = len(v)
               sec    = len(content)
               th     = init - sec
               for empty in range(th):
                   content.append('-')
                   th = th - 1

               zones_list = content


            network = neutron.list_networks()

            with open(current_dir + "/" + '.' + self.region + "/" + '.' + uname.lower() + "/" + '.network.json', 'wt') as out:
                 netJson = dump(network, out, sort_keys=True, indent=4, separators=(',', ': '))

            with open(current_dir + "/" + '.' + self.region + "/" + '.' + uname.lower() + "/" + '.network.json', 'r') as f:
                 net_data = load(f)

            for key, value in net_data.items():
                for column in value:
                    for net_key, net_value in column.items():
                        if net_key == 'id':
                           net_id.insert(y,net_value)
                        if net_key == 'name':
                           net_val.insert(y,net_value)
                        y = y + 1

            network_id  = net_id
            network_val = net_val

            if len(v) > len(network_id):
               net_one = len(v)
               net_two = len(network_id)
               net_th  = net_one - net_two
               for blank in range(net_th):
                   network_id.append('-')
                   network_val.append('-')
                   net_th = net_th - 1

               _net_id = network_id
               _net_val = network_val

            
            region_val = self.region.split()
            if len(v) > len(region_val):
               r_one = len(v)
               r_two = len(region_val)
               r_th  = r_one - r_two
               for rank in range(r_th):
                   region_val.append('-')
                   r_th = r_th - 1

               _region_val = region_val

       
            for l,m,n,p,q,r in map(None,img,v,fl,zones_list,_net_val,_region_val):
                userDisplay.add_row([l,m,n,p,q,r])

            self.progress()
            print ' [DONE]'
            print('\n')

            print '- USE THE TABLE DETAILS: IMAGE, FLAVOR, AVAILABILITY ZONES, NETWORK NAME FOR INSTANCE CREATION.'
            print(userDisplay)
        except(IOError,IndexError,KeyError,NameError,OSError,RuntimeError,SyntaxError,IndentationError,TypeError,UnboundLocalError,ValueError):
            self.progress()
            print ' [DONE]'
            print('\n')

            prompt = '- Error: Could not fetch the resource records for ' + uname + ' at ' + time.strftime("%d/%m/%Y") + ' ' + time.strftime("%I:%M:%S") + '.'
            self.log(self.region,uname,prompt)
            print(prompt)
            return 1
        else:
            prompt = '- Info: Resource records fetch successful for ' + uname + ' at ' + time.strftime("%d/%m/%Y") + ' ' + time.strftime("%I:%M:%S") + '.'
            self.log(self.region,uname,prompt)
            print(prompt)
            return 0


    def progress(self):
        print '\b',
        sys.stdout.flush()
        time.sleep(10)


    def log(self,region,username,prompt):
        try:
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

            log = open(current_dir + "/" + '.' + self.region + "/" + '.' + uname.lower() + "/" + '.' + uname + '.log','a')
            log.write(self.prompt + '\n')
      
            log.close()
        except(IOError,IndexError,KeyError,NameError,OSError,RuntimeError,SyntaxError,IndentationError,TypeError,UnboundLocalError,ValueError):
            prompt = '- Info: Could not create logs for ' + uname + ' at ' + time.strftime("%d/%m/%Y") + ' ' + time.strftime("%I:%M:%S") + '.'
            self.log(self.region,uname,prompt)
            print(prompt)
            return 0


    def makeImage(self,visible,imgName):
        self.visible = visible
        self.imgName = imgName
        if self.visible == 'private':
           return False
        else:
            return self.imgName                


    def makeImgId(self,visible,imgId):
        self.visible = visible
        self.imgId   = imgId
        if self.visible == 'private':
           return False
        else:
            return self.imgId


    def makeVisible(self,visible):
        self.visible = visible
        if self.visible == 'private':
           return False
        else:
            return self.visible
