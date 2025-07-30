from setuptools import setup, find_packages

setup(
    name='whatsapp_message_sender',
    version='0.2.2',
    description='A tool for sending WhatsApp messages to clients with pending payments',
    packages=find_packages(),
    install_requires=[
        'pandas',
        'pyautogui',
        'openpyxl'
    ],
    entry_points={
        'console_scripts': [
            'whatsapp_message_sender = src.__main__:main',
        ],
    },
)
