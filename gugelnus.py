from pygooglenews import GoogleNews

gn = GoogleNews()

s = gn.search('lumpy skin disease')

for items in s['entries']:
    print(items["summary"])
