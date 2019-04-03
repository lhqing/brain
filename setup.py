from setuptools import setup, find_packages

allen_version = '0.1.1'

setup(
    name='allen',
    version=allen_version,
    author='Hanqing Liu',
    author_email='hanliu@salk.edu',
    packages=find_packages(),
    description='A package for processing and analyzing Allen atlas data.',
    long_description=open('README.md').read(),
    include_package_data=True,
    package_data={
        '': ['*.nrrd', '*.tsv', '*.csv', '*.json'],
    },
    install_requires=['pandas', 'numpy', 'scipy', 'allensdk', 'matplotlib'],
)

if __name__ == '__main__':
    f = open("allen/__init__.py", 'a')
    f.write(f"__version__ = '{allen_version}'\n")
    f.close()
