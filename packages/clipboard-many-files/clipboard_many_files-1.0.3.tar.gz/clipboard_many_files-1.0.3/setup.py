import setuptools
import distutils.core

setuptools.setup(
    name='clipboard-many-files',
    version="1.0.3",
    author='@readwithai',
    long_description_content_type='text/markdown',
    author_email='talwrii@gmail.com',
    description='Place several files on clipboard from the command-line',
    license='MIT',
    keywords='clipboard, files',
    url='https://github.com/talwrii/clipboard-many-files',
    install_requires=[],
    packages=["clipboard_many_files"],
    long_description=open('README.md').read(),
    entry_points={
        'console_scripts': [
            'clipboard-many-files=clipboard_many_files.main:main',
            'cmf=clipboard_many_files.main:main'

        ]
    },
)
