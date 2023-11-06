from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    readme = f.read()

setup(
    name='restocks_api_wrapper',
    version='0.1.1',
    packages=find_packages(exclude=("tests",)),
    url='https://github.com/AkiLetschne/restocks_api_wrapper',
    license='MIT',
    author='AkiLetschne',
    description='A unofficial Python wrapper for the Restocks API',
    long_description=readme,
    long_description_content_type="text/markdown",
    install_requires=["requests", "lxml"],
    python_requires='>=3.11',
    classifiers=[
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ],
)
