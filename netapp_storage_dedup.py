#########################
## 
## Script helps check/enable dedup status of volumes in SVM used by Expostack Storage As a Service 
## 
## Author: Suhaib Chishti
## 
## Prerequisites: Please make sure Cinder-Weekly & Manila-Weekly Storage efficiency policies exist on the SVM 
## 
## NOTE: Make sure all SVM used by  Expostack Storage As a Service are placed in list 'smvs'
## python /usr/local/bin/netapp_storage_dedup.py help
##
## Usage- Volume dedup status:
## python netapp_storage_dedup.py status 
##
## Usage- Volume enable dedup/compression:
## python netapp_storage_dedup.py efficiency
########################
#!/usr/bin/python
import sys
sys.path.append("/usr/local/src/lease_expire/netapp-manageability-sdk-5.3/lib/python/NetApp")
from NaServer import *
from bs4 import BeautifulSoup
from prettytable import PrettyTable
import os

if len (sys.argv) != 2 :
    print "\n Usage- Volume dedup status:\n python netapp_storage_dedup.py status "
    print "\n Usage- Volume enable dedup/compression:\n python netapp_storage_dedup.py efficiency \n"
    sys.exit (1)

def print_status(x):
   rxo = s.invoke_elem(x)
   if (rxo.results_status() == "failed"):
            raise NAException(rxo.sprintf())
   str_rxo = str(rxo.sprintf())
   res=BeautifulSoup(str_rxo)
   names = res.results.findAll("name")
   dedup = res.results.findAll("is-sis-volume")
   status = res.results.findAll("state")
   figures = {}
   counter = 0 
   diff = 0
   for num  in xrange(0,(len(names))):
     key = str(names[num]).split('>')[1].split('<')[0]
     state = str(status[num]).split('>')[1].split('<')[0]
     if 'online' in state:
        counter = num - diff
        value = str(dedup[counter]).split('>')[1].split('<')[0]
        figures.update({key:value})
     else:
        diff = diff + 1
        continue
   x = PrettyTable()
   x.field_names = ["Vol Name","Dedup Status"]

   for key,value in figures.iteritems():
       x.add_row([key,value])

   print(x)
   print "\n"
   return figures

svms=['svm-dev-saas-01','svm-prod-saas-01']

for mysvm in svms:
  myfiler='fcl02-mgmt.scl1.us.tribalfusion.net'
  user='cinderapi'
  password='mypassword'
  cmd='/usr/local/src/lease_expire/netapp-manageability-sdk-5.3/src/sample/Data_ONTAP/Python/apitest.py'
  s = NaServer(myfiler, 1, 7)
  s.set_admin_user(user,password)
  s.set_vfiler(mysvm)
  x = NaElement('volume-get-iter')
  x.child_add(NaElement('query','is-sis-volume=False'))

  if 'stat' in sys.argv[1]:      
     print "\n********* Current status of SVM '"+mysvm+"'\n"
     print_status(x)

  elif 'eff' in sys.argv[1]:
    print "\n********* Current status of SVM '"+mysvm+"'\n"
    figures = print_status(x)
    for key,value in figures.iteritems():
       if 'root' in key or 'cinder' in key or 'true' in value:
  	  pass
       elif 'share' in key:
          dedup_cmd="python " + cmd + " -v " + mysvm +" "+ myfiler +" "+ user +" "+ password + " sis-enable path /vol/" + key  
          compress_cmd="python " + cmd + " -v " + mysvm +" "+ myfiler +" "+ user +" "+ password + " sis-set-config  enable-compression true path /vol/" + key  
          run_cmd="python " + cmd + " -v " + mysvm +" "+ myfiler +" "+ user +" "+ password + " sis-set-config path /vol/" + key + " policy-name 'Manila-Weekly'" 
	  try:
	    print "\n \n Setting dedup on volume '"+key+"' .................\n"
            os.system(dedup_cmd)
	    print "\n Setting compression on volume '"+key+"' .................\n"
            os.system(compress_cmd)
	    print "\n Setting efficieny policy on volume '"+key+"' .................\n"
            os.system(run_cmd)
            print "\nLatest status of SVM '"+mysvm+"'\n"
	    print_status(x)
	  except:
		print "\n Error occurred while updating volume '"+key+"', please check manually! \n"
	        os.system("'echo Please check volume and run netapp_storage_dedup.py with 'status' switch!' | mailx -s 'Error occurred while setting dedup/compression setting on volume' noc@exponential.com")
       elif 'volume' in key:
          dedup_cmd="python " + cmd + " -v " + mysvm +" "+ myfiler +" "+ user +" "+ password + " sis-enable path /vol/" + key  
          compress_cmd="python " + cmd + " -v " + mysvm +" "+ myfiler +" "+ user +" "+ password + " sis-set-config  enable-compression true path /vol/" + key  
          run_cmd="python " + cmd + " -v " + mysvm +" "+ myfiler +" "+ user +" "+ password + " sis-set-config path /vol/" + key + " policy-name 'Cinder-Weekly'" 
	  try:
	    print "\n \n Setting dedup on volume '"+key+"' .................\n"
            os.system(dedup_cmd)
	    print "\n Setting compression on volume '"+key+"' .................\n"
            os.system(compress_cmd)
	    print "\n Setting efficieny policy on volume '"+key+"' .................\n"
            os.system(run_cmd)
	    print "\n Latest status of SVM '"+mysvm+"': \n\n"
            print "\nLatest status of SVM '"+mysvm+"'\n"
	    print_status(x)
	  except:
		print "\n Error occurred while updating volume '"+key+"', please check manually! \n"
   
  else:
      print "\n Usage- Volume dedup status:\n python netapp_storage_dedup.py status "
      print "\n Usage- Volume enable dedup/compression:\n python netapp_storage_dedup.py efficiency \n"
      sys.exit(1)
