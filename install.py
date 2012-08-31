#!/usr/bin/env python
import os, sys, subprocess, getopt, StringIO

class subgetInstaller:
    """ Subget commandline installer, just run it as root to install Subget to your system or run as regular user to install to chrooted directory (eg. for packaging) """

    pyVersions = dict()
    distCheckCMD = "from distutils.sysconfig import get_python_lib; print(get_python_lib())" # command to check python dist directory
    chroot = ""
    #chroot = "/tmp/test"
    tmp = "/tmp/subget-chroot"
    subgetDir = "./"
    destOS = ""
    os = ""
    osPKG = ""
    installDependencies = False

    packages = dict()
    packages['py26-gtk'] = {'ebuild': 'dev-python/pygtk', 'pkg': 'py26-gtk', 'pacman': 'pygtk', 'deb': 'python-gtk2'}
    packages['py26-dbus'] = {'ebuild': 'dev-python/dbus-python', 'pkg': 'py26-dbus', 'pacman': 'python2-dbus', 'deb': 'python-dbus'}
    packages['p7zip'] = {'ebuild': 'app-arch/p7zip', 'pkg': 'p7zip', 'pacman': 'p7zip', 'deb': 'p7zip-full'}
    packages['gettext'] = {'ebuild': 'sys-devel/gettext', 'pkg': 'gettext', 'pacman': 'gettext', 'deb': 'gettext-base'}

    def usage(self):
        print("install.py -[short GNU option] [value] --[long GNU option]=[value]")
        print("\nUsage:\n")
        print("--help, -h (this message)")
        print("--chroot, -c (where to install files; optional)")
        print("--destination-os, -d (which OS type will be using installed files, supported: FreeBSD, Linux; optional)")
        print("--dependencies (try install Subget dependencies; supports Debian, Ubuntu, Linux Mint, Arch Linux, Gentoo and FreeBSD; disabled by default; optional)")


    def getopt(self):
        try:
            opts, args = getopt.getopt(sys.argv[1:], "hc:d:", ["help", "chroot=", "destination-os=", "dependencies"])
        except getopt.GetoptError as err:
            print("Error: "+str(err)+", Try --help for usage\n\n")
            self.usage()
            sys.exit(2)

        for o, a in opts:
            if o in ('-h', '--help'):
                 self.usage()
                 sys.exit(2)

            if o in ('-c', '--chroot'):
                if not os.path.isdir(a):
                    print("Error: chroot directory does not exists")
                    sys.exit(1)

                self.chroot = a

            if o in ('-d', '--destination-os'):
                if a == "Linux" or a == "FreeBSD":
                    self.destOS = a

            if o in '--dependencies':
                self.installDependencies = True

        self.main()

    def dictValueExists(self, dictionary, value):
        for key in dictionary:
            if dictionary[key] == value:
                return True

    def detectPythonVersions(self):
        """ Detect multiple versions of python to build Subget libraries """

        if self.os == "Linux":
            path = "/usr/bin/"
        else:
            path = "/usr/local/bin/"

        files = os.listdir(path)

        print("# Detecting avaliable python versions for "+self.os+", this may take a second...")

        # all files with "python" but "-config" and "-wrapper" in name
        for file in files:
            if "python" in file and not "-config" in file and not "-wrapper" in file:
            
		try:
		    # get site-packages directory for this python version
		    distDir = subprocess.check_output([path+file, "-c", self.distCheckCMD], stderr=open("/dev/null", "w")).replace("\n", "",)
		except subprocess.CalledProcessError:
		    continue # if non-python binary found (eg. dh_python2)
		  		  
                # Fix for FreeBSD
                if not os.path.isdir(distDir):
                    distDir = distDir.replace("/usr/lib/", "/usr/local/lib/")

                # if previous fix not fixed problem we must skip this python version
                if not os.path.isdir(distDir):
                    continue

                # clean doubled entries
                if self.dictValueExists(self.pyVersions, distDir):
                    continue

                self.pyVersions[path+file] = distDir
                print(path+file+" => "+distDir)


    def detectOS(self):
        """ Detect supported operating systems """

        osName = subprocess.check_output("uname").replace("\n", "")

        if osName == "Linux" or self.os == "FreeBSD":
            self.os = osName
        else:
            self.os = "FreeBSD" # here should be other OS'es like OpenBSD, NetBSD... they can be recognized as FreeBSD (/usr/local instead of /usr/)

        if self.destOS == "":
            self.destOS = self.os

    def osSystem(self, command):
        print("> "+command)
        os.system(command)

    def compileLibraries(self):
        """ Compile Subget libraries using various python versions """

        print("\n# Compiling libraries...")

        for python in self.pyVersions:
            self.osSystem(python + " ./setup.py install --home="+self.tmp)
            self.osSystem("mkdir -p "+self.tmp+"/"+self.pyVersions[python])
            self.osSystem("cp -r "+self.tmp+"/lib/python/* "+self.tmp+"/"+self.pyVersions[python]+"/")
            self.osSystem("rm -rf "+self.tmp+"/lib")

    def compileLanguages(self, prefix=''):
        """ Compile GNU Gettext translations to binary files """

        print("Compiling translations to binary files...")
        localeDir = "usr/share"

        languages = os.listdir(prefix+"/"+localeDir+"/subget/locale")

        for locale in languages:
            self.osSystem("msgfmt "+prefix+"/"+localeDir+"/subget/locale/"+locale+"/LC_MESSAGES/subget-src.po -o "+prefix+"/"+localeDir+"/subget/locale/"+locale+"/LC_MESSAGES/subget.mo")

    def main(self):
        self.detectOS()
        self.detectPythonVersions()
        self.detectPackageManager()

        if self.chroot is not "":
            self.osSystem("mkdir "+self.tmp)

        if self.destOS == "Linux":
            self.linuxInstall()
        elif self.destOS == "FreeBSD":
            self.bsdInstall()

        # if not using chroot let Subget will be installed in root directory
        if self.chroot == "":
            self.chroot = "/"

        print("# Copying files to destination...")
        self.osSystem("cp -r "+self.tmp+"/* "+self.chroot)

        # Cleanup
        print("# Cleaning up...")
        self.osSystem("rm -rf "+self.tmp)



    def detectPackageManager(self):
        if os.path.isfile("/usr/bin/apt-get"):
            self.osPKG = "deb"
            self.pkgCommand = "/usr/bin/apt-get install -y %package%"
        elif os.path.isfile("/usr/sbin/pkg_add"):
            self.osPKG = "pkg"
            self.pkgCommand = "/usr/sbin/pkg_add -rv %package%"
        elif os.path.isfile("/usr/bin/emerge"):
            self.osPKG = "ebuild"
            self.pkgCommand = "/usr/bin/emerge %package%"
        elif os.path.isfile("/usr/bin/pacman"):
            self.osPKG = "pacman"
            self.pkgCommand = "pacman -S %package%"
        else:
            self.pkgCommand = ""

    def installPackage(self, package):
	""" Install package using system's package manager """

        if self.os == "FreeBSD":
            os.putenv("FTP_PASSIVE_MODE", "1")

        if self.pkgCommand is not "":
            self.osSystem(self.pkgCommand.replace("%package%", self.packages[package][self.osPKG]))


    def linuxInstall(self):
        print("# Installing Subget for Linux...")

        if self.installDependencies == True and self.os == "Linux":
            print("# Checking dependencies...")
            if not os.path.isfile("/usr/bin/7z"):
                self.installPackage("p7zip")

            if not os.path.isfile("/usr/bin/msgfmt"):
                self.installPackage("gettext")

        print("# Copying files...")

        self.osSystem("mkdir -p "+self.tmp+"/usr/bin")
        self.osSystem("cp -r ./usr "+self.tmp+"/")

        # Copy executable files
        self.osSystem("cp subget.py "+self.tmp+"/usr/bin/subget")
        self.osSystem("cp subget-translator.py "+self.tmp+"/usr/bin/subget-translator")

        # Make it executable
        self.osSystem("chmod +x "+self.tmp+"/usr/bin/subget")
        self.osSystem("chmod +x "+self.tmp+"/usr/bin/subget-translator")

        self.compileLibraries()
        self.compileLanguages(self.tmp)

        print("Installation done.")

    def bsdInstall(self):
        self.linuxInstall()

        if self.installDependencies == True and self.os == "FreeBSD":
            print("# Checking dependencies...")
            if not os.path.isfile("/usr/local/bin/7z"):
                self.installPackage("p7zip")

            if not os.path.isfile("/usr/local/bin/msgfmt"):
                self.installPackage("gettext")

            if not os.path.isfile("/usr/local/lib/python2.6/site-packages/dbus/__init__.pyc"):
                self.installPackage("py26-dbus")

            if not os.path.isfile("/usr/local/lib/python2.6/gtk-2.0/gtk/__init__.pyc"):
                self.installPackage("py26-gtk")

        print("# Installing Subget for BSD...")

        self.osSystem("mkdir "+self.tmp+"/usr/local")
        self.osSystem("mv "+self.tmp+"/usr/bin "+self.tmp+"/usr/local/bin")

        self.osSystem("sed 's/\/usr\/bin\/subget/\/usr\/local\/bin\/subget/g' "+self.subgetDir+"/usr/share/applications/subget.desktop > "+self.tmp+"/usr/share/applications/subget.desktop")
        self.osSystem("sed 's/\/usr\/bin\/subget/\/usr\/local\/bin\/subget/g' "+self.subgetDir+"/usr/share/menu/subget > "+self.tmp+"/usr/share/menu/subget")
        self.osSystem("sed 's/\/usr\/bin\/subget/\/usr\/local\/bin\/subget/g' "+self.subgetDir+"/usr/share/subget/fm-integration/kde4.desktop > "+self.tmp+"/usr/share/subget/fm-integration/kde4.desktop")
        self.osSystem("sed 's/\/usr\/bin\/subget/\/usr\/local\/bin\/subget/g' "+self.subgetDir+"/usr/share/subget/fm-integration/kde4-wws.desktop > "+self.tmp+"/usr/share/subget/fm-integration/kde4-wws.desktop")

        print("BSD integration installation done.")
        

        

installer = subgetInstaller()
installer.getopt()
