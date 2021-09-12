import sys

sizes = {'db' : 2, 'dw' : 4, 'dd' : 8, 'resb' : 1, 'resw' : 2, 'resd' : 4}


def forBss(n: str, dir: str) :
    resMem = (hex(int(n) * sizes[dir])[2:]).upper().zfill(8)
    return '<res ' + resMem + '>\n'


def forDataNumbers(num: str, dir: str) :
    isHex = False
    if ('0x' not in num) :
        isHex = True
        num = hex(int(num))
    ans = num[2:].upper().zfill(sizes[dir])
    return ans if not isHex else ans + '\n'


def forDataArrays(arr: list, dir: str) :
    hexarr = ''
    for a in arr :
        hexarr += hex(a)[2:].upper().zfill(sizes[dir])
    hexarr = '-\n'.join(hexarr[i:i + 18] for i in range(0, len(hexarr), 18))
    return hexarr


def forDataStrings(st: str, dir: str) :
    hexstr = ''
    count = 0
    for ch in st :
        count += 1
        hexstr += hex(ord(ch))[2:].upper()
        if count % 9 == 0 :
            hexstr += '-\n'
    return hexstr


input = sys.argv[1]

lstfile = open("p.lst", "w")
assemblyfile = open(input, "r")

i = 1
bssflag = dataflag = False

for line in assemblyfile :
    if line.strip().startswith('section .text') :
        break

    if line.strip().startswith('section .bss') :
        bssflag = True
    
    if line.strip().startswith('section .data') :
        dataflag = True


    if bssflag == True :
        tokens = line.split()
        if ('resb' in line) or ('resw' in line) or ('resd' in line) :
            dir = tokens[1]
            num = tokens[2]
            res = (str(i)).rjust(2) + ' ' + forBss(num, dir)
            lstfile.write(res)


    if dataflag == True :
        tokens = line.split(' ')
        if ('db' in line) or ('dw' in line) or ('dd' in line) :
            dir = tokens[1]
            num = tokens[2]
            res = (str(i)).rjust(2) + ' ' + forDataNumbers(num, dir)
            lstfile.write(res)

    i += 1