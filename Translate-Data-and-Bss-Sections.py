import sys

sizes = {'db' : 2, 'dw' : 4, 'dd' : 8, 'resb' : 1, 'resw' : 2, 'resd' : 4}


def forBss(n, dir) :
    resMem = (hex(int(n) * sizes[dir])[2:]).upper().zfill(8)
    return '<res ' + resMem + '>'


def toLittleEndian(n) :
    return ('').join([n[i:i+2] for i in range(0, len(n), 2)])


def forDataNumbers(num, dir) :
    if '0x' not in num :
        num = hex(int(num)).upper()
    return toLittleEndian(num[2:].zfill(sizes[dir]))


def forDataArrays(arr, dir) :
    hexarr = ''
    for a in arr :
        hexarr += toLittleEndian(hex(a)[2:].upper().zfill(sizes[dir]))
    hexarr = '-\n'.join(hexarr[i:i + 18] for i in range(0, len(hexarr), 18))
    return hexarr


def forDataStrings(s) :
    tempstr = ('').join(map(lambda ch: hex(ord(ch))[2:].upper(), s))
    hexstr = '-\n'.join(tempstr[i:i + 18] for i in range(0, len(tempstr), 18))
    return hexstr


# Main Function
if __name__ == '__main__':

    input = sys.argv[1]

    lstfile = open("p.lst", "w")
    assemblyfile = open(input, "r")

    i = 1
    bssflag = False
    dataflag = False

    for line in assemblyfile :
        if len(line.strip()) == 0:
            res = '{0} {1:32} {2}'.format((str(i)).rjust(2), ' ', line)
            lstfile.write(res)


        if line.strip().startswith('section .text') :
            break


        if line.strip().startswith('section .bss') :
            bssflag = True
            res = '{0} {1:32} {2}'.format((str(i)).rjust(2), '', line)
            lstfile.write(res)
        

        if line.strip().startswith('section .data') :
            dataflag = True
            res = '{0} {1:32} {2}'.format((str(i)).rjust(2), '', line)
            lstfile.write(res)


        if bssflag == True :
            tokens = line.split()
            if ('resb' in line) or ('resw' in line) or ('resd' in line) :
                dir = tokens[1]
                num = tokens[2]
                res = '{0} {1:36} {2}'.format((str(i)).rjust(2), forBss(num, dir), line)
                lstfile.write(res)


        if dataflag == True :
            tokens = line.split(' ')
            if ('db' in line) or ('dw' in line) or ('dd' in line) :
                dir = tokens[1]
                num = tokens[2].strip()
                res = '{0} {1:36} {2}'.format((str(i)).rjust(2), forDataNumbers(num, dir), line)
                lstfile.write(res)

        i += 1
