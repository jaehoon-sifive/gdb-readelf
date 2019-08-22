# @author : Jaehoon Park (jaehoon.park@sifive.com)
# version 0.1

"""Utilities for parse symbol information from elf in gdb."""

import gdb
import re
import argparse

class SymbolPrinter (gdb.Command):
    """show the symbol as fromelf does"""
  
    def __init__ (self):
        super (SymbolPrinter, self).__init__ ("readelf", gdb.COMMAND_USER)

    def __print_title__(self):
        print "%-12s %-10s %-40s %s" % ("address", "size", "variable name", "type")
  
    def __format_print__(self, addr, size, name, typename):
        print "%-12s 0x%-8x %-40s %s" % (addr, size, name, typename)

    def __select_printer__(self, symbol_name, symbol_type):
        code = symbol_type.code
        if symbol_type.code == gdb.TYPE_CODE_STRUCT:
            self.__print_struct__(symbol_name, symbol_type)
        elif symbol_type.code == gdb.TYPE_CODE_ARRAY:
            self.__print_array__(symbol_name, symbol_type)

    def __print_array__(self, array_name, array_type):
        array_size = array_type.sizeof
        array_0_val = gdb.parse_and_eval(array_name + "[0]")
        array_0_size = array_0_val.type.sizeof
        count = array_size / array_0_size
        for i in range(0,count):
            array_item_name = "%s[%d]" % (array_name, i)
            array_item_addr = gdb.parse_and_eval("&" + array_item_name).__str__().split(" ")[0]
            array_item_type_name = gdb.execute("whatis " + array_item_name, to_string=True).replace("type = ", "").replace("\n","")
            self.__format_print__(array_item_addr, array_0_size, array_item_name, array_item_type_name)

            array_0_type = array_0_val.type.unqualified ().strip_typedefs ()
            self.__select_printer__(array_item_name, array_0_type)

    def __print_struct__(self, symbol_name, symbol_type):
        for field in symbol_type.fields():
            field_name = symbol_name + "." + field.name
            filed_size = field.type.sizeof
            field_addr = gdb.parse_and_eval("&" + field_name).__str__().split(" ")[0]
            field_type_name = gdb.execute("whatis " + field_name, to_string=True).replace("type = ", "").replace("\n","")
      
            self.__format_print__(field_addr, filed_size, field_name, field_type_name)      
            
            field_type = field.type.unqualified ().strip_typedefs ()
            self.__select_printer__(field_name, field_type)

    def __print_symbol__(self, symbol_name):
        symbol = gdb.lookup_global_symbol(symbol_name)
        if symbol != None:
            symbol_type = symbol.type
            if symbol_type.code == gdb.TYPE_CODE_TYPEDEF:
                symbol_type = symbol.type.unqualified ().strip_typedefs ()  

            symbol_addr = gdb.parse_and_eval("&" + symbol_name).__str__().split(" ")[0]
            symbol_type_name = gdb.execute("whatis " + symbol_name, to_string=True).replace("type = ", "").replace("\n","")
    
            self.__print_title__()
            self.__format_print__(symbol_addr, symbol_type.sizeof, symbol_name, symbol_type_name)
            self.__select_printer__(symbol_name, symbol_type)

        else:
            print "No symbol found - " + symbol_name

    def __print_all_symbols__(self):
        symbol_full_list = gdb.execute("info variables", to_string=True)
        symbol_lines = symbol_full_list.split('\n')
        for symbol_line in symbol_lines:
            if re.search("^(Non-debugging symbols)", symbol_line):
                return

            if re.search("^(File|All defined variables)", symbol_line):
                continue

            symbols = symbol_line.split(" ")
            if len(symbols) >= 2:
                symbol = symbols[-1].replace("*","").replace(";","")                
                idx = symbol.find("[")
                if idx > 0:
                    symbol = symbol[0:idx]
                
                self.__print_symbol__(symbol)
                print("")
    
    def invoke (self, arg, from_tty):
        argv = gdb.string_to_argv(arg)
        parser = argparse.ArgumentParser()
        parser.add_argument("-s", "--sym", metavar='symbol', type=str, help='specifiy the symbol name of variables', action='store')
        parser.add_argument("-a", "--all", help="show all available symbols", action="store_true")
        parser.add_argument("-o", "--output", metavar='file', type=str, help="the output file(defaults to stdout)", action="store", default='stdout')
        args = parser.parse_args(argv)

        if args.output != 'stdout':
            gdb.execute("set height 0")
            gdb.execute("set logging redirect on")
            gdb.execute("set logging overwrite on")
            gdb.execute("set logging on " + args.output)

        if args.all:
            self.__print_all_symbols__()
        elif args.sym:
            self.__print_symbol__(args.sym)

        if args.output != 'stdout':
            gdb.execute("set logging off")
            gdb.execute("set logging redirect off")

SymbolPrinter ()