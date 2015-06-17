import os

filelist = os.listdir('.')  # get files in current directory
i=30
for filename in filelist:
    if "door" in filename:  # only process pictures
        newname = "subject02_" + str(i) + ".jpg"
        print(filename + " will be renamed as " + newname)
	i=i+1
        os.rename(filename, newname)
