import sys

# Dictionary to store the relevant size directives along with their sizes 
sizes = {'db' : 2, 'dw' : 4, 'dd' : 8, 'resb' : 1, 'resw' : 2, 'resd' : 4}

# Define the required flags
bssflag = dataflag = currDataAddr = prevDataAddr = currBssAddr = prevBssAddr = None

# Define and initialize relevant variables
idfNames = []
idfLen = [0]
lenVars = {}

# Open a new file in 'write' mode to store the output
lstfile = open("p.lst", "w")


def translateEmptyLine(i, ln) :
    return '{0} {1:28} {2}'.format((str(i+1)).rjust(6), '', ln)


def translateLabelLine(i, ln) :
    return '{0} {1:8} {2:28} {3}'.format((str(i+1)).rjust(6), '', '', ln)


def translateDataSection(i, ln) :
    global currDataAddr
    global prevDataAddr
    global lstfile

    t = ln.split()
    dir = t[1]

    # If the directive found is present in the 'sizes' dictionary, we proceed with this if block
    if dir in sizes.keys() and len(dir) == 2 :
        quote = ln[ln.index(dir)+2:].lstrip()[0]
        # print(quote)
        # If the line contains a <<<< single string >>>>, we do the translation accordingly
        if ln.count(quote) == 2 :
            strTokens = ln.split(',')
            identifierName = strTokens[0][:strTokens[0].index(dir)].strip()
            idfNames.append(identifierName)
            strTokens[0] = strTokens[0][strTokens[0].index(dir)+2:].lstrip().replace(quote,'')
            translatedPart = translateDataStr(strTokens, dir) 
            identifierLength = int(len(translatedPart)/2) 
            idfLen.append(identifierLength)
            translatedPart = divideStr(translatedPart).split()

            for chunk in translatedPart :
                currDataAddr += prevDataAddr
                res = '{0} {1} {2:28}'.format((str(i+1)).rjust(6), toHex(currDataAddr), chunk)                        
                if translatedPart.index(chunk) == 0 :
                    res += ' ' + ln.rstrip()
                res += '\n'
                prevDataAddr = len(chunk.replace('-','')) / 2
                lstfile.write(res)


        # If the line contains an <<<< array of strings >>>>
        elif ln.count(quote) > 2 :
            strTokens = ln.split(',')
            identifierName = strTokens[0][:strTokens[0].index(dir)].strip()
            idfNames.append(identifierName)
            strTokens[0] = strTokens[0][strTokens[0].index(dir)+2:]
            strTokens = list(map(lambda s: s.lstrip().replace(quote,'').replace("\n",''), strTokens))
            translatedPart = translateDataStrArray(strTokens, dir)
            identifierLength = int(len(translatedPart)/2)
            idfLen.append(identifierLength)
            translatedPart = divideStr(translatedPart).split()
            for chunk in translatedPart :
                currDataAddr += prevDataAddr
                res = '{0} {1} {2:28}'.format((str(i+1)).rjust(6), toHex(currDataAddr), chunk)
                if translatedPart.index(chunk) == 0 :
                    res += ' ' + ln.rstrip()
                res += '\n'
                prevDataAddr = len(chunk.replace('-','')) / 2
                lstfile.write(res)
            

        # If line doesn't contain a string value, it must be either a single number or an array of numbers
        else :
            t = ln.split(',')
            # Check if it is a <<<< single number >>>>
            if len(t) == 1:
                t = ln.split()
                num = t[2].strip()
                translatedPart = (translateDataNum(num, dir))
                currDataAddr += prevDataAddr
                res = '{0} {1} {2:28} {3}'.format((str(i+1)).rjust(6), toHex(currDataAddr), translatedPart, ln)
                prevDataAddr = len(translatedPart) / 2
                lstfile.write(res)


            # Check if if is an <<<< array of numbers >>>>
            elif len(t) > 1 :
                t[0] = t[0][t[0].index(dir)+2:].lstrip()
                arrTokens = list(map(lambda x: int(x), t))
                translatedPart = translateDataNumArray(arrTokens, dir)
                translatedPart = divideStr(translatedPart).split()
                for chunk in translatedPart :
                    currDataAddr += prevDataAddr
                    res = '{0} {1} {2:28}'.format((str(i+1)).rjust(6), toHex(currDataAddr), chunk)
                    if translatedPart.index(chunk) == 0 :
                        res += ' ' + ln.rstrip()
                    res += '\n'
                    prevDataAddr = len(chunk.replace('-','')) / 2
                    lstfile.write(res)
        
        
    elif dir == 'equ' :
        if idfLen[-1] != 0 :
            idfLen.append(0)

        lenVarName = t[0]
        lenVars[lenVarName] = t[2][t[2].index('$-')+2:]
    
        res = '{0} {1:8} {2:28} {3}'.format((str(i+1)).rjust(6), '', '', ln)
        lstfile.write(res)


