#!/bin/sh
subget_git="/home/webnull/Praca/python/subget"
vm_name="Subget on windows"

rm "$subget_git/setup.exe" # delete setup.exe file
rm "$subget_git/setup.exe" # make sure its deleted

# start virtual machine - but be sure to add build script to startup
/usr/lib/virtualbox/VirtualBox --startvm "$vm_name" &

while [ True ]
do
	sleep 1

        # check if operation is done (check for setup.exe file)
	if [ -f "$subget_git/setup.exe" ]
	then
		sleep 5
		/usr/lib/virtualbox/VBoxManage controlvm "$vm_name" acpipowerbutton # poweroff machine using ACPI power button
		break
	fi
done
