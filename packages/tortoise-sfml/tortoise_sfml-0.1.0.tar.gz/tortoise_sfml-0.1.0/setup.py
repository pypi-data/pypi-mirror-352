from setuptools import setup, find_packages


setup(
    name='tortoise-sfml',
    version='0.1.0',
    packages=find_packages(),
    package_data={'psf': ['*.pyd', '*.dll', '*.md', '*.pyx', '*.py']},
    author='CoffeeTortoise',
    author_email='e.8ychkov@yandex.ru',
    description='SFML 2.6.1 cython binding for python',
    license='zlib'
)