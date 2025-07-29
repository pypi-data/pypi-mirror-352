from setuptools import setup, find_packages

setup(
    name='graph_visualizer',
    version='1.0.0',
    author='Ankit Kataria',
    author_email='ankitsinghkataria5@gmail.com',
    description='Interactive EDA graph visualizer for univariate, bivariate, multivariate, and datetime data.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    packages=find_packages(),
    install_requires=[
        'pandas',
        'matplotlib',
        'seaborn',
        'plotly'
    ],
    license='MIT',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
)

