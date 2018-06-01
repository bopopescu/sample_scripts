#!/usr/bin/env bash
exit

# version 2015120300

# This script will verify that the root passwd hash string in the shadow file
# matches this script's version of said string. If it differs then
# it will auto-inject a new root passwd hash string into a copy shadow
# file, and preserve all other entries into the copy, then safely put the copy
# in place while backing up the original

# since this only verifies the hash sting and not the actual passwd it
# will update machines with the correct passwd but a different shadow entry

# options?

# our only function thus far is an error checking printy bailer
function errChk {
  if (( $? )) ; then
    echo "FATAL: Failed to ${TRING}!"
    exit 1
  fi
}

# set new root passwd, escape your dollar signs, or lock yourself out!
NEWP="root:\$6\$.52SQcFJ/f5NaRga\$Im2cZVVpLfWbD6hI/aHNRtDh798ZN6eJnTMqZFvY.df62FXy1qfq1nUQZTo8Zvoh0PsmNydXkUxKwSAVBtLct0:15752:0:99999:7:::"
MODE="000"
LNX="yes"

# Solaris 10 has different form and mode
if [ "$(uname -rs)" == "SunOS 5.10" ]; then
  LNX="no"
  NEWP="root:Bebtx3zYQ5i56:15752::::::"
  MODE="400"

# code for local zones
  if [ "$(zonename)" != "global" ] ; then
# this option sets a different hash string for a local zone
#    NEWP="root:bwrGVjvHp0Ecc:6445::::::"

# this option will exit if not a Solaris Global Zone, so no update:
    echo "FATAL: Must be a Solaris Global Zone!"
    exit 1

# this option will update all local zones from the global zone
#FIX: add the code
#fetch zonenames and paths
#turn build new shadow file code into a function
#operate on all shadow files in loop
#errChk and exit

  fi
fi

# check that we're root
TRING="must be ROOT or use SUDO to run $(basename $0)"
if [ "$LNX" == "no" ]
  then if [ "$(/usr/xpg4/bin/id -u)" != "0" ]
    then echo $TRING
    exit 1
  fi
  else if [ "$LNX" == "yes" ]
    then if [ "$(id | cut -d\( -f1 | cut -d= -f2)" != "0" ]
      then echo $TRING
      exit 1
    fi
  fi
fi

# verify we have the correct hash string set in the shadow file, if so stop
#say okay and exit 0 if head -1 /etc/shadow == $NEWP
TRING="$(head -1 /etc/shadow)"
if [ "$TRING" == "$NEWP" ] ; then
  echo "root passwd hash is up to date."
  exit 0
fi

#FIX: check permissions?

# build new shadow file in /tmp with perms and then the new passwd
FILE="/tmp/$(basename $0).$$"
TRING="create $FILE"
touch $FILE 1>/dev/null 2>&1
errChk

TRING="set mode($MODE) on $FILE"
chmod $MODE $FILE 1>/dev/null 2>&1
errChk

TRING="place new hash string into $FILE"
echo $NEWP > $FILE 2>&1
errChk

# copy remainder of original shadow file
#FIX: this is where to look for multiple root entries in the source file
# or the very embarrassing empty line
TRING="read shadow file"
sed 1d /etc/shadow >> $FILE 2>&1
errChk

TRING="make backup shadow file /etc/shadow.old"
cp /etc/shadow /etc/shadow.old 1>/dev/null 2>&1
errChk

TRING="copy the new shadow file into place"
mv $FILE /etc/shadow 1>/dev/null 2>&1
errChk

echo "root passwd hash updated successfully."
exit 0
