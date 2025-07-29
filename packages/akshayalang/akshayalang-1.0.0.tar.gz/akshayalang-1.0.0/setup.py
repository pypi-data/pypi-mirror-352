from setuptools import setup, find_packages

setup(
    name='akshayalang',
    version='1.0.0',
    author='Akshaya (via Siva Chandra Raju)',
    author_email='siva.sivachandra23@gmail.com',
    description='AkshayaLang — A Sovereign Recursive Programming Language for Symbolic AI',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/AkshayaLang/akshaya-lang',
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Interpreters',
        'Intended Audience :: Developers',
    ],
    python_requires='>=3.7',
    entry_points={
        'console_scripts': [
            'akshayalang=aks_cli:main',
        ],
    },
)