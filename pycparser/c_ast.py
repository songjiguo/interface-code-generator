#-----------------------------------------------------------------
# ** ATTENTION **
# This code was automatically generated from the file:
# _c_ast.cfg 
#
# Do not modify it directly. Modify the configuration file and
# run the generator again.
# ** ** *** ** **
#
# pycparser: c_ast.py
#
# AST Node classes.
#
# Copyright (C) 2008-2012, Eli Bendersky
# License: BSD
#-----------------------------------------------------------------


import sys
from reportlab.graphics.barcode.code128 import seta
import copy

from collections import Mapping, Set, Sequence 
string_types = (str, unicode) if str is bytes else (str, bytes)
iteritems = lambda mapping: getattr(mapping, 'iteritems', mapping.items)()


class Node(object):
    """ Abstract base class for AST nodes.
    """
    def children(self):
        """ A sequence of all children that are Nodes
        """
        pass

    def show(self, buf=sys.stdout, offset=0, attrnames=False, nodenames=False, showcoord=False, _my_node_name=None):
        """ Pretty print the Node and all its attributes and
            children (recursively) to a buffer.
            
            buf:   
                Open IO buffer into which the Node is printed.
            
            offset: 
                Initial offset (amount of leading spaces) 
            
            attrnames:
                True if you want to see the attribute names in
                name=value pairs. False to only see the values.
                
            nodenames:
                True if you want to see the actual node names 
                within their parents.
            
            showcoord:
                Do you want the coordinates of each Node to be
                displayed.
        """
        lead = ' ' * offset
        if nodenames and _my_node_name is not None:
            buf.write(lead + self.__class__.__name__ + ' <' + _my_node_name + '>: ')
        else:
            buf.write(lead + self.__class__.__name__ + ': ')

        if self.attr_names:
            if attrnames:
                nvlist = [(n, getattr(self, n)) for n in self.attr_names]
                attrstr = ', '.join('%s=%s' % nv for nv in nvlist)
            else:
                vlist = [getattr(self, n) for n in self.attr_names]
                attrstr = ', '.join('%s' % v for v in vlist)
            buf.write(attrstr)

        if showcoord:
            buf.write(' (at %s)' % self.coord)
        buf.write('\n')

        for (child_name, child) in self.children():
            child.show(
                buf,
                offset=offset + 2,
                attrnames=attrnames,
                nodenames=nodenames,
                showcoord=showcoord,
                _my_node_name=child_name)       
            
    def walk_node(self, buf=sys.stdout, offset=0, attrnames=True, nodenames=True, showcoord=False, _my_node_name=None):
        lead = ' ' * offset
        if nodenames and _my_node_name is not None:
            buf.write(lead + self.__class__.__name__ + ' <' + _my_node_name + '>: ')
        else:
            buf.write(lead + self.__class__.__name__ + ': ')

        if self.attr_names:
            if attrnames:
