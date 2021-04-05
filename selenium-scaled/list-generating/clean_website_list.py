file = open('website_list.txt','r')
#print file.readlines()
for i in file.readlines():
    j = i.split("http://")
    if (len(j)!=2):
        k = i.split("https://")
        if (len(k)!=2):
            i = i
        else:
            i = k[1]
    else:
        i = j[1]
    print(i,end='')
