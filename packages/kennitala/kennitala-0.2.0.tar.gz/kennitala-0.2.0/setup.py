from distutils.core import setup

import kennitala

setup(
    name='kennitala',
    version=kennitala.__version__,
    url='https://github.com/ojake/python-kennitala',
    description='Icelandic national registry codes made easy',
    author='Sævar Öfjörð Magnússon, Jakub Owczarski',
    author_email='hallo@overcast.is',
    packages=['kennitala'],
    license='MIT license',
    long_description=open('README').read(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3'
    ]
)
