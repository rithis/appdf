all: requirements samples test

requirements:
	pip install -r requirements.txt

samples:
	wget https://github.com/onepf/AppDF/archive/master.tar.gz
	tar xf master.tar.gz
	mv AppDF-master/samples samples
	rm -r AppDF-master
	rm master.tar.gz

test:
	python -m doctest -v parser.py
