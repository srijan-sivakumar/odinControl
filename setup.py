from setuptools import setup, find_packages

with open('README.md') as f:
      readme = f.read()

with open('LICENSE') as f:
      license = f.read()

setup(name='rexe',
      version='0.1',
      description=readme,
      url='https://github.com/srijan-sivakumar/odinControl',
      author='Srijan Sivakumar',
      author_email='ssivakum@redhat.com',
      license=license,
      packages=['sample'],
      zip_safe=False) 