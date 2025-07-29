from setuptools import setup, find_namespace_packages

install_requires = [
    'sentry==25.*',
    'pymongo==4.*',
]

with open("README.md", "r") as readme:
    long_description = readme.read()

setup(
    name='sentry-nodestore-mongodb',
    version='0.1.0',
    author='David Smith',
    author_email='david@xterm.me',
    url='https://github.com/xterm-inator/sentry-nodestore-mongodb',
    description='Sentry nodestore MongoDB backend',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=find_namespace_packages(),
    include_package_data=True,
    license='Apache-2.0',
    install_requires=install_requires,
    zip_safe=False,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Operating System :: POSIX',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python',
        'Operating System :: OS Independent',
    ],
    project_urls={
        'Bug Tracker': 'https://github.com/xterm-inator/sentry-nodestore-mongodb/issues',
        'CI': 'https://ggithub.com/xterm-inator/sentry-nodestore-mongodb/actions',
        'Source Code': 'https://github.com/xterm-inator/sentry-nodestore-mongodb',
    },
    keywords=['sentry', 'mongodb', 'nodestore', 'backend'],
)
