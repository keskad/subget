#!/bin/bash
if [ ! -f /usr/share/alang/python/alang.py ]
then
	./install-dependencies.sh
fi

echo "Installing Subget..."
cp subget.py /usr/bin/subget
chmod +x /usr/bin/subget
cp usr/share/subget /usr/share/subget -R
cp usr/share/alang /usr/share/alang -R
echo "Subget installed." 
