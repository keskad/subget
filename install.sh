#!/bin/bash
bash ./install-dependencies.sh
./setup.py install
cp usr / -R
cp subget.py /usr/bin/subget
chmod +x /usr/bin/subget 
