import sys


# Dictionary to store the relevant size directives along with their sizes 
sizes = {'db' : 2, 'dw' : 4, 'dd' : 8, 'resb' : 1, 'resw' : 2, 'resd' : 4}


# Define and initialize relevant variables
dataflag = currDataAddr = prevDataAddr = None
bssflag  = currBssAddr  = prevBssAddr  = None

identifiers = []
idenLengths = [0]
varAndLenDict = {}


# Open a new file in 'write' mode to store the output
lstfile = open("p.lst", "w")




# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> MAIN TRANSLATION FUNCTIONS <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< #


def translateDataSection(i, ln) :
    global currDataAddr, prevDataAddr, lstfile
    t = ln.split()
    dir = t[1]

    # If the directive found is present in the 'sizes' dictionary, we proceed with this if block
    if dir in sizes.keys() and len(dir) == 2 :
        quote = "'" if ln[ln.index(dir)+2:].lstrip()[0] == '\'' else '"'
        
        # If it is a SINGLE STRING
        if ln.count(quote) == 2 :
            translateStrArray(i, ln, dir, quote)

        # If it is a STRING ARRAY
        elif ln.count(quote) > 2 :
            translateStr(i, ln, dir, quote)
            

        # If line doesn't contain a string value, it must be either a single number or an array of numbers
        else :
            t = ln.split(',')

            # If it is a SINGLE NUMBER
            if len(t) == 1:
                translateNum(i, ln, t, dir)

            # If if is an NUMBER ARRAY
            elif len(t) > 1 :
                translateNumArray(i, ln, t, dir)
        
        
    elif dir == 'equ' :
        if idenLengths[-1] != 0 :
            idenLengths.append(0)

        lenVarName = t[0]
        varAndLenDict[lenVarName] = t[2][t[2].index('$-')+2:]
    
        res = '{0} {1:8} {2:28} {3}'.format((str(i+1)).rjust(6), '', '', ln)
        lstfile.write(res)


def translateBssSection(i, ln) :
    global currBssAddr, prevBssAddr, varAndLenDict

    reservedMemory = '0'.zfill(8)
    tokens = ln.split()

    if ('resb' in ln) or ('resw' in ln) or ('resd' in ln) :
        dir = tokens[1]
        num = tokens[2].strip()
        
        if num.isdigit() or (num.startswith('0x') and num.strip()[2:].isdigit()) :
            reservedMemory = resMemToHex(num, dir)
        elif num in varAndLenDict.keys() :
            reservedMemory = resMemToHex(str(varAndLenDict[num]), dir)

        currBssAddr += prevBssAddr
        addrPart = toHex(currBssAddr)
        transPart = '<res ' + reservedMemory + '>'
        prevBssAddr = int(reservedMemory,16)
        
        return '{0} {1} {2:28} {3}'.format((str(i+1)).rjust(6), addrPart, transPart, line)


def translateEmptyLine(i, ln) :
    return '{0} {1:28} {2}'.format((str(i+1)).rjust(6), '', ln)


def translateLabelLine(i, ln) :
    return '{0} {1:8} {2:28} {3}'.format((str(i+1)).rjust(6), '', '', ln)




# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> UTILITY FUNCTIONS <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< #




def translateStr(i, ln, dir, quote) :
    global currDataAddr, prevDataAddr, lstfile
    strTokens = ln.split(',')
            
    identifierName = strTokens[0][:strTokens[0].index(dir)].strip()
    identifiers.append(identifierName)

    strTokens[0] = strTokens[0][strTokens[0].index(dir)+2:]
    strTokens = list(map(lambda s: s.lstrip().replace(quote,'').replace("\n",''), strTokens))

    translatedPart = stringArrToHex(strTokens, dir)

    identifierLength = int(len(translatedPart) / 2)
    idenLengths.append(identifierLength)

    translatedPart = divideStr(translatedPart).split()

    for chunk in translatedPart :
        currDataAddr += prevDataAddr
        prevDataAddr = len(chunk.replace('-','')) / 2
        addr = toHex(currDataAddr)
        lnNum = (str(i+1)).rjust(6)

        res = '{0} {1} {2:28}'.format(lnNum, addr, chunk)
        
        if translatedPart.index(chunk) == 0 :
            res += ' ' + ln.rstrip()
        res += '\n'
        
        lstfile.write(res)


