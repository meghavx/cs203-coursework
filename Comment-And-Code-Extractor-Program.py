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
        c_text = str(i).ljust(2, ' ') + "  " + line.strip() + "\n"         
        comments.write(c_text)
   
    elif (txt == '/*' or flag == 1):
        if (txt == '/*'):
            c_text = str(i) + "  " + line.strip() + "\n"
            flag = 1 
        else:
            if (line.strip() == '*/'):
                c_text = str(i) + "  " + line.strip() + "\n" 
            else:
                c_text = str(i) + "     " + line.strip() + "\n" 
        
        comments.write(c_text)
        if (line.strip()[-2:] == '*/'):
            flag = 0

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