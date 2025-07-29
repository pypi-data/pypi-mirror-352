from setuptools import setup, find_packages

setup(
    name="sftp_downloader",
    version="0.1",
    packages=find_packages(),
    install_requires=["paramiko", "tqdm"],
    entry_points={
        'console_scripts': [
            'sftp-download=sftp_downloader.cli:main'
        ]
    }
)
