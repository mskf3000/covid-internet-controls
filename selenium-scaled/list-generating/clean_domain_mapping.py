file = open('type_domain_mapping.txt','r')
#print file.readlines()
for i in file.readlines():
    i = i.split("|||")[1]
    print(i,end='')
