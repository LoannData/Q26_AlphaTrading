import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()


setuptools.setup(
     name='q26_alphatrading',  
     version='0.1.1',
     packages=setuptools.find_packages(exclude=['test*', 'example*']),
     #install_requires=['numpy', 'pandas', 'matplotlib', 'importlib'],
     author="Loann Brahimi",
     author_email="loann.brahimi@outlook.fr",
     description="A python package for trading",
     long_description=long_description,
     long_description_content_type="text/markdown",
    #  url="https://github.com/LoannData/Q26_QuanTester.git",
     classifiers=[
         "Programming Language :: Python :: 3",
         "License :: OSI Approved :: MIT License",
         "Operating System :: OS Independent",
     ],
     python_requires=">=3.6",
 )