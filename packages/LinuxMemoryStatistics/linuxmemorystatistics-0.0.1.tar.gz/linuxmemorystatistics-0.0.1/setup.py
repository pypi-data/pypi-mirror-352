from setuptools import setup, find_packages
import LinuxMemoryStatistics as package

setup(
    name='LinuxMemoryStatistics',
    version=package.__version__,
    py_modules=['LinuxMemoryStatistics'],
    packages=find_packages(include=[]),
    install_requires=[],
    scripts=[],
    author="Maurice Lambert",
    author_email="mauricelambert434@gmail.com",
    maintainer="Maurice Lambert",
    maintainer_email="mauricelambert434@gmail.com",
    description='This script prints memory usages and statistics (by process, executable and for the full system).',
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/mauricelambert/LinuxMemoryStatistics",
    project_urls={
        "Github": "https://github.com/mauricelambert/LinuxMemoryStatistics",
        "Documentation": "https://mauricelambert.github.io/info/python/code/LinuxMemoryStatistics.html",
        "Python Executable": "https://mauricelambert.github.io/info/python/code/LinuxMemoryStatistics.pyz",
        "Windows Executable": "https://mauricelambert.github.io/info/python/code/LinuxMemoryStatistics.exe",
    },
    download_url="https://mauricelambert.github.io/info/python/code/LinuxMemoryStatistics.pyz",
    include_package_data=True,
    classifiers=[
        "Topic :: System",
        "Environment :: Console",
        "Topic :: System :: Shells",
        'Operating System :: POSIX',
        "Natural Language :: English",
        "Programming Language :: Python",
        "Topic :: System :: System Shells",
        "Programming Language :: Python :: 3.8",
        "Topic :: System :: Systems Administration",
        "Intended Audience :: System Administrators",
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
    ],
    keywords=['memory', 'executable', 'process', 'system', 'linux', 'usages'],
    platforms=['Windows', 'Linux', "MacOS"],
    license="GPL-3.0 License",
    entry_points = {
        'console_scripts': [
            'LinuxMemoryStatistics = LinuxMemoryStatistics:main'
        ],
    },
    python_requires='>=3.8',
)