#!/bin/bash
./setup.py install
msgfmt usr/share/subget/locale/pl/LC_MESSAGES/subget-src.po -o usr/share/subget/locale/pl/LC_MESSAGES/subget.mo
cp usr / -R
cp subget.py /usr/bin/subget
chmod +x /usr/bin/subget 
