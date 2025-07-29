# myproject/setup.py

from setuptools import setup, find_packages

setup(
    name="vecx",
    version="0.32.7b1",
    packages=find_packages(),
    package_data={
        '': ['libvx/*'],  # Include all files in the libvx directory
    },
    install_requires=[
        # List your dependencies here
        "requests>=2.28.0",
    ],
    author="LaunchX Labs",
    author_email="vineet@launchxlabs.ai",
    description="Encrypted Vector Database for Secure and Fast ANN Searches",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://vectorxdb.ai",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
