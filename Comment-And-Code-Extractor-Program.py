# -----------------------------------------------------------------
# |                    SYSTEMS-2 ASSIGNMENT-2                     |
# |---------------------------------------------------------------|
# | Date: July 5, 2021                                            |  
# | Submitted by: MEGHA VERMA                                     |                                   |                                            
# |_______________________________________________________________|


import sys


# Function to write a given line into the 'codefile'
def writeToCodeFile(line):
    code_txt = " " + line + "\n" 
    codefile.write(code_txt)


# Function to write a given line into the 'commentfile'
# Case parameter dictates in what format the comment will be stored
def writeToCommentFile(i, line, case):
    if case == 0:
        comment_txt = str(i) + "  " + line.strip() + "\n"  
    # if continued multi-line comment line
    elif case == 1:
        comment_txt = str(i) + "     " + line.strip() + "\n" 
    # if line contains code, store a single dot in its place
    elif case == 2:
        comment_txt = str(i) + "  .\n"
    
    commentfile.write(comment_txt)



# File input from the user (path of the file is also accepted)
input = sys.argv[1]

# Opening 2 text files to store the code and the comments separately
codefile    = open("Original.txt","w")
commentfile = open("Comments.txt","w")


sourcefile = open(input, "r")   # Creating the file object named 'file'
commentInContinuation = False   # Flag variable to keep track of the multi-line comments
i = 1                           # Variable to keep track of line numbers in the C source file


# Traversing through the C source file 'line by line'
for line in sourcefile:

    # Storing the first 2 chars (ignoring spaces) in the line
    # to see if it's a comment or a line of code
    lineBeginsWith = line.strip()[:2]

    if (lineBeginsWith == '//'):   
        writeToCommentFile(i,line,0)
        writeToCodeFile("")      


    # if Case(1) the line starts with a 'multi-line' comment start symbol, OR
    # if Case(2) the line is a part of a previously encountered multi-line comment
    elif (lineBeginsWith == '/*' or commentInContinuation == True):

        if (lineBeginsWith == '/*'):
            # Updating the flag to indicate that multi-line comment is continued on next line
            commentInContinuation = True
            writeToCommentFile(i,line,0)

        else:
            # if multi-line comment end symbol '*/' is encountered at the beginning
            if (line.strip() == '*/'):
                writeToCommentFile(i,line,0)
            else:
                writeToCommentFile(i,line,1)

        
        # Updating the flag to indicate that multi-line comment has ended
        # if multi-line comment end symbol is encountered at the end of the line
        if (line.strip()[-2:] == '*/'):
            commentInContinuation = False

        writeToCodeFile("") 
 
    elif ('//' in line or '/*' in line):
        # Variable partitionPt stores the index that separates the 
        # line of code from the comment that is followed after in the same line
        if ('//' in line):
            partitionPt = line.index('//')
        elif ('/*' in line):
            partitionPt = line.index('/*') 

        writeToCommentFile(i,line[partitionPt:],0)  
        writeToCodeFile(line[:partitionPt]) 


    # if none of the above cases are true then the line must contain only the code part 
    else:
        # if it is a line of code
        if (len(line.strip()) != 0):
            writeToCodeFile(line)

        writeToCommentFile(i,line,2)
       
    # Updating the line number
    i = i+1


# Closing the C source file
sourcefile.close()
