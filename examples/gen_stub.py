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

def gen_skeleton_ast(ast, NORMAL = True, STUB = False):
    print('\n*****')
    
# Proprocessing passed in c files here
#     with open('c_files/tmp.c', 'w') as f:
#         print(preprocess_file('c_files/template.c'), file=f)
#     print(preprocess_file('c_files/template.c'))
#     sys.exit()

    if (NORMAL):
        template_path = 'c_files/normal/'
    elif (STUB):
        template_path = 'c_files/stub/'
    else:
        return
    
    libc_path = '-I../utils/fake_libc_include'
    
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

    if (NORMAL):
        dummy_func_body_list = ['R_TYPE', 'ARG_1', 'ARG_2', 'ARG_3', 'ARG_4']
    elif (STUB):
        dummy_func_body_list = ['FUNC_T', 'FUNC_N', 'ARG1_T', 'ARG1_V', 'ARG2_T', 'ARG2_V'
                                , 'ARG3_T', 'ARG3_V', 'ARG4_T', 'ARG4_V']
    else:
        return
    
    ast_list = [ast_0_arg, ast_1_arg, ast_2_arg, ast_3_arg, ast_4_arg, dummy_func_body_list]
    
    if (NORMAL):    
        return ast.update_normal_ast(ast_list)
    elif (STUB):    
        return ast.update_stub_ast(ast_list)
    else: 
        return
    
if __name__ == "__main__":
    if len(sys.argv) > 1:
        filename  = sys.argv[1]
    else:
        #filename = 'c_files/interface.h'
        tmpPath = '/home/songjiguo/workspace/composite_test_gen/src/components/interface/mem_mgr/'
        filename = tmpPath + 'mem_mgr.h'
        
    # define all necessary headerfiles to be included in stub code here
    default_headers = """\
#include <cos_component.h>
#include <cos_debug.h>
#include <print.h>
#include <cstub.h>

#ifdef LOG_MONITOR
#include <log.h>
#endif

"""
    # generate predefined AST here
    ast = parse_file(filename, use_cpp=True,
            cpp_path='cpp', 
            cpp_args=r'-I../utils/fake_libc_include')
    
    # generate new AST here
    gen_ast_list = gen_skeleton_ast(ast, NORMAL = False, STUB = True)
    
    # generate c code from here
    print('\n\n***output_c***\n\n')
    print(default_headers)
    generator = c_generator.CGenerator()
    for new_ast in gen_ast_list:
        result = generator.visit(new_ast)
        #result = result.replace(" ", "")  # remove "{}, ;" and white spaces
        result = result.lstrip()
        result = result.replace(";", "")
        result = result.replace("{", "")
        result = result.replace("}", "")
        result = os.linesep.join([s for s in result.splitlines() if s])  # remove empty line
        print(result)
        print('')
        
