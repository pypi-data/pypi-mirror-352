from setuptools import setup, find_packages
setup(
    name='test-lib-luan',
    version='0.1.4',
    packages=find_packages(),
    author='Luan',
    author_email='',
    description='Đây là thư viện test',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    python_requirement='>=3.6'
)