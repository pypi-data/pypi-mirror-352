from setuptools import setup, find_packages

setup(
    name='pythontextstats',
    version='0.1.1',
    author='Vignesh Selvaraj',
    author_email='vigneshaasiga2020@gmail.com',
    description='A Python package for text analysis',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/Vigneshselvaraj1811/textstats',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