def translateStrArray(i, ln, dir, quote) :
    global currDataAddr, prevDataAddr, lstfile
    strTokens = ln.split(',')

    identifierName = strTokens[0][:strTokens[0].index(dir)].strip()
    identifiers.append(identifierName)
    
    strTokens[0] = strTokens[0][strTokens[0].index(dir)+2:].lstrip().replace(quote,'')
    translatedPart = stringToHex(strTokens, dir) 
    
    identifierLength = int(len(translatedPart) / 2) 
    idenLengths.append(identifierLength)
    
    translatedPart = divideStr(translatedPart).split()

    for chunk in translatedPart :

        currDataAddr += prevDataAddr
        prevDataAddr = len(chunk.replace('-','')) / 2
        addrPart = toHex(currDataAddr)
        lineNumber = (str(i+1)).rjust(6)

        res = '{0} {1} {2:28}'.format(lineNumber, addrPart, chunk)                        
       
        if translatedPart.index(chunk) == 0 :
            res += ' ' + ln.rstrip()
        res += '\n'

        lstfile.write(res)
        

def translateNum(i, ln, tokens, dir) :
    global currDataAddr, prevDataAddr, lstfile
    tokens = ln.split()
    num = tokens[2].strip()

    translation = numToHex(num, dir)
    addr = toHex(currDataAddr)
    currDataAddr += prevDataAddr
    prevDataAddr = len(translation) / 2
    lnNum = (str(i+1)).rjust(6)

    res = '{0} {1} {2:28} {3}'.format(lnNum, addr, translation, ln)
    lstfile.write(res)


def translateNumArray(i, ln, t, dir) :
    global currDataAddr, prevDataAddr, lstfile
    t[0] = t[0][t[0].index(dir)+2:].lstrip()
    arrTokens = list(map(lambda x: int(x), t))
    
    translatedPart = divideStr(numArrToHex(arrTokens, dir)).split()

    for chunk in translatedPart :
        currDataAddr += prevDataAddr
        addr = toHex(currDataAddr)
        prevDataAddr = len(chunk.replace('-','')) / 2
        lnNum = (str(i+1)).rjust(6)

        res = '{0} {1} {2:28}'.format(lnNum, addr, chunk)
        
        if translatedPart.index(chunk) == 0 :
            res += ' ' + ln.rstrip()
        res += '\n'
    
        lstfile.write(res)


def numToHex(n, dir) :
    if '0x' not in n :
        n = hex(int(n))
    return toLittleEndian(n[2:].upper().zfill(sizes[dir]))


def numArrToHex(numArr, dir) :
    hexarr = ''
    for a in numArr :
        hexarr += toLittleEndian(toHex(a, sizes[dir]))
    return hexarr


def stringToHex(strA, dir) :
    restPart = list(map(lambda x: int(x), strA[1:]))
    return strToHex(strA[0]) + numArrToHex(restPart, dir)


def stringArrToHex(strArr, dir) :
    hexstr = ''
    for a in strArr:
        hexstr += strToHex(a).ljust(sizes[dir] * 2, '0')
    return hexstr


def resMemToHex(n, dir) :
    if '0x' not in n:
        return toHex(int(n) * sizes[dir])
    else :
        return str(int(n[2:]) * sizes[dir]).upper().zfill(8)


def computeVarLengths() :
    global identifiers, idenLengths, varAndLenDict
    idenLengths = idenLengths[::-1]

    for i in range(len(idenLengths)) :
        if idenLengths[i] != 0 :
            idenLengths[i] += idenLengths[i-1]

    idenLengths = [l for l in idenLengths[::-1] if l != 0]
    for k, v in varAndLenDict.items() :
        varAndLenDict[k] = idenLengths[identifiers.index(v)]


def toHex(n, size=8) :
    return hex(int(n))[2:].upper().zfill(size)


def toLittleEndian(n) :
    return ('').join([n[i:i+2] for i in range(0, len(n), 2)][::-1]) 


def divideStr(s) :
    return '-\n'.join(s[i:i+18] for i in range(0, len(s), 18))


def strToHex(s) :
    return ('').join(map(lambda ch: hex(ord(ch))[2:].upper(), s))




# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< #




# Main Function
if __name__ == '__main__':
    input = sys.argv[1]                     # Read input file name
    assemblyfile = open(input, "r")         # Open the file and create a file object to work with it
    lstfile = open("p.lst", "w")            # Open a new file in 'write' mode to store the output


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


        # -------------------------------------------- D A T A  S E C T I O N ------------------------------------------------ #


        # If Data section is encountered, update the Data flag as TRUE
        if line.strip().startswith('section .data') :
            dataflag = True; bssflag = False
            currDataAddr = prevDataAddr = 0
            translation = translateLabelLine(lineNum, line)
            lstfile.write(translation)


        # If Data section is already TRUE, perform translation of the current line accordingly
        elif dataflag == True :
            translateDataSection(lineNum, line)


        # ---------------------------------------------- B S S  S E C T I O N ------------------------------------------------ #
    

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


        # -------------------------------------------------------------------------------------------------------------------- #




    assemblyfile.close()                 # Close the assembly file
                          


