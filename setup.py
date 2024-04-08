from setuptools import setup, find_packages
__version__='0.0'
setup(
    name='aarhusInv',
    author='Paul McLachlan',
    author_email='pm@geo.au.dk',
    packages=find_packages('src'),
    package_dir={'':'src'},
    install_requires=['numpy', 'subprocess', 'time', 'glob', 'pandas'],
    version=__version__,
    license='MIT',
    description='create and read files to interact with aarhus inv',
    python_requires=">=3.8",
)
