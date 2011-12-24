#!/usr/local/bin/bash
osname="`uname`"

if [ "$osname" == "Linux" ]
then
    echo "Please use install.sh instead of bsd-install.sh for Linux"
    exit
fi

export FTP_PASSIVE_MODE=1
export IN_BSD_SCRIPT=1

echo "Installing python 2.6..."
pkg_add -rv python26

echo "Installing pygtk..."
pkg_add -rv py26-gtk

echo "Installing python dbus bindings..."
pkg_add -rv py26-dbus

echo "Installing git..."
pkg_add -rv git

echo "Installing p7zip..."
pkg_add -rv p7zip

echo "Installing GNU Gettext..."
pkg_add -rv gettext

echo "Installing subget..."
sed 's/\#\!\/usr\/bin\/python/\#\!\/usr\/local\/bin\/python/g' subget.py > /tmp/subget.py
mv /tmp/subget.py ./subget.py
chmod +x ./subget.py

sed 's/\#\!\/usr\/bin\/python/\#\!\/usr\/local\/bin\/python/g' setup.py > /tmp/setup.py
mv /tmp/setup.py ./setup.py
chmod +x ./setup.py

python ./setup.py install
cp -r usr /
msgfmt usr/share/subget/locale/pl/LC_MESSAGES/subget-src.po -o usr/share/subget/locale/pl/LC_MESSAGES/subget.mo
cp subget.py /usr/bin/subget
chmod +x /usr/bin/subget
echo "Installation done."
