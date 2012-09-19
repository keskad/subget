#!/usr/bin/env python
#-*- coding: utf-8 -*-
from distutils.core import setup
from distutils.command.build import build
from distutils.command.install_data import install_data
from distutils.command.install import install
from distutils.dist import Distribution
from xml.dom import minidom
from distutils.log import error, info, warn
import sys
import glob
import subprocess
import shutil
import os

appname = "subget"

w = open("usr/share/"+appname+"/version.xml", "r")
contents = w.read()
w.close()

dom = minidom.parseString(contents)
VERSION = str(dom.getElementsByTagName('version').item(0).firstChild.data)

class Dist(Distribution):
    """ Additional commandline arguments """

    global_options = Distribution.global_options + [
       ("without-gettext", None, "Don't build/install gettext .mo files")]

    def __init__ (self, *args):
        self.without_gettext = False
        Distribution.__init__(self, *args)

class BuildData(build):
    def run(self):
        build.run(self)

        # don't build languages if --without-gettext was specified in commandline
        if self.distribution.without_gettext: return
        languages = glob.glob("usr/share/"+appname+"/locale/*/*/*.po")

        for k in languages:
            try:
                mo = k.replace("-src", "")[:-3]
                rc = subprocess.call(['msgfmt', '-o', mo+".mo", k])
                if rc != 0: raise Warning, "msgfmt returned %d" % rc
                info("msgfmt -o "+mo+".mo "+k)
            except Exception as e:
                error("Building gettext files failed. Try setup.py --without-gettext [build|install]")
                error("Error: %s" % str(e))
                sys.exit(1)

class Install(install):
    def run(self):
        shutil.copyfile("subget.py", "/tmp/subget") # small trick to cut off ".py" extension
        shutil.copyfile("subget-translator.py", "/tmp/subget-translator")
        self.distribution.scripts=['/tmp/subget', '/tmp/subget-translator']
        install.run(self)
        os.remove("/tmp/subget-translator")


class InstallData(install_data):
    def run(self):
        files = self.listDirs("usr")

        self.data_files.extend(files)
        install_data.run(self)
        warn("If application wont run try: ln -s /usr/local/share/subget/ /usr/share/subget")

    def listDirs(self, directory):
        # Source: http://mayankjohri.wordpress.com/2008/07/02/create-list-of-files-in-a-dir-tree/
        fileList = []

        for root, subFolders, files in os.walk(directory):
            a = []

            file = None

            for file in files:
                f = os.path.join(root,file)
                a.append(f)

            if file is not None:
                fileList.append((root[4:],a))

        return fileList

setup(name='subget',
      description = "Simple subtitles downloading program",
      long_description = "Subget is an application that supports downloading from many subtitles servers, plugins, multiplatform and international languages.",
      author = "Damian Kęska",
      author_email = "webnull.www@gmail.com",
      version=VERSION,
      license = "GPL",
      package_dir={'': 'src'},      
      packages=['subgetlib', 'subgetcore'],
      distclass=Dist,
      data_files = [],
      cmdclass={
            'build': BuildData,
            'install_data': InstallData,
            'install': Install
          }
     )
