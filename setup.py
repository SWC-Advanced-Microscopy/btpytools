from setuptools import setup

setup(
    name='btpytools',
    version='0.1.0',    
    description='A example Python package',
    url='https://github.com/sainsburywellcome/btpytools',
    author='Rob Campbell',
    author_email='rob.campbell@ucl.ac.uk',
    license='GPLv3',
    packages=['btpytools'],
    install_requires=['pyyaml',
                      ],

    classifiers=[
        'Intended Audience :: Science/Research',
        'Operating System :: POSIX :: Linux',        
    ],
)