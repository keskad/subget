#!/usr/bin/env bash
if [ -e "/usr/bin/subget" ] # Linux
then
    /usr/bin/subget `pwd`/$1
else # FreeBSD
    /usr/local/bin/subget `pwd`/$1
fi
