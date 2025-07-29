from setuptools import setup

setup(
    name='muhamadyorg-nik',
    version='0.1.1',
    packages=['muhamadyorg_nik'],
    install_requires=['pyfiglet'],
    entry_points={
        'console_scripts': [
            'muhamadyorg-nik=muhamadyorg_nik.main:main'
        ]
    },
    author='Muhamadyor',
    description='CLI tool to print text in figlet ASCII art style',
    license='MIT',
    python_requires='>=3.6',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
