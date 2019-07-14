import os
import sys
import hashlib
import shutil
from PIL import Image

def hashfile(path, blocksize = 65536):
    afile = open(path, 'rb')
    hasher = hashlib.md5()
    buf = afile.read(blocksize)
    while len(buf) > 0:
        hasher.update(buf)
        buf = afile.read(blocksize)
    afile.close()
    return hasher.hexdigest()

def findDup(parentFolder):
    #Dupplicates in format {hash:[names]}
    dups = {}
    for dirName, subdirs, fileList in os.walk(parentFolder):
        print('Scanning {}...'.format(dirName))
        for filename in fileList:
            #Get the path to the file
            path = os.path.join(dirName, filename)
            #Calculate hash
            file_hash = hashfile(path)
            # Add or append the file path
            if file_hash in dups:
                dups[file_hash].append(path)
            else:
                dups[file_hash] = [path]

    ####### RETURN ONLY DUPLICATES, NOT THE WHOLE DIRECTORY
    for k in list(dups.keys()):
        if len(dups[k])<=1:
            dups.pop(k, None)
    return dups

def joinDicts(dict1, dict2):
    for key in dict2.keys():
        if key in dict1:
            dict1[key] = dict1[key] + dict2[key]
        else:
            dict1[key] = dict2[key]

def printResults(dict1):
    results = list(filter(lambda x: len(x) > 1, dict1.values()))
    if len(results) > 0:
        print('Duplicates Found:')
        print('The following files are identical. The name could differ, but the content is identical')
        print('___________________')
        for result in results: #List of lists with duplicate names
            for subresult in result: #This is the duplicate file
                print('\t\t%s' % subresult)
            print('___________________') 
    else:
        print('No duplicate files found.')

if __name__ == '__main__':
    if len(sys.argv) > 1:
        dups = {}
        folders = sys.argv[1:]
        for folder in folders:
            os.chdir(folder)
            dirs = [dirs for root, dirs, files in os.walk(folder)]
            # Iterate the folders given
            if os.path.exists(folder):
                # Find the duplicated files and append them to the dups
                joinDicts(dups, findDup(folder))                
                #Create folder to store duplicates
                folder_name = 'duplicates'
                if folder_name in dirs[0]: #Check that the folder doesn't exist
                    j = 1
                    while folder_name in dirs[0]:
                        folder_name = 'duplicates_' + str(j)
                        j += 1
                os.mkdir(folder_name)
                #Move duplicates to folder
                for pics in list(dups.values()): #list of list of keys
                    for pic in pics:
                        if pics.index(pic) != 0: #Ignore the first picture since I want to keep one non duplicate picture outside the "duplicates" folder
                            destination = os.path.join(folder_name, os.path.split(pic)[1])
                            shutil.move(pic, destination)
            else:
                print('{} is not a valid path, please verify'.format(folder))
                sys.exit()
    else:
        print('Usage: python find_duplicates.py folder or python find_duplicates.py folder1 folder2 folder3')
        sys.exit()
    printResults(dups)
