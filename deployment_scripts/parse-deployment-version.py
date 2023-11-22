import sys
import json
listStr = sys.stdin.read()

try:
    result = json.loads(listStr)[0]
    template = result['instanceTemplate'].split('/')[-1]
    

    print(int(template.replace("key-val-template-", "")))
except:
    print("undefined")