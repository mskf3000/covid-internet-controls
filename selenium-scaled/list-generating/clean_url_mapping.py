file = open('url_type_mapping.txt','r')
#print file.readlines()
for i in file.readlines():
    i = i.split("|||")[0]
    if(i[-1] == '.'):
        i = i[:-1]
    print(i)
