from setuptools import setup, find_packages
import os
import subprocess

def get_version_from_git():
    """Get version from git tags, or default to 0.1.0 if not available"""
    try:
        # Try to get the version from git tag
        git_tag = subprocess.check_output(['git', 'describe', '--tags', '--abbrev=0'], 
                                          stderr=subprocess.STDOUT, 
                                          universal_newlines=True).strip()
        # Remove 'v' prefix if present
        if git_tag.startswith('v'):
            git_tag = git_tag[1:]
        return git_tag
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "0.1.0"  # Default version

# Write version to _version.py
version = get_version_from_git()
version_file_path = os.path.join('diffeomorphic', '_version.py')
with open(version_file_path, 'w') as f:
    f.write(f'__version__ = "{version}"\n')

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(    name="diffeomorphic",
    version=version,
    use_scm_version=True,  # Automatically manage versioning from Git tags
    setup_requires=["setuptools-scm"],  # Required for setuptools-scm versioning
    author="Mohammad Ahsan Khodami",
    author_email="ahsan.khodami@gmail.com",
    description="Diffeomorphic transformations for image and video morphing in psychological experiments",    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/AhsanKhodami/diffeomorphic",
    packages=["diffeomorphic"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        "numpy",
        "matplotlib",
        "pillow",
        "scipy",
        "opencv-python",
    ],    entry_points={
        "console_scripts": [
            "diffeomorphic-image=diffeomorphic.cli:run_diffeomorphic",
            "diffeomorphic-movie=diffeomorphic.cli:run_diffeomorphic_movie",
            "diffeomorphic-warpshift=diffeomorphic.cli:run_diffeomorphic_movie_warpshift",
        ],
    },
)
