import sys

input = sys.argv[1]
file = open(input, "r")

codefile = open("Original.txt","w")
comments = open("Comments.txt","w")

i = 1
flag = 0

for line in file:
    txt = line.strip()[:2]

    if (txt == '//'):
        c_text = str(i) + "  " + line.strip() + "\n"         
   
    elif (txt == '/*' or flag == 1):
        if (txt == '/*'):
            c_text = str(i) + "  " + line.strip() + "\n"
            flag = 1 
        else:
            if (line.strip() == '*/'):
                c_text = str(i) + "  " + line.strip() + "\n" 
            else:
                c_text = str(i) + "     " + line.strip() + "\n" 
        
        if (line.strip()[-2:] == '*/'):
            flag = 0

    elif ('//' in line):
        start = line.index('//') 
        c_text = str(i) + "  " + line[start:].strip() + "\n"
        o_text = " " + line[:start]
        codefile.write(o_text)


    elif ('/*' in line):
        start = line.index('/*') 
        c_text = str(i) + "  " + line[start:].strip() + "\n"
        o_text = " " + line[:start]
        codefile.write(o_text)


    else:
        if (len(line.strip()) == 0):
            o_text = " " + line
        else: 
            o_text = " " + line + "\n"
        
        c_text = str(i) + "  .\n"
        codefile.write(o_text)

    comments.write(c_text)

    i = i+1

file.close()
