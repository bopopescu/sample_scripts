#!/usr/bin/env python
""" Utility to check validity & enforce anti-affinity rules on Expostack service groups"""
""" Author: Suhaib Chishti """

import os
import sys
import argparse
import time
from collections import defaultdict, Counter
from keystoneclient import session
from keystoneclient.auth.identity import v3
from keystoneclient.v2_0 import client as ksclient
from novaclient import client as nclient
from keystoneauth1.identity import v3
from keystoneauth1 import session
from keystoneclient.v3 import client
from os import environ as env
import prettytable
from novaclient.v2 import services
#import novaclient 
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("server-group-antiaffinitycheck.py")
handler = logging.FileHandler('/var/log/nova/nova-api.log')
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

def get_args():
    """ Get commandline arguments """
    parser = argparse.ArgumentParser(description='Nova Server Group anti-affinity rule checker')
    parser.add_argument('--check', type=str, help='Validate the specified Server Group')
    parser.add_argument('--list', type=str, help='List instances and their hypervisors for a given Server Group')
    parser.add_argument('--fix', type=str, help='Live migrates instances in Server Group to enforce anit-affinity')
    return parser.parse_args()

def get_server(serverid):
    """ Return Server object """
    return nova.servers.get(serverid)

def get_group_members(server_group_id):
    """ Return list of instance UUIDs present in a Server Group """
    server_group = nova.server_groups.get(server_group_id)
    if 'anti-affinity' in server_group.policies:
        return server_group.members
    else:
        return False

def create_table(fields):
    """ Boilerplate for PrettyTable """
    table = prettytable.PrettyTable(fields, caching=False)
    table.align = 'l'
    return table

def print_group_members(server_group_id):
    """ Print a table detailing Server Group instances and their hypervisors """
    group_members = get_group_members(server_group_id)
    if group_members:
        table = create_table(['Instance ID', 'Instance', 'Hypervisor'])
        for server in get_group_members(server_group_id):
            instance = get_server(server)
            hypervisor = getattr(instance, 'OS-EXT-SRV-ATTR:hypervisor_hostname'.split('.')[0])
            table.add_row([instance.id, instance.name, hypervisor])
        print table
    else:
        print "Server Group", server_group_id, "empty or does not have an anti-affinity policy set."

def print_group_duplicates(server_group_id):
    """ Evaluate whether any instances in a SG have been scheduled to the same hypervisor """
    group_members = get_group_members(server_group_id)
    if group_members:
        hypervisors = []
        instances = defaultdict(list)
        for instance in get_group_members(server_group_id):
            i = get_server(instance)
            hypervisor = getattr(i, 'OS-EXT-SRV-ATTR:hypervisor_hostname')
            instances[instance].append(i.name)
            instances[instance].append(hypervisor)
            hypervisors.append(hypervisor)
        dupes = [k for k, v in Counter(hypervisors).items() if v > 1]
        if dupes:
            print "Anti-affinity rules violated in Server Group:", server_group_id
            table = create_table(['Instance ID', 'Instance', 'Hypervisor'])
            [table.add_row([instance_id, instance_name, hypervisor])
             for instance_id, [instance_name, hypervisor] in instances.items()
             if hypervisor in dupes]
            print table
        else:
            print "No anti-affinity rules violated for Server Group:", server_group_id
    else:
        print "Server Group", server_group_id, "empty or does not have an anti-affinity policy set."

def fix_group_duplicates(server_group_id):
    """ Enforce anti-affinity on any instances in a SG that have been scheduled to the same hypervisor """
    group_members = get_group_members(server_group_id)
    if group_members:
        hypervisors = []
        instances = defaultdict(list)
        for instance in get_group_members(server_group_id):
            i = get_server(instance)
            hypervisor = getattr(i, 'OS-EXT-SRV-ATTR:hypervisor_hostname')
            instances[instance].append(i.name)
            instances[instance].append(hypervisor)
            hypervisors.append(hypervisor)
        dupes = [k for k, v in Counter(hypervisors).items() if v > 1]
	def find_availabilityzone(compute_node_name):
		for serverz in nova.services.list(binary="nova-compute"):
		   if compute_node_name == serverz.host:
			return serverz.zone
			break
        if dupes:
          # print "Anti-affinity rules violated in Server Group:", server_group_id
	    logger.info('Anti-affinity rules violated in Server Group: %s', server_group_id)
	    for instance_id, [instance_name, hypervisor] in instances.items():
		if hypervisor in dupes:
		#  print instance_id, hypervisor
		   old_host = hypervisor.split('.')[0]
		#  print old_host
		   for server in nova.services.list(binary="nova-compute"):
			if old_host == server.host:
		#		print server.zone
			 	free_node = 0
				for stat in nova.hypervisors.list():
		#		    print "free_node",free_node
				    new_host = stat.hypervisor_hostname.split('.')[0]
				    new_host_az = find_availabilityzone(new_host)
				    if stat.free_ram_mb > free_node and server.zone == new_host_az and stat.hypervisor_hostname not in hypervisors:
					free_node = stat.free_ram_mb
		#			print stat.hypervisor_hostname
					free_node_name = new_host
		#		print free_node_name,free_node		
		   try:
		      logger.info('Going to live migrate instance %s to host %s inorder to enforce antiaffinity rule',instance_id,free_node_name)
		      nova.servers.live_migrate(host=free_node_name, block_migration=False, server=instance_id, disk_over_commit=False)
		      time.sleep(90)
		      args = get_args()
    		      group = sys.argv[2]
		      fix_group_duplicates(group)
		   except:
	              logger.error('Possible error while migrating instance %s to host %s.', instance_id,free_node_name)
  		      os.system("printf '\n \n \n Reason: Possiblely an error occured during live migration.' | mail -s 'Alert - Error while trying to enforce anti-affinity on server groups.' NOC@mydomain.com")
		      sys.exit(1)
			
		
          # table = create_table(['Instance ID', 'Instance', 'Hypervisor'])
          # [table.add_row([instance_id, instance_name, hypervisor])
          #  for instance_id, [instance_name, hypervisor] in instances.items()
          #  if hypervisor in dupes]
          # print table
        else:
            print "No anti-affinity rules violated for Server Group:", server_group_id
	    os._exit(1)
    else:
        print "Server Group", server_group_id, "empty or does not have an anti-affinity policy set."


if __name__ == '__main__':
    os.environ["OS_AUTH_URL"] = "http://expostack.tf-net.mydomain.com:35357/v3"
    os.environ["OS_PROJECT_DOMAIN_ID"] = "default"
    os.environ["OS_USER_DOMAIN_ID"] = "default"
    os.environ["OS_PROJECT_NAME"] = "admin"
    os.environ["OS_TENANT_NAME"] = "admin"
    os.environ["OS_USERNAME"] = "admin"
    os.environ["OS_PASSWORD"] = "XXXXXXXXXX"
    os.environ["OS_IDENTITY_API_VERSION"] = "3"
    auth = v3.Password(user_domain_name=env['OS_USER_DOMAIN_ID'],username=env['OS_USERNAME'],password=env['OS_PASSWORD'],project_domain_id=env['OS_USER_DOMAIN_ID'],project_name=env['OS_PROJECT_NAME'],auth_url=env['OS_AUTH_URL'])
    sess = session.Session(auth=auth)
    nova = nclient.Client(2, session=sess)
    args = get_args()
    group = sys.argv[2]
    if args.check:
        print_group_duplicates(group)
    if args.list:
        print_group_members(group)
    if args.fix:
        fix_group_duplicates(group)
