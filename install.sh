#!/bin/bash
osname="`uname`"

if [ "$osname" == "FreeBSD" ]
then
    if [ "$IN_BSD_SCRIPT" != "1" ]
    then
        bash bsd-install.sh
        exit
    fi
fi

./setup.py install
msgfmt usr/share/subget/locale/pl/LC_MESSAGES/subget-src.po -o usr/share/subget/locale/pl/LC_MESSAGES/subget.mo
cp -r usr /
cp subget.py /usr/bin/subget
chmod +x /usr/bin/subget 
