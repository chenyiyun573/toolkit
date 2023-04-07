import os
import sys

# Get command line arguments for counter_total and dir_path
try:
    counter_total = int(sys.argv[1])
except IndexError:
    counter_total = 3
try:
    dir_path = sys.argv[2]
except IndexError:
    dir_path = os.getcwd()

def print_folder_tree(dir_path, padding=''):
    """
    Recursively prints the folder tree of the given directory path.
    """
    items = os.listdir(dir_path)
    folders = [item for item in items if os.path.isdir(os.path.join(dir_path, item))]
    files = [item for item in items if os.path.isfile(os.path.join(dir_path, item))]
    counter_folder = 0
    for folder in folders:
        print(padding + folder + '/')
        sub_dir_path = os.path.join(dir_path, folder)
        if len(os.listdir(sub_dir_path)) > 0:
            if folder == folders[-1]:
                print_folder_tree(sub_dir_path, padding + '  ')
            else:
                print_folder_tree(sub_dir_path, padding + '| ')
        counter_folder += 1
        if counter_folder >=counter_total : 
            print(padding + "...")
            break
    counter_file = 0
    for file in files:
        print(padding + file)
        counter_file += 1
        if counter_file>=counter_total:
            print(padding +"...")
            break

# Print the folder tree of the current directory or user-specified directory
print_folder_tree(dir_path)
