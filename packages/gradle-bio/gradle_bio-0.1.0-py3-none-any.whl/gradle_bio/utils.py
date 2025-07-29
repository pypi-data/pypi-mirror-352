import os
import shutil

def get_project_dir(project_name):
    """Get the full path to a specific project directory"""
    from gradle_bio import get_projects_path
    base_path = get_projects_path()
    project_path = os.path.join(base_path, project_name)
    if os.path.exists(project_path):
        return project_path
    return None

def copy_project(project_name, destination):
    """Copy a project directory to a specified destination"""
    project_path = get_project_dir(project_name)
    if not project_path:
        raise ValueError(f"Project '{project_name}' not found")
    
    if not os.path.exists(destination):
        os.makedirs(destination)
    
    dest_path = os.path.join(destination, project_name)
    shutil.copytree(project_path, dest_path)
    return dest_path

def print_project_structure(project_name=None):
    """Print the structure of a project or all projects"""
    from gradle_bio import get_projects_path, list_projects
    
    def print_dir_tree(path, prefix=""):
        items = os.listdir(path)
        items.sort()
        for i, item in enumerate(items):
            is_last = i == len(items) - 1
            item_path = os.path.join(path, item)
            
            # Print the item
            if is_last:
                print(f"{prefix}└── {item}")
                new_prefix = prefix + "    "
            else:
                print(f"{prefix}├── {item}")
                new_prefix = prefix + "|   "
            
            # Recursively print subdirectories
            if os.path.isdir(item_path):
                print_dir_tree(item_path, new_prefix)
    
    base_path = get_projects_path()
    if project_name:
        project_path = os.path.join(base_path, project_name)
        if os.path.exists(project_path):
            print(f"Project: {project_name}")
            print_dir_tree(project_path)
        else:
            print(f"Project '{project_name}' not found")
    else:
        projects = list_projects()
        print(f"Available projects in {base_path}:")
        for project in projects:
            print(f"- {project}")