#                 for n in self.attr_names:
#                     if (getattr(self,n) == 'FN_NAME'):
#                         setattr(self, n, 'test')
                nvlist = [(n, getattr(self, n)) for n in self.attr_names]
                attrstr = ', '.join('%s=%s' % nv for nv in nvlist)
            else:
                vlist = [getattr(self, n) for n in self.attr_names]
                attrstr = ', '.join('%s' % v for v in vlist)
            buf.write(attrstr)

        if showcoord:
            buf.write(' (at %s)' % self.coord)
        buf.write('\n')

        for (child_name, child) in self.children():
            child.walk_node(
                buf,
                offset=offset + 2,
                attrnames=attrnames,
                nodenames=nodenames,
                showcoord=showcoord,
                _my_node_name=child_name)    
            
    def objwalk(self, obj, path=(), memo=None):
        if memo is None:
            memo = set()
        iterator = None
        if isinstance(obj, Mapping):
            iterator = iteritems
        elif isinstance(obj, (Sequence, Set)) and not isinstance(obj, string_types):
            iterator = enumerate
        if iterator:
            if id(obj) not in memo:
                memo.add(id(obj))
                for path_component, value in iterator(obj):
                    for result in self.objwalk(value, path + (path_component,), memo):
                        yield result
                memo.remove(id(obj))
        else:
            yield path, obj

    def find_replace(self, old, new, buf=sys.stdout, offset=0, attrnames=True, nodenames=True, showcoord=False, _my_node_name=None):
        if self.attr_names:
            for n in self.attr_names:
                if type(getattr(self,n)) is list:
                    for tmp_obj in getattr(self,n):
                        if (tmp_obj == old):
                            tmpList = getattr(self,n)
                            #print(tmpList[0])
                            tmpList[0] = new                            
                else:
                    tmp_obj = getattr(self,n)
                    if (tmp_obj == old):
                        setattr(self, n, new)

        for (child_name, child) in self.children():
            child.find_replace(
                old,
                new,
                buf,
                offset=offset + 2,
                attrnames=attrnames,
                nodenames=nodenames,
                showcoord=showcoord,
                _my_node_name=child_name)    

    def update_normal_ast(self, ast_arg_list):
        
        ret_ast_list      = []
        dummy_body_list   = ast_arg_list[-1]
        
        #self.walk_node(sys.stdout, 0, True, True, False, 'OldAST')  # remove later
        
        for ext_decl in self.ext:
            func_body_list    = []   # reset this for each declaration
            #print(ext_decl.__class__.__name__)
            if (ext_decl.__class__.__name__ == 'Typedef'):
                continue
            #print(ext_decl.name)
            func_decltype = ext_decl.type
            #print(len(func_decltype.args.params))
            if hasattr(func_decltype.args, 'params'):
                for params in func_decltype.args.params:
                    param_type = params.type
                    if (param_type.__class__.__name__ == 'PtrDecl'):
                        param_type = param_type.type
                        # param_type.type.names[0] = param_type.type.names[0] + ' *'
                    if (param_type.declname == None and param_type.type.names[0] == 'void'):
                        continue
                    tmpstr = ' '.join('%s' % tt for tt in param_type.type.names)
                    #print(tmpstr + ' ' + param_type.declname)
                    func_body_list.append(tmpstr)  # replace args in body
                    func_body_list.append(param_type.declname)
                    # print(params.name)
            ret_fn = func_decltype.type
            if (ret_fn.__class__.__name__ == 'PtrDecl'):
                ret_fn = ret_fn.type
            #tmpstr = ', '.join('%s' % tt for tt in ret_fn.type.names)
            tmpstr = ' '.join('%s' % tt for tt in ret_fn.type.names)
            #print(tmpstr + ' ' + ret_fn.declname)
            func_body_list.insert(0, tmpstr)
            func_body_list.insert(1, '__sg_' + ret_fn.declname)
            func_body_list.insert(2, ret_fn.declname)
            
            if hasattr(func_decltype.args, 'params'):
                arg_list_len = len(func_decltype.args.params)
                # for some functions that have no parameter, but pass 'void'
                param_type = func_decltype.args.params[0].type
                if (param_type.declname == None and param_type.type.names[0] == 'void'):
                    arg_list_len = arg_list_len -1
                
            else:
                arg_list_len = 0
            
            #print(dummy_body_list)
            #print(func_body_list)
            tmp_ast = ast_arg_list[arg_list_len]
            update_ast = copy.deepcopy(tmp_ast)   # make a copy of ast here            
            #update_ast.walk_node(sys.stdout, 0, True, True, False, 'Before')
            for tmpObj in update_ast.ext:
                if (tmpObj.__class__.__name__ == 'FuncDef'):
                    headObj = tmpObj.decl
                    pos = 0
                    for new in func_body_list:
                        headObj.find_replace(dummy_body_list[pos], new, sys.stdout, 0, True, True, False, 'updateBody')
                        pos = pos + 1

                    bodyObj = tmpObj.body
                    pos = 0
                    for new in func_body_list:
                        bodyObj.find_replace(dummy_body_list[pos], new, sys.stdout, 0, True, True, False, 'updateBody')
                        pos = pos + 1
                    
            #print('')
            #update_ast.walk_node(sys.stdout, 0, True, True, False, 'After')
            ret_ast_list.append(update_ast)  
 
        return ret_ast_list
    
    def update_stub_ast(self, ast_arg_list):
        
        ret_ast_list      = []
        dummy_body_list   = ast_arg_list[-1]
        
        #self.walk_node(sys.stdout, 0, True, True, False, 'OldAST')  # remove later
        
        for ext_decl in self.ext:
            func_body_list    = []   # reset this for each declaration
            if (ext_decl.__class__.__name__ == 'Typedef'):
                continue
            #print("\n\n*******\n")
            #print(ext_decl.name)
            func_decltype = ext_decl.type
            #print(len(func_decltype.args.params))
            if hasattr(func_decltype.args, 'params'):
                for params in func_decltype.args.params:
                    param_type = params.type    
                    if (param_type.__class__.__name__ == 'PtrDecl'):
                        param_type = param_type.type
                        # param_type.type.names[0] = param_type.type.names[0] + ' *'
                        
                    # for some functions that have no parameter, but pass 'void'                
                    if (param_type.declname == None and param_type.type.names[0] == 'void'):
                        continue                    
                    tmpstr = ' '.join('%s' % tt for tt in param_type.type.names)
                    #print(tmpstr + ' ' + param_type.declname)
                    func_body_list.append(tmpstr)
                    func_body_list.append(param_type.declname)  # replace args in body
            ret_fn = func_decltype.type
            if (ret_fn.__class__.__name__ == 'PtrDecl'):
                ret_fn = ret_fn.type
                #ret_fn.type.names[0] = ret_fn.type.names[0] + ' *'
            #tmpstr = ', '.join('%s' % tt for tt in ret_fn.type.names)
            tmpstr = ' '.join('%s' % tt for tt in ret_fn.type.names)
            #print(tmpstr + ' ' + ret_fn.declname)
            #func_body_list.insert(0, tmpstr)
            func_body_list.insert(0, tmpstr)
            func_body_list.insert(1, ret_fn.declname)
            
            if hasattr(func_decltype.args, 'params'):
                arg_list_len = len(func_decltype.args.params)
                # for some functions that have no parameter, but pass 'void'
                param_type = func_decltype.args.params[0].type
                if (param_type.declname == None and param_type.type.names[0] == 'void'):
                    arg_list_len = arg_list_len -1
            else:
                arg_list_len = 0
            
            #print(dummy_body_list)
            #print(func_body_list)
            tmp_ast = ast_arg_list[arg_list_len]
            update_ast = copy.deepcopy(tmp_ast)   # make a copy of ast here
            #update_ast.walk_node(sys.stdout, 0, True, True, False, 'Before---')
            for tmpObj in update_ast.ext:
                if (tmpObj.__class__.__name__ == 'FuncDef'):
                    funObj = tmpObj.decl.type.args
                    pos = 0
                    for new in func_body_list:
                        funObj.find_replace(dummy_body_list[pos], new, sys.stdout, 0, True, True, False, 'updateBody')
                        pos = pos + 1
                        
                    bodyObj = tmpObj.body                    
                    pos = 0
                    for new in func_body_list:
                        bodyObj.find_replace(dummy_body_list[pos], new, sys.stdout, 0, True, True, False, 'updateBody')
                        pos = pos + 1                        
                    
            #print('')
            #update_ast.walk_node(sys.stdout, 0, True, True, False, 'After')
            ret_ast_list.append(update_ast)  

        return ret_ast_list    

    def update_asm_ast(self, ast_arg_list):
        
        ret_ast_list      = []
        dummy_body_list   = ast_arg_list[-1]
        
        #self.walk_node(sys.stdout, 0, True, True, False, 'ASMAST')  # remove later
        for ext_decl in self.ext:
            func_body_list    = []   # reset this for each declaration
            if (ext_decl.__class__.__name__ == 'Typedef'):
                continue
