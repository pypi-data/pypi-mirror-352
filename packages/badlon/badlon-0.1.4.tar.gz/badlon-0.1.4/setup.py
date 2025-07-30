from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()

# Get the long description from the README file
long_description = (here / 'README.md').read_text(encoding='utf-8')

setup(
    name='badlon',
    version='0.1.4',
    description='A bioinf tool for analyzing pan-genome and other features based on synteny blocks',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/oxygen311/badlon',
    author='Alexey Zabelkin',
    author_email='a.zabelkin@itmo.ru',
    classifiers=[
        'Topic :: Scientific/Engineering :: Bio-Informatics',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3 :: Only',
    ],
    keywords='synteny blocks, pan genome, core genome, bioinformatics, genome alignment',
    package_dir={'badlon': 'badlon'},
    packages=['badlon', 'badlon.charts', 'badlon.data'],
    python_requires='>=3.6, <4',
    install_requires=
        ['pandas',
         'numpy',
         'seaborn',
         'biopython'],
    entry_points={
        'console_scripts': [
            'badlon=badlon.run_badlon:main',
        ],
    },
)