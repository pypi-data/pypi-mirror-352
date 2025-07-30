from setuptools import setup, find_packages
import os

def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), "README.md")
    if os.path.exists(readme_path):
        with open(readme_path, "r", encoding="utf-8") as fh:
            return fh.read()
    return "A Python tool for video contour extraction."

setup(
    name="contourvision",  
    version="0.1.6",       
    author="Vilius Bankauskas",    
    author_email="bankauskasvil@gmail.com",  
    description="A Python tool for extracting and visualizing contours in videos.",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/viliusbankauskas/contourvision",
    
    packages=['contourvision'], 

    license="MIT", 

    license_files = ('LICENSE',), 
    
    classifiers=[
        "Development Status :: 3 - Alpha", 
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        # "License :: OSI Approved :: MIT License",  
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Multimedia :: Video",
        "Topic :: Scientific/Engineering :: Image Processing",
        "Topic :: Utilities",
    ],
    
    python_requires=">=3.8",

    install_requires=[
        "opencv-python>=4.0",  
        "numpy>=1.19",         
    ],
    
    project_urls={
        "Bug Tracker": "https://github.com/viliusbankauskas/contourvision/issues",
        "Documentation": "https://github.com/viliusbankauskas/contourvision/blob/main/README.md",
        "Source Code": "https://github.com/viliusbankauskas/contourvision",
    },
)
