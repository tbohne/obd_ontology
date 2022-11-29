from setuptools import find_packages, setup

__version__ = '0.0.1'
URL = 'https://github.com/tbohne/OBDOntology'

with open('requirements.txt') as f:
    required = f.read().splitlines()

for i in range(len(required)):
    # adapt the repo references for setup.py usage
    if "https" in required[i]:
        pkg = required[i].split(".git")[0].split("/")[-1]
        required[i] = pkg + "@" + required[i]

setup(
    name='obd_ontology',
    version=__version__,
    description='Ontology for capturing knowledge about on-board diagnosis (DTCs).',
    author='Tim Bohne',
    author_email='tim.bohne@dfki.de',
    url=URL,
    download_url=f'{URL}/archive/{__version__}.tar.gz',
    keywords=[
        'ontology',
        'knowledge-graph',
        'knowledge-base'
    ],
    python_requires='>=3.7',
    install_requires=required,
    packages=find_packages(),
    py_modules=['']
    include_package_data=True,
)
