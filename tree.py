import os
counter_total = 3

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

# Get the current directory path
current_dir_path = os.getcwd()

# Print the folder tree of the current directory
print_folder_tree(current_dir_path)
