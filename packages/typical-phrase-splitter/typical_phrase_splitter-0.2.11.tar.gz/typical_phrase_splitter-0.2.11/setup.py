from setuptools import setup, find_packages

setup(
    name="typical-phrase-splitter",
    version="0.2.11",
    packages=find_packages(
        include=['typical_phrase_splitter', 'typical_phrase_splitter.*']
    ),
    install_requires=[
        "openai",       
        "spacy"        
    ],
    entry_points={
        'console_scripts': [
            'split-phrase=typical_phrase_splitter.typical_phrase_splitter:main',
        ],
    },
    include_package_data=True,
    description="A package to split sentences into typical segments using OpenAI API",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author="Ziwei Gu",
    author_email="ziweigu@g.harvard.edu",
    url="https://github.com/ZiweiGu/GP-TSM", 
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
