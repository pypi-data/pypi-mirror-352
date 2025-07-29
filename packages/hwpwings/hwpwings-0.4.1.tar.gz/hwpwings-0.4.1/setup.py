from setuptools import setup, find_packages

setup(
    name="hwpwings",
    version="0.4.1",
    author="한파엑셀",
    author_email="hpxl0518@gmail.com",
    description="파이썬으로 한글 문서를 제어할 수 있는 두번째 라이브러리입니다.",
    url="https://www.youtube.com/@%ED%95%9C%ED%8C%8C%EC%97%91%EC%85%80",
    packages=find_packages(include=["hwpwings", "hwpwings.*"]),
    python_requires=">=3.6",
    install_requires=[
        "pywin32>=302",
        "pandas>=1.0.0",
        "lxml>=4.0.0",
    ],
)
