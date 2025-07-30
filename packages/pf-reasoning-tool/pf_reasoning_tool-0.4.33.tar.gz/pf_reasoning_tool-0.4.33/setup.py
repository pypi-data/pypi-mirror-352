# pf-reasoning-tool-proj/setup.py
from setuptools import find_packages, setup

PACKAGE_NAME = "pf_reasoning_tool"

setup(
    name=PACKAGE_NAME,
    version="0.4.33",                       # ↑ bump each release
    description="Custom PromptFlow tools for Hall & Wilcox (Azure Search only)",
    packages=find_packages(),
    entry_points={
        "package_tools": [
            # utils.py dynamically discovers every YAML in pf_reasoning_tool/yamls
            "pf_reasoning_tool = pf_reasoning_tool.tools.utils:list_package_tools",
        ],
    },
    install_requires=[
        "promptflow-core>=1.0.0",
        "jinja2>=3.0",
        "ruamel.yaml>=0.17",
        "openai>=1.0",                     # for OpenAIConnection dataclass
        "langchain>=0.2.0",
        "langchain-openai>=0.1.5",
        "langchain-community>=0.0.32",
        "azure-search-documents>=11.4.0b7",
        "azure-core"
    ],
    # No extras_require – package now targets Azure Search exclusively
    include_package_data=True,            # ship YAMLs via MANIFEST.in
)
