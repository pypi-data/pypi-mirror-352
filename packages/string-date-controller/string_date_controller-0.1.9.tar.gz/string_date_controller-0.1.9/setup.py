from setuptools import setup, find_packages

with open('requirements.txt') as f:
    requirements = [line.strip() for line in f if line.strip()]

setup(
    name='string_date_controller',
    version='0.1.9',
    packages=find_packages(),
    install_requires=requirements,
    author='June Young Park',
    author_email='juneyoungpaak@gmail.com',
    description='A Python module for string date manipulation and formatting',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/nailen1/string_date_controller.git',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Libraries',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.11',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.11',
    keywords='date time formatting manipulation utility',
)
