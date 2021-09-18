section .data
	a db 60
	b dw 120
	c dd 123456
	d dd 0x123456
	
	msg1 db "Enter 3 values",10,0
	msg2 db "%d%d%d",0
	msg3 db "0123456789abcdefghijklmNOPQRSTUVWXYZ",0
	
	len1 equ $-msg1
	len2 equ $-msg2
	len3 equ $-msg3	
	
	Array1 dw 10,20,30,40
	Array2 dd 10,20,30,40
	Array3 db "Indigo", "Gray", "Navy", "Pastel", "White"

section .bss
	i resd 1
	j resb 100
	k resw 10
	Dest1 resb len1
	Dest2 resb len2
	Dest3 resb len3

section .text
	global main

main:
	add dword[ecx],10
	add dword[a],10
	add word[ecx],10
	add word[a],10
	
	
