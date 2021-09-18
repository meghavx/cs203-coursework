
import sys

# Dictionary to store the relevant size directives along with their sizes 
sizes = {'db' : 2, 'dw' : 4, 'dd' : 8, 'resb' : 1, 'resw' : 2, 'resd' : 4}


def toLittleEndian(num) :
    """ Utility function that returns a given hex value in the little endian format """
    return ('').join([num[i:i+2] for i in range(0, len(num), 2)][::-1]) 


def toHex(n, size=8) :
    """ Utility function that returns a given number's hex equivalent value """
    return hex(int(n))[2:].upper().zfill(size)
    

def translateBssTxt(num, dir) :
    """ Function that returns the hex representation of the memory to be reserved in the Bss section
        according to the given size"""
    return toHex(int(num) * sizes[dir])


def translateDataNum(num, dir) :
    """ Function that returns the hex representation of a 'number' defined in the Data section """
    if '0x' not in num :
        num = hex(int(num))
    return toLittleEndian(num[2:].upper().zfill(sizes[dir]))


def divideStr(s) :
    """ Function to divide a given string into chunks of max 9 bytes each """
    return '-\n'.join(s[i:i+18] for i in range(0, len(s), 18))


def translateStrToHex(s) :
    """ Function to translate a given string into hex format """
    return ('').join(map(lambda ch: hex(ord(ch))[2:].upper(), s))


def translateDataNumArray(arr, dir) :
    """ Function that returns the hex representation of an 'numeric array' defined in the Data section """
    hexarr = ''
    for a in arr :
        hexarr += toLittleEndian(toHex(a, sizes[dir]))
    return divideStr(hexarr)


def translateDataStr(strArr, dir) :
    """ Function that returns the hex representation of a 'string' defined in the Data section """
    restPart = list(map(lambda x: int(x), strArr[1:]))
    s = translateStrToHex(strArr[0]) + translateDataNumArray(restPart, dir)
    return divideStr(s)


def translateDataStrArray(arr, dir) :
    """ Function that returns the hex representation of an 'string array' defined in the Data section """
    hexstr = ''
    for a in arr:
        hexstr += translateStrToHex(a).ljust(sizes[dir]*2, '0')
    return divideStr(hexstr)


