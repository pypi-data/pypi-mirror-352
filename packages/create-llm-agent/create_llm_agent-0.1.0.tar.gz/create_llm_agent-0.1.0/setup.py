from setuptools import setup, find_packages

setup(
    name='create-llm-agent',
    version='0.1.0',
    author='Alexandre Moraes de Souza Lima',
    author_email='alexandre.msl@gmail.com',
    description='A CLI tool to scaffold your first AI llm-agent project.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://gist.github.com/JimSP/5920dd06f31913eb42657ede1ae85cff',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
    entry_points={
        'console_scripts': [
            'create-llm-agent=create_llm_agent.cli:main',
        ],
    },
)