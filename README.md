#Requirements
1. Download from http://nlp.stanford.edu/software/stanford-corenlp-full-2015-12-09.zip and remove all unnecessary files by
```
rm !(*.jar)
```
Then move all jar files into this directory.
2. Libraries:
- jsonrpc
- werkzeug
- pexpect
```
pip install jsonrpc werkzeug pexpect
```
Execute the server by using
```
python server.py <ip_addr> <port>
```
Default ip is 0.0.0.0 and port is 8080