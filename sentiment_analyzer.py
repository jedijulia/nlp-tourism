#!/usr/bin/env python
import re

def clean(tweet):
    clean = re.sub(r'https?:\/\/\w+(\.\w+)*(:\w+)?(/[A-Za-z0-9-_\.]*)* ?', '', tweet)
    clean = re.sub(r'#', '', clean)
    clean = re.sub(r'!', '', clean)
    clean = re.sub(r'\.\.\.', '', clean)
    clean = re.sub(r',', '', clean)
    return clean