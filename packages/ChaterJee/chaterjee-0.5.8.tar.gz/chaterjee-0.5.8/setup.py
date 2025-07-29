from setuptools import setup, find_packages

setup(
    name='ChaterJee',
    version='0.5.8',
    packages=find_packages(),
    install_requires=[
        'python-telegram-bot==20.7',
    ],
    author='Pallab Dutta',
    author_email='pallab9997@gmail.com',
    description='Communicate your project updates via Telegram Bot!',
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    python_requires=">=3.8",
)
