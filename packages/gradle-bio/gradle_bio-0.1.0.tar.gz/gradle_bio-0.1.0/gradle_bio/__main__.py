#!/usr/bin/env python

from gradle_bio import get_projects_path, list_projects
from gradle_bio.utils import get_project_dir, print_project_structure
import os
import sys
import argparse

def main():
    """Command line interface for gradle-bio"""
    parser = argparse.ArgumentParser(description='Gradle-Bio - Android Project Templates')
    parser.add_argument('--list', action='store_true', help='List all available projects')
    parser.add_argument('--path', action='store_true', help='Show the path to the installed project files')
    parser.add_argument('--structure', metavar='PROJECT', help='Show the structure of a specific project')
    parser.add_argument('--all-structures', action='store_true', help='Show the structure of all projects')
    
    args = parser.parse_args()
    
    # Default behavior if no arguments provided
    if len(sys.argv) == 1:
        args.list = True
        args.path = True
    
    if args.path:
        projects_path = get_projects_path()
        print(f"Android project files are located at: {projects_path}")
        print()
    
    if args.list:
        projects = list_projects()
        print("Available projects:")
        for project in projects:
            print(f"  - {project}")
        print()
    
    if args.structure:
        print_project_structure(args.structure)
    
    if args.all_structures:
        for project in list_projects():
            print_project_structure(project)
            print()

if __name__ == "__main__":
    main()
