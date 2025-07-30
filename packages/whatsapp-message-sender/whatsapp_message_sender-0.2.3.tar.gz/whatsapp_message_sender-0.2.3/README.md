Build locally:
python -m pip install -e .

Push to PyPi
pip install twine
python setup.py sdist bdist_wheel
twine upload dist/whatsapp_message_sender-0.2.2* --username __token__