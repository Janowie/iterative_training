from setuptools import setup

setup(
    name='pyexample',
    version='0.1.0',
    description='A example Python package',
    url='https://github.com/shuds13/pyexample',
    author='Stephen Hudson',
    author_email='shudson@anl.gov',
    license='BSD 2-clause',
    packages=['pyexample'],
    install_requires=['numpy', 'pandas', 'tensorflow', 'matplotlib',
                      'google-api-python-client', 'google-auth-httplib2',
                      'google-auth-oauthlib', 'gspread', 'oauth2client'],

    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        # 'Operating System :: POSIX :: Linux',
        # 'Programming Language :: Python :: 2',
        # 'Programming Language :: Python :: 2.7',
        # 'Programming Language :: Python :: 3',
        # 'Programming Language :: Python :: 3.4',
        # 'Programming Language :: Python :: 3.5',
    ],
)
