from setuptools import setup, find_packages

setup(
    name="no-profanity",
    version="1.0.5",
    author="GlitchedLime",
    author_email="gabcosamuel8@gmail.com",
    description="A library using regex manipulation to detect and block profanity in strings.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    url="https://github.com/Gl1tch3dL1m3/no-profanity",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
