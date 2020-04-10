#!/usr/bin/python3
import os
import re
import sys
import asyncio
import requests
import wget
import tarfile
import shutil

wp_projects = "ADD THE PROJECTS LOCATION BASE FOLDER HERE" #The base folder of the project(s)
wp_download = "CREATE A FOLDER INSIDE /wp_automate/" #The base folder of downloaded wordpress 
wp_latest = 'https://wordpress.org/latest.tar.gz' #The latest tar.gz of wordpress

async def scanFolders(baseFolder):
    """This function scan the version.php of every wp projects"""

    for root, dirs, files in os.walk(baseFolder):
        for name in files:
            if os.path.join(root, name).strip().__contains__("wp-includes/version.php"):
                folder = os.path.join(root, name)
                file = open(folder, "r")
                for line in file:
                    if re.search('wp_version', line):
                        elems = re.findall(r'\d+', line.strip())
                        if elems != []:
                            version = '.'.join([str(x) for x in elems])
                            #print(folder ," => ", version)
                            yield folder, version

async def scan_wp():
    """Display the old WP versions"""

    async for folder, old_v in scanFolders(wp_projects):
        async for f,latest_v in scanFolders(wp_download):
            if old_v < latest_v:
                print(folder, old_v, "<" ,latest_v, (old_v<latest_v))

async def download_wp():
    """Download the latest wp zip folder and extract to /extract/ folder"""

    filename = wget.download(wp_latest)
    my_tar = tarfile.open(filename)
    my_tar.extractall('./'+wp_download)
    my_tar.close()


async def upgrade_wp():
    """Upgrade the wordpress projects"""

    root_src_dir = wp_download+'/'+wp_projects #the extracted wordpress

    subfolders = [ f.path for f in os.scandir(wp_projects) if f.is_dir() ]
    for path in subfolders:
        for src_dir, dirs, files in os.walk(root_src_dir):
            dst_dir = src_dir.replace(root_src_dir, path, 1)
            if not os.path.exists(dst_dir):
                os.makedirs(dst_dir)
                
            for file_ in files:
                src_file = os.path.join(src_dir, file_)
                dst_file = os.path.join(dst_dir, file_)

                if os.path.exists(dst_file):
                    # in case of the src and dst are the same file
                    if os.path.samefile(src_file, dst_file):
                        continue

                    # Do not remove /wp-content/ folder
                    # We also need to exclude wp-config.php from removing
                    if dst_file.strip().__contains__("wp-content") is False:
                        os.remove(dst_file)

                # Copy and paste all files
                print("Replacing..", src_file, dst_dir)
                shutil.copy(src_file, dst_dir)



async def main():
    while True:
        try:
            print("#################################################")
            print("###              1 = Download latest WP       ###")
            print("###              2 = Scan projects            ###")
            print("###              3 = Upgrade WP               ###")
            print("###              4 = Exit                     ###")
            print("#################################################")
            options = int(input("Select the choice : "))

            if options == 1:
                await download_wp()
            elif options == 2:
                await scan_wp()
            elif options == 3:
                await upgrade_wp()

        except ValueError:
            print("Error! Invalid option: ",test_number)


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())