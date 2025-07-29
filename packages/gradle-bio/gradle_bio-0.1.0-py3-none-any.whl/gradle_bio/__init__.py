# gradle_bio package

def get_projects_path():
    """Return the path to the installed Android project files"""
    import os
    import sys
    import site
    
    # Try to find the projects in site-packages
    for site_dir in site.getsitepackages():
        projects_dir = os.path.join(site_dir, 'gradle_bio_projects')
        if os.path.exists(projects_dir):
            return projects_dir
    
    # If not found, check the development location
    dev_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return dev_path

def list_projects():
    """List all available Android project directories"""
    import os
    projects_path = get_projects_path()
    if os.path.exists(projects_path):
        return [d for d in os.listdir(projects_path) 
                if os.path.isdir(os.path.join(projects_path, d))]
    return []

__version__ = '0.1.0'
