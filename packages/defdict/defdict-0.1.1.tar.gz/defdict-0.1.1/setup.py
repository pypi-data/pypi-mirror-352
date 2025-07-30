from setuptools import setup, find_packages
import codecs
import os.path


def read(rel_path):
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, rel_path), 'r') as fp:
        return fp.read()

def get_metadata(field):
    rel_path = "defdict/__init__.py"
    for line in read(rel_path).splitlines():
        if line.startswith(f'__{field}__'):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    else:
        raise RuntimeError(f"Unable to find {field} string.")




with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name='defdict',
    use_scm_version={'fallback_version': '0.0.0'},
    setup_requires=['setuptools_scm'],
    description=get_metadata('description'),
    url=get_metadata('url'),
    project_urls={'GitHub': 'https://github.com/Suke0811/DefDict'},
    author=get_metadata('author'),
    license='LGPLv3',
    packages=find_packages(include=['defdict', 'defdict.*']),
    install_requires=requirements,
    classifiers=[
        'Framework :: Robot Framework',
        'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
        'Programming Language :: Python :: 3',
    ],
)

