"""
Package configuration.
"""

from setuptools import find_namespace_packages, setup


setup(
    name="recall-space-agents",
    version="4.0.5",
    description="Agents of recall space.",
    author="Recall Space",
    author_email="info@recall.space",
    license="Open source",
    packages=find_namespace_packages(exclude=["tests"]),
    zip_safe=False,
    include_package_data=True,
    install_requires=[
        "langgraph<1.0.0",
        "langgraph-sdk<1.0.0",
        "langsmith<1.0.0",
        "langchain-community<1.0.0",
        "langchain-core<1.0.0",
        "langchain-openai<1.0.0",
        "langgraph-cli<1.0.0",
        "PyPDF2<4.0.0",
        "python-docx<2.0.0",
        "openpyxl<4.0.0",
        "beautifulsoup4<5.0.0",
        "pytz==2024.2",
        "pandas<3.0.0",
        "tabulate<1.0.0",
        "agent-builder<1.0.0",
    ],
    extras_require={
        "postgresql": [
            "psycopg[binary,pool]",
            "langgraph-checkpoint-postgres",
            "azure-storage-queue",
        ],
        "microsoft_graph": ["msgraph-sdk"],
        "all": [
            "psycopg[binary,pool]",
            "langgraph-checkpoint-postgres ",
            "msgraph-sdk",
            "azure-storage-queue",
        ],
    },
    test_suite="tests",
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries",
        "Programming Language :: Python :: 3.13",
    ],
)
