from setuptools import setup

setup(
    name='cctool',
    version='0.1',
    description='CryptoCompare.com portfolio import command line tool',
    url='https://github.com/m-kus/cctool',
    author='m-kus',
    author_email='44951260+m-kus@users.noreply.github.com',
    license='MIT',
    packages=['cctool'],
    entry_points={
        'console_scripts': ['cctool=cctool.cctool:main'],
    },
    zip_safe=False
)
