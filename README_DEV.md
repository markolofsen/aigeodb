
https://test.pypi.org/project/aigeodb/

rm -rf venv/lib/python3.13/site-packages/aigeodb
rm -rf venv/lib/python3.13/site-packages/aigeodb*
pip show aigeodb
pip uninstall aigeodb

pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ aigeodb==0.2.1a3


# pip install aigeodb==0.2.0