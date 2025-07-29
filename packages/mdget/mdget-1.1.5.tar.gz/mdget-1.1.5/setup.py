#from distutils.core import setup
# import setuptools
from setuptools import setup, find_packages
import mdget.mdget as v

setup(name='mdget',
      version=v.__version__,
      author='xigua, ',
      author_email="2587125111@qq.com",
      url='https://pypi.org/project/mdget',
      long_description='''
      世界上最庄严的问题：我能做什么好事？
      ''',
      packages=find_packages(include=['mdget', 'mdget.*']),
      package_data={
          'mdget': [],
      },
      exclude_package_data={
          'mdget': ['conf', 'conf.*', 'spd.txt'],
      },
      entry_points={
              'console_scripts': [
                  'mdget=mdget.mdget:main',
              ],
          },
      package_dir={'requests': 'requests'},
      license="MIT",
      python_requires='>=3.6',
      )
