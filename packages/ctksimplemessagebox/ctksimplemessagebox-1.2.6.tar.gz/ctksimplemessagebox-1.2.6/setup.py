from setuptools import setup, find_packages

setup(
    name='ctksimplemessagebox',
    version='1.2.6',
    author='Scott',
    author_email='ctksimplemessagebox@gmail.com',
    description='Python Messagebox to display current Infos or Errors.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    packages=find_packages(),
    package_data={
        '': ['MessageBoxIcons/*.ico'],
    },
    include_package_data=True,
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
