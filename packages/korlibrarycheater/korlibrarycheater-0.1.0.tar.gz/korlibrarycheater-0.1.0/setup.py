from setuptools import setup, find_packages

setup(
    name="korlibrarycheater",  # PyPI에 중복 없는 이름
    version="0.1.0",
    packages=find_packages(),
    python_requires='>=3.6',
    entry_points={
        'console_scripts': [
            'cheatlib=korlibrarycheater.KorLibraryCheater:main',  # main 함수가 KorLibraryCheater.py에 있어야 함
        ],
    },
    author="ppenn0411",
    description="파이썬 라이브러리 탐색 도구",
    url="https://github.com/ppenn0411/KorLibraryCheater",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
) 