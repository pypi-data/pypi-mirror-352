from setuptools import setup, find_packages

setup(
    name='django_logger_cli',
    version='0.1.3',
    description='🛠️ A CLI tool to generate Django-style logger configurations.',
    long_description=open("README.md").read(),  
    long_description_content_type='text/markdown',
    author='Manukrishna S',
    author_email='manukrishna.s2001@gmail.com',
    url='https://github.com/codewithmanuu/django-logger',  
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'click>=8.0'
    ],
    python_requires='>=3.7',  
    entry_points={
        'console_scripts': [
            'django-logger=Logger.cli:cli',
        ],
    },
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha', 
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Environment :: Console',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.10',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    project_urls={ 
        'Documentation': 'https://github.com/codewithmanuu/django-logger#readme',
        'Source': 'https://github.com/codewithmanuu/django-logger',
        'Tracker': 'https://github.com/codewithmanuu/django-logger/issues',
    },
)
