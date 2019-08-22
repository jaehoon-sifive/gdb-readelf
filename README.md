It's gdb python extension to show symbol information of variables

How to launch:

	gdb [elf] -x readelf.py ; $ gdb dhrystone.elf -x readelf.py

How to use in gdb:
	Show one symbol
	 readelf -s symbol		; (gdb) readelf -s Arr_1_Glob

	Show all symbols
	 readelf -a			; (gdb) readelf -a

	Redirect output to file
	 readelf -a -o filename		; (gdb) readlef -a -o output.txt
