#!/bin/bash
echo "Installing dependencies..."
cd /tmp
git clone git://github.com/webnull/alang.git
chmod +x /tmp/alang/install.sh
cd /tmp/alang
/tmp/alang/install.sh
cd /tmp
git clone git://github.com/webnull/alang-py.git
chmod +x /tmp/alang-py/install.sh
cd /tmp/alang-py
/tmp/alang-py/install.sh
echo "Dependencies installed."
