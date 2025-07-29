from setuptools import setup, find_packages

classifiers = [
  'Development Status :: 5 - Production/Stable',
  'Intended Audience :: Education',
  'Operating System :: Microsoft :: Windows :: Windows 10',
  'License :: OSI Approved :: MIT License',
  'Programming Language :: Python :: 3'
]

setup(
  name='Niharikabasiccalculator',
  version='0.0.1',
  description='A very basic calculator',
  long_description=open('README.md', encoding='utf-8').read(),
  long_description_content_type='text/markdown',  # <-- Add this line
  url='',
  author='Praveena Niharika Thivari',
  author_email='thivariniharika@gmail.com',
  license='MIT',
  classifiers=classifiers,
  keywords='calculator',
  packages=find_packages(),
  install_requires=[]
)
