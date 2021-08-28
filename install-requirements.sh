curl -LJ  https://github.com/bitly/bitly-api-python/archive/refs/heads/master.zip -o temp.zip
unzip temp.zip
rm temp.zip
cd bitly-api-python-master && python3 setup.py install
