from setuptools import setup, find_packages

setup(
    name='llm_reasoning_tracer',
    version='0.1.0',
    author='Nisaharan Genhatharan',
    description='Trace and explain LangChain agent reasoning step-by-step',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/nisaharan/llm_reasoning_tracer',
    packages=find_packages(exclude=["examples"]),
    install_requires=[
        "langchain",
        "streamlit",
        "openai",
        "faiss-cpu",
        "tiktoken",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    include_package_data=True,
    python_requires='>=3.8',
)
