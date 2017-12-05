# Introduction
Code for the labs are in [lab1](./lab1), [lab2](./lab2) and [lab3](./lab3) respectively.

# Requirements
* [Python 2.7](https://www.python.org/)
* Python pip (package manager). Install pip via the following command
```
wget -qO- https://bootstrap.pypa.io/get-pip.py | python
```

```
pip install -r requirement.txt
```
# How to run
## Lab 1
```
python lab1/lab1_server.py
python lab1/lab1_client.py
```

## Lab 2
Server
```
sh lab2/comile.sh
sh lab2/start.sh 8080
```
Client test
```
python lab2/lab2_client.py
```

## Lab 3
```
sh lab3/start.sh 8181
```
Server uses port 8181 to accept connections from clients.