#             print("\n\n*******\n")
#             print(ext_decl.name)
            func_decltype = ext_decl.type

            ret_fn = func_decltype.type
            if (ret_fn.__class__.__name__ == 'PtrDecl'):
                ret_fn = ret_fn.type
            func_body_list.append(ret_fn.declname)
            
#             print(dummy_body_list)
#             print(func_body_list)
            ret_ast_list.append(func_body_list)

        return ret_ast_list


class NodeVisitor(object):
    """ A base NodeVisitor class for visiting c_ast nodes. 
        Subclass it and define your own visit_XXX methods, where
        XXX is the class name you want to visit with these 
        methods.
        
        For example:
        
        class ConstantVisitor(NodeVisitor):
            def __init__(self):
                self.values = []
            
            def visit_Constant(self, node):
                self.values.append(node.value)

        Creates a list of values of all the constant nodes 
        encountered below the given node. To use it:
        
        cv = ConstantVisitor()
        cv.visit(node)
        
        Notes:
        
        *   generic_visit() will be called for AST nodes for which 
            no visit_XXX method was defined. 
        *   The children of nodes for which a visit_XXX was 
            defined will not be visited - if you need this, call
            generic_visit() on the node. 
            You can use:
                NodeVisitor.generic_visit(self, node)
        *   Modeled after Python's own AST visiting facilities
            (the ast module of Python 3.0)
    """
    def visit(self, node):
        """ Visit a node. 
        """
        method = 'visit_' + node.__class__.__name__
        visitor = getattr(self, method, self.generic_visit)
        return visitor(node)
        
    def generic_visit(self, node):
        """ Called if no explicit visitor function exists for a 
            node. Implements preorder visiting of the node.
        """
        for c_name, c in node.children():
            self.visit(c)


