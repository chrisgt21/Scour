from setuptools import setup

setup(
    name='scour',
    version='1.0',
    py_modules=['scour'],
    install_requires=[
        'Click',
    ],
    entry_points='''
        [console_scripts]
        scour=scour:cli
    '''
)