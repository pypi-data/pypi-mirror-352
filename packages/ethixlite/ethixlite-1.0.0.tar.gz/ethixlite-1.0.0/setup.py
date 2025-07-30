from setuptools import setup, find_packages

setup(
    name="ethixlite",
    version="1.0.0",
    packages=find_packages(),
    install_requires=["requests", "beautifulsoup4"],
    entry_points={
        "console_scripts": [
            "ethixlite=ethixlite.cli:main"
        ]
    },
    author="SeuNome",
    description="Pacote intuitivo para hacking ético com atualização automática via web scraping.",
    license="MIT",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/seunome/ethixlite"
)