class ArrayDecl(Node):
    def __init__(self, type, dim, coord=None):
        self.type = type
        self.dim = dim
        self.coord = coord

    def children(self):
        nodelist = []
        if self.type is not None: nodelist.append(("type", self.type))
        if self.dim is not None: nodelist.append(("dim", self.dim))
        return tuple(nodelist)

    attr_names = ()

class ArrayRef(Node):
    def __init__(self, name, subscript, coord=None):
        self.name = name
        self.subscript = subscript
        self.coord = coord

    def children(self):
        nodelist = []
        if self.name is not None: nodelist.append(("name", self.name))
        if self.subscript is not None: nodelist.append(("subscript", self.subscript))
        return tuple(nodelist)

    attr_names = ()

class Assignment(Node):
    def __init__(self, op, lvalue, rvalue, coord=None):
        self.op = op
        self.lvalue = lvalue
        self.rvalue = rvalue
        self.coord = coord

    def children(self):
        nodelist = []
        if self.lvalue is not None: nodelist.append(("lvalue", self.lvalue))
        if self.rvalue is not None: nodelist.append(("rvalue", self.rvalue))
        return tuple(nodelist)

    attr_names = ('op',)

class BinaryOp(Node):
    def __init__(self, op, left, right, coord=None):
        self.op = op
        self.left = left
        self.right = right
        self.coord = coord

    def children(self):
        nodelist = []
        if self.left is not None: nodelist.append(("left", self.left))
        if self.right is not None: nodelist.append(("right", self.right))
        return tuple(nodelist)

    attr_names = ('op',)

class Break(Node):
    def __init__(self, coord=None):
        self.coord = coord

    def children(self):
        return ()

    attr_names = ()

class Case(Node):
    def __init__(self, expr, stmts, coord=None):
        self.expr = expr
        self.stmts = stmts
        self.coord = coord

    def children(self):
        nodelist = []
        if self.expr is not None: nodelist.append(("expr", self.expr))
        for i, child in enumerate(self.stmts or []):
            nodelist.append(("stmts[%d]" % i, child))
        return tuple(nodelist)

    attr_names = ()

class Cast(Node):
    def __init__(self, to_type, expr, coord=None):
        self.to_type = to_type
        self.expr = expr
        self.coord = coord

    def children(self):
        nodelist = []
        if self.to_type is not None: nodelist.append(("to_type", self.to_type))
        if self.expr is not None: nodelist.append(("expr", self.expr))
        return tuple(nodelist)

    attr_names = ()

class Compound(Node):
    def __init__(self, block_items, coord=None):
        self.block_items = block_items
        self.coord = coord

    def children(self):
        nodelist = []
        for i, child in enumerate(self.block_items or []):
            nodelist.append(("block_items[%d]" % i, child))
        return tuple(nodelist)

    attr_names = ()

