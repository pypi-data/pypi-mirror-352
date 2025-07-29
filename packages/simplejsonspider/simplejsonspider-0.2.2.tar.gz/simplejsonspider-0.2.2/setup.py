from setuptools import setup, find_packages

setup(
    name='simplejsonspider',
    version='0.2.2',
    description='A simple package to crawl JSON APIs and save response to local files.',
    author='Zeturn',
    author_email='hollowdata@outlook.com',
    packages=find_packages(),
    install_requires=[
        'requests',
    ],
    python_requires='>=3.6',
    url='https://github.com/zeturn/simplejsonspider',  # 可选
    license='MIT',
    keywords='json spider api crawler',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
