#!/usr/bin/python
import os, sys
sys.path.insert(0, "/tmp/")

if not len(sys.argv) == 3:
    print("You need to specify two arguments. First - path to alang, second - path to gettext locale directory")
    sys.exit(1)


translationName = "subget"

sourceLang = "english"
sourceShort = "en"

destinationLang = "polski"
destinationShort = "pl"

if not os.path.isdir(sys.argv[1]+"/translations/"):
    print("You need to specify path to alang directory in first argument.")
    sys.exit(1)

if not os.path.isdir(sys.argv[1]+"/translations/"+sourceLang):
    print("Cannot find directory "+sys.argv[1]+"/translations/"+sourceLang)
    sys.exit(1)

print("Source language: "+sys.argv[1]+"/translations/"+sourceLang)
os.system("cp "+sys.argv[1]+"/translations/"+sourceLang+"/"+translationName+".py /tmp/"+translationName+"_"+sourceLang+".py")
exec("import "+translationName+"_"+sourceLang+" as alang")
t = alang.alangINC()
sourceStrings = t.return_array()

if not os.path.isdir(sys.argv[1]+"/translations/"+destinationLang):
    print("Cannot find directory "+sys.argv[1]+"/translations/"+destinationLang)
    sys.exit(1)

print("Destination language: "+sys.argv[1]+"/translations/"+destinationLang)
os.system("cp "+sys.argv[1]+"/translations/"+destinationLang+"/"+translationName+".py /tmp/"+translationName+"_"+destinationLang+".py")
exec("import "+translationName+"_"+destinationLang+" as alang")
t = alang.alangINC()
destStrings = t.return_array()

if not os.path.isdir(sys.argv[2]):
    print("You need to specify path to locale files as second argument")
    sys.exit(1)

if not os.path.isdir(sys.argv[2]+"/"+destinationShort):
    os.mkdir(sys.argv[2]+"/"+destinationShort)

if not os.path.isdir(sys.argv[2]+"/"+destinationShort+"/LC_MESSAGES"):
    os.mkdir(sys.argv[2]+"/"+destinationShort+"/LC_MESSAGES")

if not len(sourceStrings) == len(destStrings):
    print("Source translations string count doesnt match destination strings count.")
    sys.exit(1)

translatedMO = "# Converted using alang_to_gettext.py from Subget tools\n\n"

i=0
while i < len(sourceStrings):
    translatedMO += "msgid \""+sourceStrings[i]+"\"\nmsgstr \""+destStrings[i]+"\"\n\n"
    i=i+1

translated = open(sys.argv[2]+"/"+destinationShort+"/LC_MESSAGES/"+translationName+"-src.po", "wb")
translated.write(translatedMO)
translated.close()
print("Conversion done!")
