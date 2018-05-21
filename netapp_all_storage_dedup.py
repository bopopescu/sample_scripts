#########################
## 
## Script helps check/enable dedup status of volumes in SVM used by Expostack Storage As a Service 
## 
## Author: Suhaib Chishti
## 
## Prerequisites: Please make sure Cinder-Weekly & Manila-Weekly Storage efficiency policies exist on the SVM 
## 
## NOTE: Make sure all SVM used by  Expostack Storage As a Service are placed in list 'smvs'
## python /usr/local/bin/expo_netapp_dedup_checker.py help
##
## Usage- Volume dedup status:
## python expo_netapp_dedup_checker.py status 
##
## Usage- Volume enable dedup/compression:
## python expo_netapp_dedup_checker.py efficiency
########################
#!/usr/bin/python
import sys
sys.path.append("/usr/local/src/lease_expire/netapp-manageability-sdk-5.3/lib/python/NetApp")
from NaServer import *
from bs4 import BeautifulSoup
from prettytable import PrettyTable
import os
import xml.etree.ElementTree as ET

if len (sys.argv) < 2 :
    print "\n Usage- Volume dedup status on all SVMs:\n python expo_netapp_dedup_checker.py status "
    print "\n Usage- Volume enable dedup/compression on all SVMs:\n python expo_netapp_dedup_checker.py efficiency \n"
    print "\n Usage- Volume dedup status of specified SVM:\n python expo_netapp_dedup_checker.py status <svm name> "
    print "\n Usage- Volume enable dedup/compression on specified SVM:\n python expo_netapp_dedup_checker.py efficiency <svm name> \n"
    print "\n Usage- Volume enable dedup/compression of a single volume on a on specified SVM :\n python expo_netapp_dedup_checker.py dedup <svm name> <volume name> \n "
    sys.exit (1)

def print_status(x):
   figures = {}
   rxo = s.invoke_elem(x)
   if (rxo.results_status() == "failed"):
	    print ("Error:\n")
            print (rxo.sprintf())
	    sys.exit (1)
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
if len (sys.argv) < 3 :
    svms=['svm-dev-clones','svm-dev-01','svm-corp-01','svm-prod-01','svm-prod-02','svm-prod-ad','svm-stby-ad']
elif len (sys.argv) >= 3 and 'svm' in sys.argv[2] :
    svms= [sys.argv[2]]
#svms= [sys.argv[2]]

for mysvm in svms:
  myfiler='fcl02-mgmt.scl1.us.tribalfusion.net'
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
	    if 'prod' not in mysvm:
	        print "\n Setting compression on volume '"+key+"' .................\n"
                os.system(compress_cmd)
	        print "\n Setting efficieny policy on volume '"+key+"' .................\n"
            os.system(run_cmd)
            print "\nLatest status of SVM '"+mysvm+"'\n"
	    print_status(x)
	  except:
		print "\n Error occurred while updating volume '"+key+"', please check manually! \n"
	        os.system("'echo Please check volume and run expo_netapp_dedup_checker.py with 'status' switch!' | mailx -s 'Error occurred while setting dedup/compression setting on volume' noc@exponential.com")
   
  elif 'dedup' in sys.argv[1]:      
     print "\n********* Current status of SVM '"+mysvm+"'\n"
     figures = print_status(x)
     key= [sys.argv[3]]
     print "\n********* Setting dedup on volume '"+key[0]+"'\n"
     dedup_cmd="python " + cmd + " -v " + mysvm +" "+ myfiler +" "+ user +" "+ password + " sis-enable path /vol/" + key[0]  
     compress_cmd="python " + cmd + " -v " + mysvm +" "+ myfiler +" "+ user +" "+ password + " sis-set-config  enable-compression true path /vol/" + key[0] 
     run_cmd="python " + cmd + " -v " + mysvm +" "+ myfiler +" "+ user +" "+ password + " sis-set-config path /vol/" + key[0] + " policy-name 'Biweekly'" 
     try:
	    print "\n \n Setting dedup on volume '"+key[0]+"' .................\n"
            os.system(dedup_cmd)
	    if 'prod' not in mysvm:
	        print "\n Setting compression on volume '"+key[0]+"' .................\n"
                os.system(compress_cmd)
	        print "\n Setting efficieny policy on volume '"+key[0]+"' .................\n"
            os.system(run_cmd)
            print "\nLatest status of SVM '"+mysvm+"'\n"
	    print_status(x)
     except:
		print "\n Error occurred while updating volume '"+key[0]+"', please check manually! \n"
	        os.system("'echo Please check volume and run expo_netapp_dedup_checker.py with 'status' switch!' | mailx -s 'Error occurred while setting dedup/compression setting on volume' noc@exponential.com")

  else:
      print "\n Usage- Volume dedup status on all SVMs:\n python expo_netapp_dedup_checker.py status "
      print "\n Usage- Volume enable dedup/compression on all SVMs:\n python expo_netapp_dedup_checker.py efficiency \n"
      print "\n Usage- Volume dedup status of specified SVM:\n python expo_netapp_dedup_checker.py status <svm name> "
      print "\n Usage- Volume enable dedup/compression on specified SVM:\n python expo_netapp_dedup_checker.py efficiency <svm name> \n"
      print "\n Usage- Volume enable dedup/compression of a single volume on a on specified SVM :\n python expo_netapp_dedup_checker.py dedup <svm name> <volume name> \n"
      sys.exit(1)
