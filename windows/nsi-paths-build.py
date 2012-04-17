#!/usr/bin/python2
import os

commands = ""
originalDirectory = "c:\\Subget\\build\\exe.win32-2.7"

def sortItemsByDirectory(items, directory):
    directories = list()
    allItems = list()

    # first files
    for item in items:
        if os.path.isdir(directory+"\\"+item):
            directories.append(item)
        else:
            allItems.append(item)

    item = ""

    # and then directories
    for item in directories:
       allItems.append(item)

    return allItems 

def generateList(directory):
    global commands, originalDirectory

    items = os.listdir(directory)

    for item in items:
        if os.path.isfile(directory+"\\"+item):
            #print "\n  File "+directory+"\\"+item
            commands += "\n  File "+directory+"\\"+item
            print directory+"\\"+item

    for item in items:
        if os.path.isdir(directory+"\\"+item):
            #print "\n  CreateDirectory "+directory+"\\"+item+"\n  SetOutPath "+directory+"\\"+item
            cd = directory+"\\"+item
            commands += "\n  CreateDirectory "+directory+"\\"+item+"\n  SetOutPath "+cd.replace(originalDirectory, '$INSTDIR')
            print directory+"\\"+item
            generateList(directory+"\\"+item)
            

print "Generating file list..."
generateList(originalDirectory)

#print fileList

print "Opening template..."
Template = open("c:\\Subget\\windows\installer-template.nsi", "rb")
TemplateCode = Template.read().replace("{#INSTALLER_FILES}", commands)
Template.close()

print "Saving installer script..."
Installer = open("c:\\Subget\\windows\\installer.nsi", "wb")
Installer.write(TemplateCode)
Installer.close()