# Main Function
if __name__ == '__main__':

    # Read input file name
    input = sys.argv[1]

    # Open the file and create a file object to work with it
    assemblyfile = open(input, "r")
    
    # Open a new file in 'write' mode to store the output
    lstfile = open("p.lst", "w")


    # Define and initialize relevant variables
    bssflag = dataflag = False
    bssAddr = dataAddr = None
    prevAddrB = prevAddrD = None 

    varDict = {}


    # Read the input file line by line to perform the translation 
    for lineNum, line in enumerate(assemblyfile) :

        # If an empty line is encountered, print it and continue with the next iteration
        if len(line.strip()) == 0:
            res = '{0} {1:28} {2}'.format((str(lineNum+1)).rjust(6), '', line)
            lstfile.write(res)
            continue

        # Update the Data and Bss flags as 'FALSE' as soon as Text section is encountered
        # And break out of the loop [that is, stop reading the file for further lines]
        if line.strip().startswith('section .text') :
            dataflag = bssflag = False
            break


        # If Bss section is encountered, update the Bss flag as TRUE
        if line.strip().startswith('section .bss') :
            bssflag = True
            bssAddr = prevAddrB = 0
            res = '{0} {1:8} {2:28} {3}'.format((str(lineNum+1)).rjust(6), '', '', line)
            lstfile.write(res)


        # If Bss section is already TRUE, perform translation of the current line accordingly
        elif bssflag == True :
            tokens = line.split()
            if ('resb' in line) or ('resw' in line) or ('resd' in line) :
                dir = tokens[1]
                num = tokens[2].strip()
                translatedPart = translateBssTxt(num, dir)
                bssAddr += prevAddrB
                res = '{0} {1} {2:28} {3}'.format((str(lineNum+1)).rjust(6), toHex(bssAddr), '<res ' + translatedPart + '>', line)
                prevAddrB = int(translatedPart,16)
                lstfile.write(res)


         # If Data section is encountered, update the Data flag as TRUE
        if line.strip().startswith('section .data') :
            dataflag = True
            dataAddr = prevAddrD = 0
            res = '{0} {1:8} {2:28} {3}'.format((str(lineNum+1)).rjust(6), '', '', line)
            lstfile.write(res)


        # If Data section is already TRUE, perform translation of the current line accordingly
        elif dataflag == True :
            t = line.split()
            dir = t[1]

            # If the directive found is one present in the 'sizes' doctionary, we proceed with this if block
            if dir in sizes.keys() and len(dir) == 2 :


                # If the line contains a <<<< single string >>>>, we do the translation accordingly
                if line.count('"') == 2 :
                    strTokens = line.split(',')
                    strTokens[0] = strTokens[0][strTokens[0].index(dir)+2:].lstrip().replace('"','')
                    translatedPart = translateDataStr(strTokens, dir).split()               
                    for chunk in translatedPart :
                        dataAddr += prevAddrD
                        res = '{0} {1} {2:28}'.format((str(lineNum+1)).rjust(6), toHex(dataAddr), chunk)                        
                        if translatedPart.index(chunk) == 0 :
                            res += ' ' + line.rstrip()
                        res += '\n'
                        prevAddrD = len(chunk.replace('-','')) / 2
                        lstfile.write(res)


                # If the line contains an <<<< array of strings >>>>
                elif line.count('"') > 2 :
                    strTokens = line.split(',')
                    strTokens[0] = strTokens[0][strTokens[0].index(dir)+2:]
                    strTokens = list(map(lambda s: s.lstrip().replace('"','').replace("\n",''), strTokens))
                    translatedPart = translateDataStrArray(strTokens, dir).split()
                    print(translatedPart)
                    for chunk in translatedPart :
                        dataAddr += prevAddrD
                        res = '{0} {1} {2:28}'.format((str(lineNum+1)).rjust(6), toHex(dataAddr), chunk)
                        if translatedPart.index(chunk) == 0 :
                            res += ' ' + line.rstrip()
                        res += '\n'
                        prevAddrD = len(chunk.replace('-','')) / 2
                        lstfile.write(res)
                    

                # If line doesn't contain a string value, it must be either a single number or an array of numbers
                else :
                    t = line.split(',')
                    # Check if it is a <<<< single number >>>>
                    if len(t) == 1:
                        t = line.split()
                        num = t[2].strip()
                        translatedPart = translateDataNum(num, dir)
                        dataAddr += prevAddrD
                        res = '{0} {1} {2:28} {3}'.format((str(lineNum+1)).rjust(6), toHex(dataAddr), translatedPart, line)
                        prevAddrD = len(translatedPart) / 2
                        lstfile.write(res)


                    # Check if if is an <<<< array of numbers >>>>
                    elif len(t) > 1 :
                        t[0] = t[0][t[0].index(dir)+2:].lstrip()
                        arrTokens = list(map(lambda x: int(x), t))
                        translatedPart = translateDataNumArray(arrTokens, dir).split()
                        for chunk in translatedPart :
                            dataAddr += prevAddrD
                            res = '{0} {1} {2:28}'.format((str(lineNum+1)).rjust(6), toHex(dataAddr), chunk)
                            if translatedPart.index(chunk) == 0 :
                                res += ' ' + line.rstrip()
                            res += '\n'
                            prevAddrD = len(chunk.replace('-','')) / 2
                            lstfile.write(res)
             
             
            elif dir == 'equ' :
                res = '{0} {1:8} {2:28} {3}'.format((str(lineNum+1)).rjust(6), '', '', line)
                lstfile.write(res) 


# Close the assembly file
assemblyfile.close()
                          
