import os.path
import setuptools


def read(name):
    mydir = os.path.abspath(os.path.dirname(__file__))
    return open(os.path.join(mydir, name)).read()


setuptools.setup(
    name='mkdocs-include-folders',
    version='0.1.4',
    packages=['mkdocs_include_folders'],
    url='https://github.com/hhdale/mkdocs-include-folders',
    license='Apache',
    author='Håkon Haugholt-Dale',
    author_email='hakon.dale@gmail.com',
    description='A mkdocs plugin that lets you include subfolder of a top level tree.',
    long_description=read('README.md'),
    long_description_content_type='text/markdown',
    install_requires=['mkdocs'],

    # The following rows are important to register your plugin.
    # The format is "(plugin name) = (plugin folder):(class name)"
    # Without them, mkdocs will not be able to recognize it.
    entry_points={
        'mkdocs.plugins': [
            'include-folders = mkdocs_include_folders:IncludeFolders',
        ]
    },
)
