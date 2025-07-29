"""
Package configuration.
"""

from setuptools import find_namespace_packages, setup


setup(
    name="recall-space-agents",
    version="5.0.0",
    description="Agents of recall space.",
    author="Recall Space",
    author_email="info@recall.space",
    license="Open source",
    packages=find_namespace_packages(exclude=["tests"]),
    zip_safe=False,
    include_package_data=True,
    install_requires=[
        "langgraph==0.3.34",
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
        "azure-storage-blob"
    ],
    extras_require={
        "postgresql": [
            "psycopg[binary,pool]",
            "langgraph-checkpoint-postgres",
            "azure-storage-queue",
        ],
        "microsoft_graph": ["msgraph-sdk", "azure-identity", "azure-keyvault-secrets"],
        "nlp": ["nltk"],
        "google_calendar": [
            "google-api-python-client",
            "google-auth",
            "google-auth-httplib2",
            "google-auth-oauthlib",
        ],
        "microsoft_doc_intelligence": ["azure-ai-documentintelligence"],
        "all": [
            "psycopg[binary,pool]",
            "langgraph-checkpoint-postgres",
            "azure-storage-queue",
            "msgraph-sdk",
            "nltk",
            "google-api-python-client",
            "google-auth",
            "google-auth-httplib2",
            "google-auth-oauthlib",
            "azure-identity",
            "azure-keyvault-secrets",
            "azure-ai-documentintelligence",
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
