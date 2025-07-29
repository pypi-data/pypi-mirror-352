
from setuptools import setup, find_packages

setup(
    name='nfinance',
    version='0.4.14',
    author='lega001',
    author_email='lega01077970523@gmail.com',
    packages=find_packages(),
    install_requires=[
        'pandas',  # 예시: pandas 라이브러리가 필요한 경우
        'requests',  # 예시: HTTP 요청을 위해 requests 라이브러리가 필요한 경우
        'tqdm',
        'ta'
    ],
    description='A simple finance data fetching library for Naver Finance data.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/lega001/nfinance',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    python_requires='>=3.6',
)
