"""
expostack

Usage:
 expostack login --region region --project projectname --username emailaddress
 expostack create --region region --name name --catalog catalog_name --instances number --lease lease_days --flavor flavor --tag tag_name [--user-data file] [--property key=value,key2=value2] [--boot-volume volume]
 expostack create --region region ---vol-name vol_name --vol-type vol_type_name --size number --lease lease_days --description description [--property key=value,key2=value2] 
 expostack status --region region --instance instance_name
 expostack status --region region --list all
 expostack status --region region --expiry list
 expostack operate --region region --changelease instace_name --extend number --flag flag
 expostack operate --region region --reset instance_name --status state
 expostack operate --region region --destroy instance_name
 expostack operate --region region --expire instance_name
 expostack operate --region region --reboot instace_name
 expostack operate --region region --shutdown instance_name
 expostack operate --region region --suspend instance_name
 expostack operate --region region --resume instance_name
 expostack operate --region region --poweron instance_name
 expostack operate --region region --poweroff instance_name
 expostack operate --region region --pause instance_name
 expostack operate --region region --unpause instance_name
 expostack operate --region region --instance instance_name --property k=v,k1=v1
 expostack operate --region region --instance instance_name --volume-attach volume [--device device]
 expostack operate --region region --instance instance_name --volume-update volume --attachment attachment
 expostack operate --region region --instance instance_name --volume-detach volume --attachment attachment


 expostack -h | --help
 expostack --version

Options:
  --region region              Region Name. options allowed ( SCL1 | LA1 ).
  --project projectname        Project Name of the User.
  --username emailaddress      Email Address of the user.
  --name name                  Name of the Instance to create.
  --vol-name vol_name          Name of the Volume to create.
  ----vol-type vol_type_name   Name of the type of Volume.
  --catalog catalog_name       Catalog Name for creating the Instance.
  --zone availability_zone     Availability Zone of the Instance.
  --instances number           Number of Instances to create ( 1 for single Instance ).
  --lease lease_days           Lease days of the Instance.
  --flavor flavor              Flavor for the Instance.
  --size number                Size of the Volume
  --tag tag_name               Tag Name of the Instance.
  --instance instance_name     Instance Name of the requested Instance.
  --user-data file             File containing user data.
  --property key=value         property meta data.
  --list all                   List the instances of a user.
  --expiry list                List the instances of a user with expiry time.
  --destroy instance_name      Instance Name to destroy Instance.
  --expire instance_name       Instance Name to view expired Instance.
  --reset instance_name        Instance Name to reset the Instance.
  --extend number              Number of days to change lease of Instance.
  --flag flag                  Value for lease extend. options allowed ( d | h ) d for days, h for hours.
  --status state               Change status of instance. options allowed ( active | error ).
  --reboot instance_name       Instance Name to reboot the Instance.
  --shutdown instance_name     Instance Name to shutdown the Instance.
  --suspend instance_name      Instance Name to suspend the Instance.
  --resume instance_name       Instance Name to resume the Instance.
  --poweron instance_name      Instance Name to poweron the Instance.
  --poweroff instance_name     Instance Name to poweroff the Instance.
  --pause instance_name        Instance Name to pause the Instance.
  --unpause instance_name      Instance Name to unpause the Instance.
  --changelease instance_name  Instance Name to changelease of the Instance.
  --volume-attach volume       Volume id/name to be attached.
  --device device              Device id/name of device to be attached.
  --volume-detach volume       Volume id/name to be detached.
  --volume-update volume       Volume id/name to be updated.
  --attachment attachment      Attachment Id.
  --description description    Description of the Volume.
  -h --help                    Show this screen.
  --version                    Show version.

Examples:

- LOGIN:

expostack login --region SCL1 --project "ITOps" --username firstname.lastname@mydomain.com

- CREATE:

 expostack create --region SCL1 --name vmname --catalog catalog_name --instances 1 --lease 7 --flavor micro --tag 'my VM' --user-data file.txt --property 'type=node,mode=external'

- CREATE Volume:

 expostack create --region SCL1 --vol-name my_vol_name --vol-type Tier3-ISCSI-Storage --lease 7 --property 'type=node,mode=external'

- STATUS : SINGLE INSTANCE

expostack status --region SCL1 --instance viexpostack

- STATUS : ALL INSTANCES

expostack status --region SCL1 --list all

- STATUS : EXPIRY OF INSTANCES

expostack status --region SCL1 --expiry list

- SUSPEND:

expostack operate --region SCL1 --suspend viexpostack

- RESUME:

expostack operate --region SCL1 --resume viexpostack

- PAUSE:

expostack operate --region SCL1 --pause viexpostack

- POWER ON:

expostack operate --region SCL1 --poweron viexpostack

- POWER OFF:

expostack operate --region SCL1 --poweroff viexpostack

- SHUTDOWN:

expostack operate --region SCL1 --shutdown viexpostack

- DESTROY:

expostack operate --region SCL1 --destroy viexpostack

- EXPIRE:

expostack operate --region SCL1 --expire viexpostack

- CHANGE LEASE : DAYS

expostack operate --region SCL1 --changelease viexpostack --extend 9 --flag d

- CHANGE LEASE : HOURS

expostack operate --region SCL1 --changelease viexpostack --extend 1 --flag h

- REBOOT:

expostack operate --region SCL1 --reboot viexpostack

- PAUSE:

expostack operate --region SCL1 --pause viexpostack

- UN PAUSE:

expostack operate --region SCL1 --unpause viexpostack

- RESET : STATE TO ACTIVE

expostack operate --region SCL1 --reset viexpostack --status active

- RESET : STATE TO ERROR

expostack operate --region SCL1 --reset viexpostack --status error

- META DATA SET:
expostack operate --region SCL1 --instance viexpostack --property k=v

Help:

- USE THE TABLE DETAILS: IMAGE, FLAVOR, AVAILABILITY ZONES, NETWORK NAME FOR INSTANCE CREATION.
+--------------------------+--------+----------+-------------------------------+--------------+-------------+
| CATALOG NAME             | ACCESS | FLAVOR   | ZONES                         | NETWORK NAME | REGION NAME |
+--------------------------+--------+----------+-------------------------------+--------------+-------------+
| std-aero-prod-la1        | public | x-large  | internal                      | Local        | SCL1        |
| Solaris10 Prod Aero      | public | medium   | SCL1-ZONE2(Solaris only)      | public       | -           |
| Centos7 Datagen Prod     | public | small    | SCL1-ZONE1(Windows and Linux) | Oracle-SCL1  | -           |
| Solaris10 DB Dev Generic | public | large    | nova                          | Dev-SCL1     | -           |
| EDB-ARK_2.0.1            | public | 4x-large | Oracle                        | Prod-SCL1    | -           |
| EDB-ARK_2.0.1            | public | 2x-large | -                             | -            | -           |
| Creative Prod-old1       | public | micro    | -                             | -            | -           |
| Solaris10 Dev Insights   | public | -        | -                             | -            | -           |
| Solaris10 Dev Analytics  | public | -        | -                             | -            | -           |
| Ubuntu Dev Creative      | public | -        | -                             | -            | -           |
| Solaris10 Dev TFR        | public | -        | -                             | -            | -           |
| Windows Server 2012 R2   | public | -        | -                             | -            | -           |
| Solaris10 Dev Generic    | public | -        | -                             | -            | -           |
| Ubuntu-dev-kubernetes    | public | -        | -                             | -            | -           |
| CentOS7 Dev Generic      | public | -        | -                             | -            | -           |
| Debian Dev Generic       | public | -        | -                             | -            | -           |
| Ubuntu Dev Generic       | public | -        | -                             | -            | -           |
| CentOS Dev Datagen       | public | -        | -                             | -            | -           |
| CentOS Dev Aero          | public | -        | -                             | -            | -           |
+--------------------------+--------+----------+-------------------------------+--------------+-------------+

+---------------------------------+--------+----------+------------------------------+--------------+-------------+
| CATALOG NAME                    | ACCESS | FLAVOR   | ZONES                        | NETWORK NAME | REGION NAME |
+---------------------------------+--------+----------+------------------------------+--------------+-------------+
| CentOS Dev Aero                 | public | large    | internal                     | public       | LA1         |
| Creative Dev                    | public | 2x-large | LA1-ZONE1(Windows and Linux) | Dev-LA1      | -           |
| Solaris10 Dev TFR               | public | 4x-large | LA1-ZONE2(Solaris only)      | Oracle-LA1   | -           |
| CentOS7 Dev Generic             | public | small    | LA1-ZONE3(Oracle DB)         | Prod-LA1     | -           |
| CentOS Dev Datagen              | public | x-large  | -                            | -            | -           |
| Solaris10 Dev Generic           | public | micro    | -                            | -            | -           |
| Debian Dev Generic              | public | medium   | -                            | -            | -           |
| Ubuntu Dev Generic              | public | -        | -                            | -            | -           |
| Solaris10 Dev Insights          | public | -        | -                            | -            | -           |
| Solaris10 Dev Analytics         | public | -        | -                            | -            | -           |
| ubuntu-dev-kubernetes           | public | -        | -                            | -            | -           |
| CentOS Dev Creative             | public | -        | -                            | -            | -           |
| ubuntu-dev-kubernetes-old       | public | -        | -                            | -            | -           |
| vicreativedevtest-snap          | public | -        | -                            | -            | -           |
| vivm-solaris-dev-generic1-snap  | public | -        | -                            | -            | -           |
| vivm-solaris-dev-insights1-snap | public | -        | -                            | -            | -           |
| Creative Prod                   | public | -        | -                            | -            | -           |
| watcher-image                   | public | -        | -                            | -            | -           |
| ubuntu-dev-kubernetes-old       | public | -        | -                            | -            | -           |
| Ubuntu Dev Generic-old          | public | -        | -                            | -            | -           |
| Debian Dev Generic-old          | public | -        | -                            | -            | -           |
| Windows Server 2012 R2          | public | -        | -                            | -            | -           |
+---------------------------------+--------+----------+------------------------------+--------------+-------------+
"""

from inspect import getmembers, isclass

from docopt import docopt

try:
    from . import __version__ as VERSION
except ValueError:
    VERSION = '1.0.0'

def main():
    """Main CLI entrypoint."""
    import commands
    options = docopt(__doc__, version=VERSION)

    # Here we'll try to dynamically match the command the user is trying to run
    # with a pre-defined command class we've already created.
    for k, v in options.iteritems():
        if hasattr(commands, k) and v:
            module = getattr(commands, k)
            commands = getmembers(module, isclass)
            command = [command[1] for command in commands if command[0] != 'Base'][0]
            command = command(options)
            command.run()

