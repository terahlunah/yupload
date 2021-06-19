from setuptools import setup

setup(name="yupload",
      version="0.0.1",
      description="Youtube uploader using selenium",
      author="Terah",
      author_email="terah.dev@gmail.com",
      packages=["yupload"],
      install_requires=["chromedriver-binary-auto", "selenium", "selenium_stealth"],
      license="Apache 2.0")
