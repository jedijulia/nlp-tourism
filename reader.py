#!/usr/bin/env python
import fileinput
import json

for line in fileinput.input():
	decoded = json.loads(line)
	print str(decoded['id']) + '\t' + decoded['text'].encode('utf-8')
