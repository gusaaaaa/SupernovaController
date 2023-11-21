import os
from setuptools import setup, find_packages

# Read GH_TOKEN from environment variables // Remove when transfer_controller v0.3.0 is approved
gh_token = os.environ.get('GH_TOKEN')

setup(
    name='supernovacontroller',
    version='0.1.0',
    packages=find_packages(),
    description='A blocking API for interacting with the Supernova host-adapter device',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Binho LLC',
    author_email='support@binho.io',
    url='https://github.com/yourusername/SupernovaController',
    license='Private',
    install_requires=[
      f'transfer_controller @ git+https://{gh_token}@github.com/binhollc/TransferController.git@667-gus#egg=transfer_controller', # Remove when transfer_controller v0.3.0 is approved
      # 'transfer_controller==0.3.0', # Replace previous line when transfer_controller v0.3.0 is approved
      'BinhoSupernova==0.2.0'
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.5',
)
