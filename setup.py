"""
# Create dist files:
pip3 install --upgrade setuptools wheel				# install packages needed to build distribution files
python3 setup.py sdist bdist_wheel					# build package in the dist/ directory

pip3 install dist/pypipe_tools-0.0.xx

python3 -m pip install --user --upgrade twine		# install package needed to upload the distribution

# username and password required: use __token__ and the API token created in your account
python3 -m twine upload --repository-url https://test.pypi.org/legacy/ dist/pypipe_tools-x.x.x*

# after successful upload; install the package with pip
pip3 install -i https://test.pypi.org/simple/ pypipe_tools==x.x.x
"""
from setuptools import setup
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as fh:
    readme_text = fh.read()

setup(name='pypipe_tools',
	version='0.0.1',
	long_description=readme_text,
	long_description_content_type='text/markdown',
	author='The Pipeline Plumbers',
	url='https://github.com/dlanier/pipe_tools',
	classifiers=['License :: OSI Approved :: MIT License', 
	'Programming Language :: Python :: 3.5', 
	'Programming Language :: Python :: 3.6',
	'Programming Language :: Python :: 3.7',
	'Programming Language :: Python :: 3.8',
	"Operating System :: OS Independent"],
	python_requires='>=3.5',
	packages=['pypipe_tools'],
	project_urls={'Source': 'https://github.com/dlanier/pipe_tools.git'})