class CompoundLiteral(Node):
    def __init__(self, type, init, coord=None):
        self.type = type
        self.init = init
        self.coord = coord

    def children(self):
        nodelist = []
        if self.type is not None: nodelist.append(("type", self.type))
        if self.init is not None: nodelist.append(("init", self.init))
        return tuple(nodelist)

    attr_names = ()

class Constant(Node):
    def __init__(self, type, value, coord=None):
        self.type = type
        self.value = value
        self.coord = coord

    def children(self):
        nodelist = []
        return tuple(nodelist)

    attr_names = ('type', 'value',)

class Continue(Node):
    def __init__(self, coord=None):
        self.coord = coord

    def children(self):
        return ()

    attr_names = ()

class Decl(Node):
    def __init__(self, name, quals, storage, funcspec, type, init, bitsize, coord=None):
        self.name = name
        self.quals = quals
        self.storage = storage
        self.funcspec = funcspec
        self.type = type
        self.init = init
        self.bitsize = bitsize
        self.coord = coord

    def children(self):
        nodelist = []
        if self.type is not None: nodelist.append(("type", self.type))
        if self.init is not None: nodelist.append(("init", self.init))
        if self.bitsize is not None: nodelist.append(("bitsize", self.bitsize))
        return tuple(nodelist)

    attr_names = ('name', 'quals', 'storage', 'funcspec',)

class DeclList(Node):
    def __init__(self, decls, coord=None):
        self.decls = decls
        self.coord = coord

    def children(self):
        nodelist = []
        for i, child in enumerate(self.decls or []):
            nodelist.append(("decls[%d]" % i, child))
        return tuple(nodelist)

    attr_names = ()

class Default(Node):
    def __init__(self, stmts, coord=None):
        self.stmts = stmts
        self.coord = coord

    def children(self):
        nodelist = []
        for i, child in enumerate(self.stmts or []):
            nodelist.append(("stmts[%d]" % i, child))
        return tuple(nodelist)

    attr_names = ()

class DoWhile(Node):
    def __init__(self, cond, stmt, coord=None):
        self.cond = cond
        self.stmt = stmt
        self.coord = coord

    def children(self):
        nodelist = []
        if self.cond is not None: nodelist.append(("cond", self.cond))
        if self.stmt is not None: nodelist.append(("stmt", self.stmt))
        return tuple(nodelist)

    attr_names = ()

class EllipsisParam(Node):
    def __init__(self, coord=None):
        self.coord = coord

    def children(self):
        return ()

    attr_names = ()

class EmptyStatement(Node):
    def __init__(self, coord=None):
        self.coord = coord

    def children(self):
        return ()

    attr_names = ()

class Enum(Node):
    def __init__(self, name, values, coord=None):
        self.name = name
        self.values = values
        self.coord = coord

    def children(self):
        nodelist = []
        if self.values is not None: nodelist.append(("values", self.values))
        return tuple(nodelist)

    attr_names = ('name',)

class Enumerator(Node):
    def __init__(self, name, value, coord=None):
        self.name = name
        self.value = value
        self.coord = coord

    def children(self):
        nodelist = []
        if self.value is not None: nodelist.append(("value", self.value))
        return tuple(nodelist)

    attr_names = ('name',)

class EnumeratorList(Node):
    def __init__(self, enumerators, coord=None):
        self.enumerators = enumerators
        self.coord = coord

    def children(self):
        nodelist = []
        for i, child in enumerate(self.enumerators or []):
            nodelist.append(("enumerators[%d]" % i, child))
        return tuple(nodelist)

    attr_names = ()

class ExprList(Node):
    def __init__(self, exprs, coord=None):
        self.exprs = exprs
        self.coord = coord

    def children(self):
        nodelist = []
        for i, child in enumerate(self.exprs or []):
            nodelist.append(("exprs[%d]" % i, child))
        return tuple(nodelist)

    attr_names = ()

class FileAST(Node):
    def __init__(self, ext, coord=None):
        self.ext = ext
        self.coord = coord

    def children(self):
        nodelist = []
        for i, child in enumerate(self.ext or []):
            nodelist.append(("ext[%d]" % i, child))
        return tuple(nodelist)

    attr_names = ()

