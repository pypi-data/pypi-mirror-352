from setuptools import setup, find_packages

def readme():
  with open('README.md', 'r') as f:
    return f.read()

setup(
  name='fwt_tools',
  version='1.0.4',
  author='spyr000',
  author_email='mr.zeddd123@gmail.com',
  description='Tools for building your own wavelets and performing fast wavelet transform',
  long_description=readme(),
  long_description_content_type='text/markdown',
  url='https://github.com/spyr000/FwtTools',
  packages=find_packages(),
  install_requires=['numpy>=1.20', 'numba>=0.60.0'],
  classifiers=[
    'Programming Language :: Python :: 3.11',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent'
  ],
  keywords='example python',
  project_urls={
    'Documentation': 'https://github.com/spyr000/UsagesOfFwtTools'
  },
  python_requires='>=3.7'
)