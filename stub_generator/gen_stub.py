#-----------------------------------------------------------------
# gen_stub.py  -- genenrate stub code
#
from __future__ import print_function
import sys, os

from pycparser import parse_file, c_generator, c_parser, c_ast, preprocess_file

# This is not required if you've installed pycparser into
# your site-packages/ with setup.py
#
sys.path.extend(['.', '..'])

def gen_skeleton_ast(ast, C_STUB = False, S_STUB = False, A_STUB = False):
    
# Proprocessing passed in c files if needed
#     with open('c_files/tmp.c', 'w') as f:
#         print(preprocess_file('c_files/template.c'), file=f)
#     print(preprocess_file('c_files/template.c'))
#     sys.exit()

    if (C_STUB):
        template_path = 'cli_stub/'
    elif (S_STUB):
        template_path = 'ser_stub/'
    elif (A_STUB):
        template_path = 'asm_stub/'
    else:
        return
    
    libc_path = '-I../utils/fake_libc_include'
    
    if (C_STUB or S_STUB):
        ast_0_arg = parse_file(template_path + 'template_0.c', use_cpp=True, cpp_path='cpp', 
                               cpp_args=libc_path)    
        ast_1_arg = parse_file(template_path + 'template_1.c', use_cpp=True, cpp_path='cpp', 
                               cpp_args=libc_path)
        ast_2_arg = parse_file(template_path + 'template_2.c', use_cpp=True, cpp_path='cpp', 
                               cpp_args=libc_path)
        ast_3_arg = parse_file(template_path + 'template_3.c', use_cpp=True, cpp_path='cpp', 
                               cpp_args=libc_path)
        ast_4_arg = parse_file(template_path + 'template_4.c', use_cpp=True, cpp_path='cpp', 
                               cpp_args=libc_path)
    elif (A_STUB):
        ast_0_arg = []
        with open (template_path+ "template.S", "r") as myfile:
            for line in myfile:
                ast_0_arg.append(line) 
        ast_1_arg = []
        ast_2_arg = []
        ast_3_arg = []
        ast_4_arg = []
    else:
        return
    
    
    if   (C_STUB):
        dummy_func_body_list = ['FN_TYPE', 'FN_NAME', 'ARG1_T', 'ARG1_V', 'ARG2_T', 'ARG2_V'
                                , 'ARG3_T', 'ARG3_V', 'ARG4_T', 'ARG4_V']    
    elif (S_STUB):
        dummy_func_body_list = ['FN_TYPE', '__sg_FN_NAME', 'FN_NAME', 'ARG1_T', 'ARG1_V',
                                'ARG2_T', 'ARG2_V', 'ARG3_T', 'ARG3_V', 'ARG4_T', 'ARG4_V']
    elif (A_STUB):
        dummy_func_body_list = ['FUNC_NAME']
    else:
        return
    
    ast_list = [ast_0_arg, ast_1_arg, ast_2_arg, ast_3_arg, ast_4_arg, dummy_func_body_list]
    
    if   (C_STUB):    
        return ast.cli_stub_ast(ast_list)
    elif (S_STUB):    
        return ast.ser_stub_ast(ast_list)
    elif (A_STUB):    
        asm_list = ast.asm_ast(ast_list)
        print("")
        target_str = ast_0_arg[-1]
        for item in asm_list:
            ast_0_arg.append(target_str.replace('FUNC_NAME', item[0]))
        return (''.join([ str(myelement) for myelement in ast_0_arg if "FUNC_NAME" not in myelement]))
    else: 
        return
    
if __name__ == "__main__":
    if len(sys.argv) > 1:
        filename  = sys.argv[1]
    else:
        tmpPath = '/home/songjiguo/workspace/composite_test_gen/src/components/interface/sched/'
        interface_h = 'sched.h'
        filename = tmpPath + interface_h
        
    # define all necessary headerfiles to be included in stub code here
    default_cli_headers = """\
#include <cos_component.h>
#include <cos_debug.h>
#include <print.h>
#include <cstub.h>

#ifdef LOG_MONITOR
#include <log.h>
#endif
"""
    default_ser_headers = """\
#include <cos_component.h>
#include <print.h>
#ifdef LOG_MONITOR
#include <log.h>
#endif
"""
    # generate predefined AST here
    ast = parse_file(filename, use_cpp=True,
            cpp_path='cpp', 
            cpp_args=r'-I../utils/fake_libc_include')
    
    # generate new AST for client stub
    cli_ast_list = gen_skeleton_ast(ast, C_STUB = True, S_STUB = False, A_STUB = False)
    # generate new AST for server stub
    ser_ast_list = gen_skeleton_ast(ast, C_STUB = False, S_STUB = True, A_STUB = False)
    # generate new AST for stub asm
    asm_ast_list = gen_skeleton_ast(ast, C_STUB = False, S_STUB = False, A_STUB = True)

    
    # generate cli stub code from here
    print('\n***********************')
    print('  client stub code ')
    print('***********************')
    print(default_cli_headers)
    print('#include <' + interface_h + '>\n')
    generator = c_generator.CGenerator()
    generator.cli_stub = True
    for new_ast in cli_ast_list:
        result = generator.visit(new_ast)
        #result = result.replace(" ", "")  # remove "{}, ;" and white spaces
        result = result.lstrip()
        result = result.replace(";", "")
        result = result.replace("{", "")
        result = result.replace("}", "")
        result = os.linesep.join([s for s in result.splitlines() if s])  # remove empty line
        print(result)
        print('')
        
    # generate ser stub code from here
    print('\n***********************')
    print('  server stub code ')
    print('***********************')    
    print(default_ser_headers)
    print('#include <' + interface_h + '>\n')
    generator = c_generator.CGenerator()
    generator.cli_stub = False
    for new_ast in ser_ast_list:
        result = generator.visit(new_ast)  # Only True for client stub
        print(result)
        print('')        

    # generate ser stub code from here
    print('\n***********************')
    print('  asm stub code ')
    print('***********************')      
    print(asm_ast_list)
    
    
    
