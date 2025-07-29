from setuptools import setup, find_packages

setup(
    name='nicewoo',  # PyPI 패키지 이름
    version='0.1.0',
    description='A lightweight NLP utility toolkit for stopword removal, keyword extraction, summarization, and language detection.',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    author='우성현',
    author_email='wshyun314@naver.com',
    url='https://github.com/WooMongGae/nicewoo',
    project_urls={
        'Documentation': 'https://woomonggae.github.io/nicewoo',
        'Source': 'https://github.com/WooMongGae/nicewoo',
        'Tracker': 'https://github.com/WooMongGae/nicewoo/issues',
    },
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        'nltk>=3.8',
        'scikit-learn>=1.2',
        'langdetect>=1.0',
        'sumy>=0.11.0',
        'numpy>=1.21.0',
        'scipy>=1.7.0',
    ],
    python_requires='>=3.8',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: MIT License',
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Text Processing :: Linguistic',
    ],
    keywords='nlp stopwords tf-idf summarization language-detection',
    include_package_data=True,
    zip_safe=False,
)
