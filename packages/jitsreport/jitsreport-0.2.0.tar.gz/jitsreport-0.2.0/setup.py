from setuptools import setup, find_packages

setup(
    name='jitsreport',
    version='0.2.0',
    description='A package for generating automated data profiling reports.',
    author='Surajit Das',
    author_email="mr.surajitdas@gmail.com",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(where='dist_obf'),
    package_dir={'': 'dist_obf'},
    package_data={
        'pyarmor_runtime_000000': ['*.pyd', '*.py'],
    },
    include_package_data=True,
    install_requires=[
        'pandas',
        'numpy',
        'plotly',
        'pdfkit',
        'openpyxl',
        'scipy',
        'matplotlib',
        'statsmodels',
        'jinja2',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
    ],
    python_requires='>=3.6',
)