class For(Node):
    def __init__(self, init, cond, next, stmt, coord=None):
        self.init = init
        self.cond = cond
        self.next = next
        self.stmt = stmt
        self.coord = coord

    def children(self):
        nodelist = []
        if self.init is not None: nodelist.append(("init", self.init))
        if self.cond is not None: nodelist.append(("cond", self.cond))
        if self.next is not None: nodelist.append(("next", self.next))
        if self.stmt is not None: nodelist.append(("stmt", self.stmt))
        return tuple(nodelist)

    attr_names = ()

class FuncCall(Node):
    def __init__(self, name, args, coord=None):
        self.name = name
        self.args = args
        self.coord = coord

    def children(self):
        nodelist = []
        if self.name is not None: nodelist.append(("name", self.name))
        if self.args is not None: nodelist.append(("args", self.args))
        return tuple(nodelist)

    attr_names = ()

class FuncDecl(Node):
    def __init__(self, args, type, coord=None):
        self.args = args
        self.type = type
        self.coord = coord

    def children(self):
        nodelist = []
        if self.args is not None: nodelist.append(("args", self.args))
        if self.type is not None: nodelist.append(("type", self.type))
        return tuple(nodelist)

    attr_names = ()

class FuncDef(Node):
    def __init__(self, decl, param_decls, body, coord=None):
        self.decl = decl
        self.param_decls = param_decls
        self.body = body
        self.coord = coord

    def children(self):
        nodelist = []
        if self.decl is not None: nodelist.append(("decl", self.decl))
        if self.body is not None: nodelist.append(("body", self.body))
        for i, child in enumerate(self.param_decls or []):
            nodelist.append(("param_decls[%d]" % i, child))
        return tuple(nodelist)

    attr_names = ()

class Goto(Node):
    def __init__(self, name, coord=None):
        self.name = name
        self.coord = coord

    def children(self):
        nodelist = []
        return tuple(nodelist)

    attr_names = ('name',)

class ID(Node):
    def __init__(self, name, coord=None):
        self.name = name
        self.coord = coord

    def children(self):
        nodelist = []
        return tuple(nodelist)

    attr_names = ('name',)

class IdentifierType(Node):
    def __init__(self, names, coord=None):
        self.names = names
        self.coord = coord

    def children(self):
        nodelist = []
        return tuple(nodelist)

    attr_names = ('names',)

class If(Node):
    def __init__(self, cond, iftrue, iffalse, coord=None):
        self.cond = cond
        self.iftrue = iftrue
        self.iffalse = iffalse
        self.coord = coord

    def children(self):
        nodelist = []
        if self.cond is not None: nodelist.append(("cond", self.cond))
        if self.iftrue is not None: nodelist.append(("iftrue", self.iftrue))
        if self.iffalse is not None: nodelist.append(("iffalse", self.iffalse))
        return tuple(nodelist)

    attr_names = ()

class InitList(Node):
    def __init__(self, exprs, coord=None):
        self.exprs = exprs
        self.coord = coord

    def children(self):
        nodelist = []
        for i, child in enumerate(self.exprs or []):
            nodelist.append(("exprs[%d]" % i, child))
        return tuple(nodelist)

    attr_names = ()

class Label(Node):
    def __init__(self, name, stmt, coord=None):
        self.name = name
        self.stmt = stmt
        self.coord = coord

    def children(self):
        nodelist = []
        if self.stmt is not None: nodelist.append(("stmt", self.stmt))
        return tuple(nodelist)

    attr_names = ('name',)

class NamedInitializer(Node):
    def __init__(self, name, expr, coord=None):
        self.name = name
        self.expr = expr
        self.coord = coord

    def children(self):
        nodelist = []
        if self.expr is not None: nodelist.append(("expr", self.expr))
        for i, child in enumerate(self.name or []):
            nodelist.append(("name[%d]" % i, child))
        return tuple(nodelist)

    attr_names = ()

class ParamList(Node):
    def __init__(self, params, coord=None):
        self.params = params
        self.coord = coord

    def children(self):
        nodelist = []
        for i, child in enumerate(self.params or []):
            nodelist.append(("params[%d]" % i, child))
        return tuple(nodelist)

    attr_names = ()

