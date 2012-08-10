#!/usr/bin/env bash
osname="`uname`"

rm -rf build/

#### FreeBSD
if [ "$osname" == "FreeBSD" ]
then
    echo "Installing subget for FreeBSD..."
    mkdir /tmp/subget
    cp -r ./* /tmp/subget/

    export FTP_PASSIVE_MODE=1

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
    sed 's/\#\!\/usr\/bin\/python/\#\!\/usr\/local\/bin\/python/g' subget.py > /tmp/subget/subget.py
    chmod +x /tmp/subget/subget.py

    # setup.py
    sed 's/\#\!\/usr\/bin\/python/\#\!\/usr\/local\/bin\/python/g' setup.py > /tmp/subget/setup.py
    chmod +x /tmp/subget/setup.py

    # subget.desktop
    sed 's/\/usr\/bin\/subget/\/usr\/local\/bin\/subget/g' usr/share/applications/subget.desktop > /tmp/subget/usr/share/applications/subget.desktop

    # menu/subget
    sed 's/\/usr\/bin\/subget/\/usr\/local\/bin\/subget/g' usr/share/menu/subget > /tmp/subget/usr/share/menu/subget

    # KDE4 integration
    sed 's/\/usr\/bin\/subget/\/usr\/local\/bin\/subget/g' usr/share/subget/fm-integration/kde4.desktop > /tmp/subget/usr/share/subget/fm-integration/kde4.desktop
    sed 's/\/usr\/bin\/subget/\/usr\/local\/bin\/subget/g' usr/share/subget/fm-integration/kde4-wws.desktop > /tmp/subget/usr/share/subget/fm-integration/kde4-wws.desktop

    cd /tmp/subget
    python ./setup.py install
    cp -r usr /
    msgfmt usr/share/subget/locale/pl/LC_MESSAGES/subget-src.po -o usr/share/subget/locale/pl/LC_MESSAGES/subget.mo
    cp subget.py /usr/local/bin/subget
    chmod +x /usr/local/bin/subget
    echo "Installation done."

    exit
fi

#### Linux
if [ "$osname" == "Linux" ]
then
    echo "Installing subget for Linux..."
    ./setup.py install
    cp -r usr /
    msgfmt usr/share/subget/locale/pl/LC_MESSAGES/subget-src.po -o usr/share/subget/locale/pl/LC_MESSAGES/subget.mo
    cp subget.py /usr/bin/subget
    chmod +x /usr/bin/subget 
    echo "Installation done."
    exit
fi