def translateBssSection(i, ln) :
    global currBssAddr
    global prevBssAddr
    global lenVars

    translatedPart = '0'.zfill(8)
    tokens = ln.split()

    if ('resb' in ln) or ('resw' in ln) or ('resd' in ln) :
        dir = tokens[1]
        num = tokens[2].strip()
        if num.isdigit() or (num.startswith('0x') and num.strip()[2:].isdigit()) :
            translatedPart = translateBssTxt(num, dir)
        elif num in lenVars.keys() :
            translatedPart = translateBssTxt(str(lenVars[num]), dir)

        currBssAddr += prevBssAddr
        res = '{0} {1} {2:28} {3}'.format((str(i+1)).rjust(6), toHex(currBssAddr), '<res ' + translatedPart + '>', line)
        prevBssAddr = int(translatedPart,16)
        return res


def toLittleEndian(num) :
    """ Utility function that returns a given hex value in the little endian format """
    return ('').join([num[i:i+2] for i in range(0, len(num), 2)][::-1]) 


def toHex(n, size=8) :
    """ Utility function that returns a given number's hex equivalent value """
    return hex(int(n))[2:].upper().zfill(size)
    

def translateBssTxt(num, dir) :
    """ Returns the hex representation of the memory to be 
        reserved in the Bss section as per the given size """
    if '0x' not in num:
        return toHex(int(num) * sizes[dir])
    return str(int(num[2:]) * sizes[dir]).upper().zfill(8)
    

def translateDataNum(num, dir) :
    """ Function that returns the hex representation of a 'number' defined in the Data section """
    if '0x' not in num :
        num = hex(int(num))
    return toLittleEndian(num[2:].upper().zfill(sizes[dir]))


def divideStr(s) :
    """ Utility function to divide a given string into chunks of max 9 bytes each """
    return '-\n'.join(s[i:i+18] for i in range(0, len(s), 18))


def strToHex(s) :
    """ Utility function to translate a given string into hex format """
    return ('').join(map(lambda ch: hex(ord(ch))[2:].upper(), s))


def translateDataNumArray(arr, dir) :
    """ Function that returns the hex representation of an 'numeric array' defined in the Data section """
    hexarr = ''
    for a in arr :
        hexarr += toLittleEndian(toHex(a, sizes[dir]))
    return hexarr


def translateDataStr(strArr, dir) :
    """ Function that returns the hex representation of a 'string' defined in the Data section """
    restPart = list(map(lambda x: int(x), strArr[1:]))
    s = strToHex(strArr[0]) + translateDataNumArray(restPart, dir)
    return s


def translateDataStrArray(arr, dir) :
    """ Function that returns the hex representation of an 'string array' defined in the Data section """
    hexstr = ''
    for a in arr:
        hexstr += strToHex(a).ljust(sizes[dir]*2, '0')
    return hexstr


def computeVarLengths() :
    global idfLen
    global idfNames

    idfLen = idfLen[::-1]
    for i in range(len(idfLen)) :
        if idfLen[i] != 0 :
            idfLen[i] += idfLen[i-1]

    idfLen = [l for l in idfLen[::-1] if l != 0]
    for k, v in lenVars.items() :
        lenVars[k] = idfLen[idfNames.index(v)]


# Main Function
if __name__ == '__main__':
    # Read input file name
    input = sys.argv[1]
    # Open the file and create a file object to work with it
    assemblyfile = open(input, "r")
    # Open a new file in 'write' mode to store the output
    lstfile = open("p.lst", "w")


    # Read the input file line by line to perform the translation 
    for lineNum, line in enumerate(assemblyfile) :

        # Update the Data and Bss flags as 'FALSE' as soon as Text section is encountered
        # And break out of the loop [that is, stop reading the file for further lines]
        if line.strip().startswith('section .text') :
            dataflag = bssflag = False
            break
        

        # If an empty line is encountered, print it and continue with the next iteration
        if len(line.strip()) == 0:
            translation = translateEmptyLine(lineNum, line)
            lstfile.write(translation)
            continue




# ------------------------------------------------------ D A T A  S E C T I O N ---------------------------------------------------------- #




        # If Data section is encountered, update the Data flag as TRUE
        if line.strip().startswith('section .data') :
            dataflag = True
            bssflag = False
            currDataAddr = prevDataAddr = 0
            translation = translateLabelLine(lineNum, line)
            lstfile.write(translation)


        # If Data section is already TRUE, perform translation of the current line accordingly
        elif dataflag == True :
            translateDataSection(lineNum, line)




# -------------------------------------------------------- B S S  S E C T I O N ---------------------------------------------------------- #
    
    


        # If Bss section is encountered, update the Bss flag as TRUE
        if line.strip().startswith('section .bss') :
            bssflag = True
            computeVarLengths()
            dataflag = False
            currBssAddr = prevBssAddr = 0
            translation = translateLabelLine(lineNum, line)
            lstfile.write(translation)

        
        # If Bss section is already TRUE, perform translation of the current line accordingly
        elif bssflag == True :
            translation = translateBssSection(lineNum, line)
            lstfile.write(translation)




# ---------------------------------------------------------------------------------------------------------------------------------------- #


    # Close the assembly file
    assemblyfile.close()
                          
