from setuptools import setup, find_packages

setup(
    name="ailine",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "clight",
        
    ],
    entry_points={
        "console_scripts": [
            "ailine=ailine.main:main",  # Entry point of the app
        ],
    },
    package_data={
        "ailine": [
            "main.py",
            "__init__.py",
            ".system/imports.py",
            ".system/index.py",
            ".system/modules/jobs.py",
            ".system/sources/clight.json",
            ".system/sources/logo.ico"
        ],
    },
    include_package_data=True,
    author="Irakli Gzirishvili",
    author_email="gziraklirex@gmail.com",
    description="AILine transforms your (Command-Line) terminal into an AI-powered (AI-Line) terminal. By using AILine, you can gain superpowers that help you manage your system and perform complex workflows in a simple way. AILine has a default action base and develops itself based on your commands.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/IG-onGit/AILine",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
