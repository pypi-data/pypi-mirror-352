from setuptools import setup, find_packages

setup(
    name="p4b",
    version="0.1.4",
    description="god bless you.",
    packages=find_packages(),
    install_requires=[
        "keyboard>=0.13.5",
        "pyperclip>=1.9.0",
        "pillow>=11.2.1",
        "pyautogui>=0.9.54",
        "setuptools>=78.1.1",
        "google-generativeai==0.8.5",
        "openai==1.83.0"
    ],
    entry_points={
        "console_scripts": [
            "p4b=p4b.core:core"
        ],
    },
    package_data={
        "p4b": ["core.pyd", "*.pyd", "*.py"],
    },
    include_package_data=True,
    zip_safe=False,
)