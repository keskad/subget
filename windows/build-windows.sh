#!/bin/sh
rm /home/webnull/Praca/python/subget/setup.exe
rm /home/webnull/Praca/python/subget/setup.exe
/usr/lib/virtualbox/VirtualBox --startvm "Subget on windows" &

while [ True ]
do
	sleep 1

	if [ -f /home/webnull/Praca/python/subget/setup.exe ]
	then
		/usr/lib/virtualbox/VBoxManage controlvm "Subget on windows" acpipowerbutton
		break
	fi
done
