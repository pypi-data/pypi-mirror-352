from setuptools import setup, find_packages

setup(
    name="Paid.ai-Client",
    version="0.4.8",
    author="Paid.ai",
    author_email="raj@agentpaid.ai",
    description="A package to interact with the Paid API.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/AgentPaid/ap-client",
    packages=find_packages(),
    install_requires=[
        "requests>=2.0.0",
        "python-dateutil>=2.8.2"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
    ],
    python_requires=">=3.6",
)
