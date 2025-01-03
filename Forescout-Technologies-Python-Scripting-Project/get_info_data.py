import os
import json
import shutil
from subprocess import PIPE, run
import sys


INFO_DIR_PATTERN = "info" # What we're looking for in the directories, ie directories that have "info" in the name
INFO_CODE_EXTENSION = ".go" # What we're looking for to compile, ie files that have ".go" in the name (.go files)
INFO_COMPILE_COMMAND = ["go", "build"] 


def find_all_info_paths(source): 
    """
    Takes as argument the source directory, the directory we will be searching

    Returns all paths with the sub-directories that have the string "info" in them
    """
    info_paths = [] # List of full paths that have "info" in them

    for root, dirs, files in os.walk(source): # Recursively looks through "data", ie enters data, then the for loop below checks all directories in data
        for directory in dirs:
            if INFO_DIR_PATTERN in directory.lower():
                path = os.path.join(source, directory) # Creates path that appends directory to source, something like "C://users/Robin/desktop/python-scripting-project-main/data/forescout_technologies_info"
                info_paths.append(path)

        break

    return info_paths


def get_name_from_paths(paths, to_strip):
    """
    Takes as arguments the paths and what should be taken off the path, such as "forescout_technologies_info" and "info"

    Returns the directory names after having been stripped, such as "forescout_technologies"
    """
    new_names = []
    for path in paths:
        _, dir_name = os.path.split(path) # We do not specify where we're splitting by because default is to split between last part of path and rest
        new_dir_name = dir_name.replace(to_strip, "") # Replaces "_info" with ""
        new_names.append(new_dir_name)

    return new_names


def create_dir(path):
    """
    Takes as argument a path name

    Creates the path if it does not already exist
    """
    if not os.path.exists(path): # os.path.exists checks if the path that is given does indeed exist
        os.mkdir(path) # mkdir is "make directory"


def copy_and_overwrite(source, dest):
    """
    Takes as arguments source path and destination path, destination path can or cannot exist

    Deletes anything in destination if anything in destination exists, then takes a copy of source and puts it in destination
    """
    if os.path.exists(dest):
        shutil.rmtree(dest) # rmtree stands for remove tree, basically a recursive delete, deletes everything inside that path
    shutil.copytree(source, dest)


def make_json_metadata_file(path, info_dirs):
    """
    Takes as argument path to put json data and new info directories

    Puts newly created json data into file in path
    """
    data = {
        "infoNames": info_dirs,
        "numberOfInfos": len(info_dirs)
    }

    with open(path, "w") as f: # with is good because it automatically closes file after, and "w" writes to file and overrides anything currently in file
        json.dump(data, f)


def compile_info_code(path):
    """
    Takes as argument path
    
    Compiles all files in that path that end in .go, ie all go files
    """
    code_file_name = None
    for root, dirs, files in os.walk(path): # Has root, dirs, files because root is root, directories is a list of directories, and files is a list of files
        for file in files:
            if file.endswith(INFO_CODE_EXTENSION):
                code_file_name = file
                break

        break

    if code_file_name is None:
        return

    command = INFO_COMPILE_COMMAND + [code_file_name]
    run_command(command, path) # go, build, file_name, path, tells us that we're compiling in go, that we need to build file, what the file name is, and the path to execute the command


def run_command(command, path):
    """
    Takes as arguments a command to run and the path that command should be run in
    
    Runs the command in the OS
    """
    cwd = os.getcwd() # Storing cwd so we can change back to it later
    os.chdir(path) # chdir means change directory, ie changing our working directory to path

    result = run(command, stdout=PIPE, stdin=PIPE, universal_newlines=True) # PIPE allows us to send input to standard input and read from standard output
    print("compile result", result)

    os.chdir(cwd)

def main(source, target):
    cwd = os.getcwd() # Gets current working directory
    source_path = os.path.join(cwd, source) # Creates source path by concatenating source on cwd
    target_path = os.path.join(cwd, target) # Same as above except target path

    info_paths = find_all_info_paths(source_path)
    new_info_dirs = get_name_from_paths(info_paths, "_info")

    create_dir(target_path)

    for src, dest in zip(info_paths, new_info_dirs): 
        # zip takes elements from different arrays and combines them in tuple. Example: if [1, 2, 3] and [a, b, c] are passed to zip, 
        #   zip will return [(1, a), (2, b), (3, c)]
        dest_path = os.path.join(target_path, dest) # Creates path with new dir, such as combining /python-scripting/target and /forescout_technologies to make /python-scripting/target/forescout_technologies
        copy_and_overwrite(src, dest_path) # Copies all data in src to all data in dest_path
        compile_info_code(dest_path)

    json_path = os.path.join(target_path, "metadata.json")
    make_json_metadata_file(json_path, new_info_dirs)


if __name__ == "__main__":
    args = sys.argv # Pulling arguments from command line, something like "python get_info_data.py data new_data"
    if len(args) != 3:
        raise Exception("You must pass a source and target directory - only.")

    source, target = args[1:]
    main(source, target)
