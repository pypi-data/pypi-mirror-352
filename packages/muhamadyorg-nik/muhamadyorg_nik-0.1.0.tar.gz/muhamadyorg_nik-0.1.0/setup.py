from setuptools import setup

setup(
    name='muhamadyorg-nik',
    version='0.1.0',
    packages=['muhamadyorg-nik'],
    install_requires=['pyfiglet'],
    entry_points={
        'console_scripts': [
            'nikfiglet=muhamadyorg_nik.main:main'
        ]
    },
    author='Muhamadyor',
    description='Print nicknames in figlet ASCII art style',
    license='MIT',
    python_requires='>=3.6',
)
