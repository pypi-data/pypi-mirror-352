from setuptools import setup, find_packages
import os
import shutil
from setuptools.command.install import install

# Custom install command to copy Android project files to site-packages
class CustomInstall(install):
    def run(self):
        # Run the standard install
        install.run(self)
        
        # Get the site-packages directory
        site_packages = self.install_lib
        
        # Create the target directory
        target_dir = os.path.join(site_packages, 'gradle_bio_projects')
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
        
        # Copy all Android project directories
        for directory in ['1 check', '2 alert', '3 progress', '4 canvas', '5 intents', 
                         '6 Animations', '7 Menu', '8 Frag', '9 shared', '10 Database']:
            src_dir = os.path.join(os.getcwd(), directory)
            dst_dir = os.path.join(target_dir, directory)
            
            if os.path.exists(src_dir):
                print(f"Copying {directory} to {dst_dir}")
                if os.path.exists(dst_dir):
                    shutil.rmtree(dst_dir)
                shutil.copytree(src_dir, dst_dir)

setup(
    name="gradle-bio",
    version="0.1.0",
    packages=find_packages(),
    cmdclass={
        'install': CustomInstall,
    },
    description="Collection of Android project snippets and templates",
    author="Your Name",
    author_email="your.email@example.com",
    url="https://github.com/yourusername/gradle-bio",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
