from setuptools import find_packages, setup

with open('requirements.txt') as f:
    requirements = f.readlines()

long_description = ('consistently archive albums you download from Gazelle')

setup(
    name='gazarc',
    version='0.1.1',
    author='jonesnc',
    author_email='example@gmail.com',
    url='https://github.com/jonesnc/gazarc',
    description='Gazelle album archiver.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    license='MIT',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'gazarc=gazarc.main:main'
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    keywords='gazelle archive',
    install_requires=requirements,
    zip_safe=False
)
