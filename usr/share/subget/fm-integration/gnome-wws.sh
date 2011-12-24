#!/usr/bin/env bash
if [ -e "/usr/bin/subget" ] # Linux
then
    /usr/bin/subget -w `pwd`/$1
else # FreeBSD
    /usr/local/bin/subget -w `pwd`/$1
fi