class PtrDecl(Node):
    def __init__(self, quals, type, coord=None):
        self.quals = quals
        self.type = type
        self.coord = coord

    def children(self):
        nodelist = []
        if self.type is not None: nodelist.append(("type", self.type))
        return tuple(nodelist)

    attr_names = ('quals',)

class Return(Node):
    def __init__(self, expr, coord=None):
        self.expr = expr
        self.coord = coord

    def children(self):
        nodelist = []
        if self.expr is not None: nodelist.append(("expr", self.expr))
        return tuple(nodelist)

    attr_names = ()

class Struct(Node):
    def __init__(self, name, decls, coord=None):
        self.name = name
        self.decls = decls
        self.coord = coord

    def children(self):
        nodelist = []
        for i, child in enumerate(self.decls or []):
            nodelist.append(("decls[%d]" % i, child))
        return tuple(nodelist)

    attr_names = ('name',)

class StructRef(Node):
    def __init__(self, name, type, field, coord=None):
        self.name = name
        self.type = type
        self.field = field
        self.coord = coord

    def children(self):
        nodelist = []
        if self.name is not None: nodelist.append(("name", self.name))
        if self.field is not None: nodelist.append(("field", self.field))
        return tuple(nodelist)

    attr_names = ('type',)

class Switch(Node):
    def __init__(self, cond, stmt, coord=None):
        self.cond = cond
        self.stmt = stmt
        self.coord = coord

    def children(self):
        nodelist = []
        if self.cond is not None: nodelist.append(("cond", self.cond))
        if self.stmt is not None: nodelist.append(("stmt", self.stmt))
        return tuple(nodelist)

    attr_names = ()

class TernaryOp(Node):
    def __init__(self, cond, iftrue, iffalse, coord=None):
        self.cond = cond
        self.iftrue = iftrue
        self.iffalse = iffalse
        self.coord = coord

    def children(self):
        nodelist = []
        if self.cond is not None: nodelist.append(("cond", self.cond))
        if self.iftrue is not None: nodelist.append(("iftrue", self.iftrue))
        if self.iffalse is not None: nodelist.append(("iffalse", self.iffalse))
        return tuple(nodelist)

    attr_names = ()

class TypeDecl(Node):
    def __init__(self, declname, quals, type, coord=None):
        self.declname = declname
        self.quals = quals
        self.type = type
        self.coord = coord

    def children(self):
        nodelist = []
        if self.type is not None: nodelist.append(("type", self.type))
        return tuple(nodelist)

    attr_names = ('declname', 'quals',)

class Typedef(Node):
    def __init__(self, name, quals, storage, type, coord=None):
        self.name = name
        self.quals = quals
        self.storage = storage
        self.type = type
        self.coord = coord

    def children(self):
        nodelist = []
        if self.type is not None: nodelist.append(("type", self.type))
        return tuple(nodelist)

    attr_names = ('name', 'quals', 'storage',)

class Typename(Node):
    def __init__(self, quals, type, coord=None):
        self.quals = quals
        self.type = type
        self.coord = coord

    def children(self):
        nodelist = []
        if self.type is not None: nodelist.append(("type", self.type))
        return tuple(nodelist)

    attr_names = ('quals',)

class UnaryOp(Node):
    def __init__(self, op, expr, coord=None):
        self.op = op
        self.expr = expr
        self.coord = coord

    def children(self):
        nodelist = []
        if self.expr is not None: nodelist.append(("expr", self.expr))
        return tuple(nodelist)

    attr_names = ('op',)

class Union(Node):
    def __init__(self, name, decls, coord=None):
        self.name = name
        self.decls = decls
        self.coord = coord

    def children(self):
        nodelist = []
        for i, child in enumerate(self.decls or []):
            nodelist.append(("decls[%d]" % i, child))
        return tuple(nodelist)

    attr_names = ('name',)

class While(Node):
    def __init__(self, cond, stmt, coord=None):
        self.cond = cond
        self.stmt = stmt
        self.coord = coord

    def children(self):
        nodelist = []
        if self.cond is not None: nodelist.append(("cond", self.cond))
        if self.stmt is not None: nodelist.append(("stmt", self.stmt))
        return tuple(nodelist)

    attr_names = ()

