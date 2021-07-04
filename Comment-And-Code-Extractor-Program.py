import sys

# File input from the user
# Path of the file is also accepted
input = sys.argv[1]
file = open(input, "r")

# Opening 2 text files to store the code and the comments separately
codefile = open("Original.txt","w")
commentfile = open("Comments.txt","w")

# Flag variable to keep track of the multi-line comments
commentInContinuation = False

# Variable to keep track of line numbers in the C source file
i = 1

# Traversing through the C source file 'line by line'
for line in file:

    # Storing the first 2 chars (ignoring spaces) in the line
    # to see whether it is a comment or a line of code
    lineBeginsWith = line.strip()[:2]


    # if the line starts with a 'single line' comment symbol
    if (lineBeginsWith == '//'):
        # Storing this comment to write into the 'commentfile'
        comment_txt = str(i) + "  " + line.strip() + "\n"         


    # if Case(1) the line starts with a 'multi-line' comment start symbol
    # Or Case(2) the line is a part of a previously encountered multi-line comment
    elif (lineBeginsWith == '/*' or commentInContinuation == True):
        # if Case(1)
        if (lineBeginsWith == '/*'):
            comment_txt = str(i) + "  " + line.strip() + "\n"
            # Updating the flag to indicate that the next line contains
            # part of the multi-line comment
            commentInContinuation = True
        
        # if Case(2)
        else:
            # if multi-line comment end symbol '*/' is encountered at the beginning
            if (line.strip() == '*/'):
                comment_txt = str(i) + "  " + line.strip() + "\n" 
            else:
                comment_txt = str(i) + "     " + line.strip() + "\n" 
        
        # if multi-line comment end symbol '*/' is encountered at the end of a line
        if (line.strip()[-2:] == '*/'):
            # Updating the flag to indicate that multi-line comment has ended
            commentInContinuation = False


    # if the comment symbol is present within the same line as the code line 
    elif ('//' in line or '/*' in line):
        # if it's a single line comment symbol
        if ('//' in line):
            start = line.index('//') 

        # if it's a multi-line comment symbol
        elif ('/*' in line):
            start = line.index('/*') 
    
        # Storing the comment part of the line to write into the 'commentfile'
        comment_txt = str(i) + "  " + line[start:].strip() + "\n"
        # Storing the code part of the line to write into the 'codefile'
        code_txt = " " + line[:start] + "\n"
         # Writing into the 'codefile'
        codefile.write(code_txt)
    

    # if none of the above cases are true then
    # it must be the case that it is a code line 
    else:
        # if instead of a code line it's an empty line
        code_txt = " " + line
        # if it is a code line indeed
        if (len(line.strip()) != 0):
            code_txt += "\n"
        # Storing the line of code to write into the 'codefile'
        comment_txt = str(i) + "\n"
        # Writing into the 'codefile'
        codefile.write(code_txt)

    # Writing the comment into the 'commentfile'
    commentfile.write(comment_txt)

    # Updating the line number
    i = i+1


# Closing the C source file
file.close()
