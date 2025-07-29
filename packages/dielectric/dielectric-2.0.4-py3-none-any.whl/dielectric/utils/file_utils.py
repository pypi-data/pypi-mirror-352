
# https://datagy.io/list-files-os-glob/
# https://stackoverflow.com/questions/3094659/editing-elements-in-a-list-in-python
# https://realpython.com/working-with-files-in-python/
# https://thispointer.com/python-how-to-get-list-of-files-in-directory-and-sub-directories/
# https://www.techbeamers.com/python-list-all-files-directory/
# https://stackoverflow.com/questions/3207219/how-do-i-list-all-files-of-a-directory
# https://realpython.com/python-pathlib/
# https://www.holisticseo.digital/python-seo/list-files/
# https://stackoverflow.com/questions/39909655/listing-of-all-files-in-directory
# https://zetcode.com/python/pathlib/
# https://stackabuse.com/python-list-files-in-a-directory/
# https://www.digitalocean.com/community/tutorials/how-to-use-the-pathlib-module-to-manipulate-filesystem-paths-in-python-3
# https://www.digitalocean.com/community/tutorials/how-to-use-the-pathlib-module-to-manipulate-filesystem-paths-in-python-3
# https://stackabuse.com/introduction-to-the-python-pathlib-module/
# https://towardsdatascience.com/10-examples-to-master-python-pathlib-1249cc77de0b
# https://www.codespeedy.com/how-to-iterate-over-files-in-a-given-directory-in-python/
# https://pbpython.com/pathlib-intro.html
# https://stackabuse.com/python-list-files-in-a-directory/  ## yield generator
# https://www.journaldev.com/32158/python-pathlib-module-14-practical-examples

# importing OS and Glob Libraries
import os
import glob
# importing pathlib library
from pathlib import Path

import pandas as pd
import yaml


def load_config(config_name: str):
    """

    Args:
        config_name (str): config (.yaml) file path and name

    Returns:
        (dict): .yaml file contents
    """
    with open(config_name) as config_file:
        hp = yaml.safe_load(config_file)  # hp = house_parameters
        return hp


# using pathlib
def find_files(dirstr, pattern: str):
    """find all files with given pattern in directory.

    Args:
        dirstr (str or Path):  string with path: ``'C:/Data/yesterday'`` or ``'C:\Data\yesterday'``
        pattern (str): glob-style pattern:
                       ``'**/*'`` all files and directories, recursive \n
                       ``'**/*.txt'`` all text-files, recursive \n
                       ``'*.png'``  all `*`.png files, non-recursive
    Returns:
        (list):        list of files (pathlib.Path objects) according to selection
    """
    p = Path(dirstr).glob(pattern=pattern)
    # files = p
    files = [f for f in p if f.is_file()]
    return files


if __name__ == "__main__":
    # file_path = r'\\10.77.55.1\ProjectFolder\SU1002_MMIP_WP_TESTCENTRUM\FIELD DATA\Ferroli Field Test\rvlmodbuslogv5'
    file_path = r'C:\Users\PaulvanKan\surfdrive\PvKCC\DielectricSpectroscopy\NaCl - meas2012'
    # Example 0: using pathlib (see function find_files)
    # using pathlib is the preferred method over using os and glob
    file_list = find_files(file_path, '*.txt')
    # print(type(file_list))
    for f in file_list:
        print(f, type(f))

    # Example 1: using os.listdir
    # returns a List of all file names in a directory (only names, no path)
    file_list = os.listdir(file_path)
    for f in file_list:
        print(f)

    # Example 2: using os.walk
    # returns All Files in a Directory and all Sub-directories
    files_list = []
    for root, directories, files in os.walk(file_path):
        for name in files:
            files_list.append(os.path.join(root, name))
    # optionally select only files, discard folders from list
    files_list[:] = [f for f in files_list if os.path.isfile(f)]
    print(files_list)

    # Example 3: using glob.glob
    file_list = glob.glob(file_path + "/*.txt")
    for f in file_list:
        print(f)
