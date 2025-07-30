from setuptools import setup, find_packages

setup(
    name='interviewlib',
    version='0.1.1',
    packages=find_packages(),
    description='Python interview questions and solutions library',
    author='Mustakim Shaikh',
    author_email='mustakim.shaikh.prof@gmail.com',
    url='https://github.com/MUSTAKIMSHAIKH2942/interviewlib',
    license='MIT',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    classifiers=[
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",],
    python_requires='>=3.6',
)
