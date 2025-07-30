from setuptools import setup

setup(
    name="algoleap-dynamic-prompts",  # must be unique on PyPI
    version="0.1.1",
    py_modules=["index", "config"],
    install_requires=[
        "streamlit>=1.0.0",
        "openai>=0.28"
    ],
    entry_points={
        "console_scripts": [
            "algoleap-feedback=index:main"  # CLI command
        ]
    },
    author="Your Name",
    author_email="your@email.com",
    description="A Streamlit app to refine OpenAI prompts with real-time feedback.",
    long_description="",
    url="https://github.com/yourusername/algoleapDynamicPrompts",  # optional
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ],
    python_requires='>=3.7',
)
