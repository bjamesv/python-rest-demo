# Python REST Demo
Example REST API implemented with [Falcon](https://falconframework.org/) Python microframework.

## Build
Steps to build & run the API

    $ git clone https://github.com/bjamesv/python-rest-demo.git
    $ cd python-rest-demo/
    $ docker build -t restdemo .

## Run
    $ docker run -it --rm -p 8080:80 --name restdemo-8080 restdemo

## Test
    $ cd python-rest-demo/
    $ python -m venv demo-env
    $ source demo-env/bin/activate
    $ pip install -r requirements.txt
    $ python -m unittest discover
    $ deactivate

Copyright (C) 2019 Brandon J. Van Vaerenbergh
