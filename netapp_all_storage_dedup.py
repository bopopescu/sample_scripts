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
import xml.etree.ElementTree as ET

if len (sys.argv) != 3 :
    print "\n Usage- Volume dedup status:\n python netapp_storage_dedup.py status "
    print "\n Usage- Volume enable dedup/compression:\n python netapp_storage_dedup.py efficiency \n"
    sys.exit (1)

def print_status(x):
   figures = {}
   rxo = s.invoke_elem(x)
   if (rxo.results_status() == "failed"):
            raise NAException(rxo.sprintf())
   str_rxo = str(rxo.sprintf())
   res=BeautifulSoup(str_rxo)
   volume_info = ET.fromstring(str_rxo)
   name = volume_info.findall('attributes-list/volume-attributes/volume-id-attributes')
   dedup = volume_info.findall('attributes-list/volume-attributes/volume-sis-attributes')
   attr = volume_info.findall('attributes-list/volume-attributes/volume-state-attributes')
   for num  in range(len(name)):
     key = name[num].find('name').text
     state = attr[num].find('state').text
     if 'online' in state and 'root' not in key:
        value = dedup[num].find('is-sis-volume').text
        figures.update({key:value})
     else:
        continue
   x = PrettyTable()
   x.field_names = ["Vol Name","Dedup Status"]

   for key,value in figures.iteritems():
       x.add_row([key,value])

   print(x)
   print "\n"
   return figures

#svms=['svm-dev-clones','svm-dev-01','svm-corp-01','svm-prod-01','svm-prod-02','svm-prod-ad','svm-stby-ad']
#svms=['svm-dev-clones']
svms= [sys.argv[2]]

for mysvm in svms:
  myfiler='fcl02-mgmt.scl1.us.mydomain.com'
  user='dedupuser'
  password='dedup123'
  cmd='/usr/local/src/lease_expire/netapp-manageability-sdk-5.3/src/sample/Data_ONTAP/Python/apitest.py'
  s = NaServer(myfiler, 1, 7)
  s.set_admin_user(user,password)
  s.set_vfiler(mysvm)
  x = NaElement('volume-get-iter')
  x.child_add(NaElement('query','is-sis-volume=False'))
  x.child_add_string( 'max-records', 10000 )

  if 'stat' in sys.argv[1]:      
     print "\n********* Current status of SVM '"+mysvm+"'\n"
     print_status(x)

  elif 'eff' in sys.argv[1]:
    print "\n********* Current status of SVM '"+mysvm+"'\n"
    figures = print_status(x)
    for key,value in figures.iteritems():
       if 'root' in key or 'true' in value: 
  	  pass
       else:
          dedup_cmd="python " + cmd + " -v " + mysvm +" "+ myfiler +" "+ user +" "+ password + " sis-enable path /vol/" + key  
          compress_cmd="python " + cmd + " -v " + mysvm +" "+ myfiler +" "+ user +" "+ password + " sis-set-config  enable-compression true path /vol/" + key  
          run_cmd="python " + cmd + " -v " + mysvm +" "+ myfiler +" "+ user +" "+ password + " sis-set-config path /vol/" + key + " policy-name 'Biweekly'" 
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
	        os.system("'echo Please check volume and run netapp_storage_dedup.py with 'status' switch!' | mailx -s 'Error occurred while setting dedup/compression setting on volume' noc@mydomain.com")
   
  else:
      print "\n Usage- Volume dedup status:\n python netapp_storage_dedup.py status "
      print "\n Usage- Volume enable dedup/compression:\n python netapp_storage_dedup.py efficiency \n"
      sys.exit(1)
