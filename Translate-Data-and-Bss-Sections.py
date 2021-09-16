import sys

sizes = {'db' : 2, 'dw' : 4, 'dd' : 8, 'resb' : 1, 'resw' : 2, 'resd' : 4}


def toLittleEndian(num) :
    return ('').join([num[i:i+2] for i in range(0, len(num), 2)][::-1]) 


def toHex(n, size=8) :
    return hex(int(n))[2:].upper().zfill(size)
    

def translateBssTxt(num, dir) :
    return toHex(int(num) * sizes[dir])


def translateDataNum(num, dir) :
    if '0x' not in num :
        num = hex(int(num))
    return toLittleEndian(num[2:].upper().zfill(sizes[dir]))


def translateDataArr(arr, dir) :
    hexarr = ''
    for a in arr :
        hexarr += toLittleEndian(toHex(a, sizes[dir]))
    return '-\n'.join(hexarr[i:i + 18] for i in range(0, len(hexarr), 18))


def translateDataStr(strArr, dir) :
    strPart = strArr[0]
    restPart = list(map(lambda x: int(x), strArr[1:]))
    s = ('').join(map(lambda ch: hex(ord(ch))[2:].upper(), strPart))
    s += translateDataArr(restPart, dir)
    return '-\n'.join(s[i:i + 18] for i in range(0, len(s), 18))


# Main Function
if __name__ == '__main__':

    input = sys.argv[1]
    lstfile = open("p.lst", "w")
    assemblyfile = open(input, "r")

    bssflag = dataflag = False
    bssAddr = dataAddr = None
    prevAddrB = prevAddrD = None 


    for lineNum, line in enumerate(assemblyfile) :
        if len(line.strip()) == 0:
            res = '{0} {1:28} {2}'.format((str(lineNum+1)).rjust(6), '', line)
            lstfile.write(res)
            continue


        if line.strip().startswith('section .text') :
            dataflag = bssflag = False
            break


        if line.strip().startswith('section .bss') :
            bssflag = True
            bssAddr = prevAddrB = 0
            res = '{0} {1:8} {2:28} {3}'.format((str(lineNum+1)).rjust(6), '', '', line)
            lstfile.write(res)


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

    
        if line.strip().startswith('section .data') :
            dataflag = True
            dataAddr = prevAddrD = 0
            res = '{0} {1:8} {2:28} {3}'.format((str(lineNum+1)).rjust(6), '', '', line)
            lstfile.write(res)


        elif dataflag == True :
            t = line.split()
            dir = t[1]

            if dir in sizes.keys() and len(dir) == 2 :
                if line.count('"') == 2 :
                    strTokens = line.split(',')
                    strTokens[0] = strTokens[0][strTokens[0].index(dir)+2:].lstrip().replace('"','')
                    translatedPart = translateDataStr(strTokens, dir).split()
                
                    for ln in translatedPart :
                        dataAddr += prevAddrD
                        res = '{0} {1} {2:28}'.format((str(lineNum+1)).rjust(6), toHex(dataAddr), ln)
                        
                        if translatedPart.index(ln) == 0 :
                            res += ' ' + line.rstrip()
                        
                        res += '\n'
                        
                        # if len(translatedPart) > 1 and translatedPart.index(ln) == len(translatedPart) - 1 :
                        #     res += '\n'
                       
                        prevAddrD = len(ln.replace('-','')) / 2
                        lstfile.write(res)

                else :
                    t = line.split(',')
                    if len(t) == 1:
                        t = line.split()
                        num = t[2].strip()
                        translatedPart = translateDataNum(num, dir)
                        dataAddr += prevAddrD
                        res = '{0} {1} {2:28} {3}'.format((str(lineNum+1)).rjust(6), toHex(dataAddr), translatedPart, line)
                        
                        prevAddrD = len(translatedPart) / 2
                        lstfile.write(res)

                    elif len(t) > 1 :
                        t[0] = t[0][t[0].index(dir)+2:].lstrip()
                        arrTokens = list(map(lambda x: int(x), t))
                        translatedPart = translateDataArr(arrTokens, dir).split()
                        
                        for ln in translatedPart :
                            dataAddr += prevAddrD
                            res = '{0} {1} {2:28}'.format((str(lineNum+1)).rjust(6), toHex(dataAddr), ln)
                           
                            if translatedPart.index(ln) == 0 :
                                res += ' ' + line.rstrip()
                           
                            if len(translatedPart) > 1 and translatedPart.index(ln) <= (len(translatedPart) - 1) :
                                res += '\n'
                        
                            prevAddrD = len(ln.replace('-','')) / 2
                            lstfile.write(res)
                        
