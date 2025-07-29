# This file is part of the mlhp project. License: See LICENSE

import os, sys, ast
from functools import reduce

try:
    # mlhp.py script folder
    path = os.path.abspath( os.path.dirname(sys.argv[0]) );
    
    # Try to open path/mlhpPythonPath containing the python module path. This
    # file is written as post build command after compiling pymlhpcore.
    with open( os.path.join( path, 'mlhpPythonPath' ), 'r') as f:
        sys.path.append( os.path.normpath( f.read( ).splitlines( )[0] ) )
   
except IOError: 
    pass

from pymlhpcore import *
from pymlhpcore import _scalarFieldFromTree, _vectorFieldFromTree, _vectorFieldFromAddress, _scalarFieldFromAddress, _domainIntegrandFromAddress

Triangulation = Triangulation3D
TriangleCellAssociation = TriangleCellAssociation3D

def _iterativeSolve(internalSolve, A, b, x0, *, rtol, atol, maxiter, M, residualNorms):
    maxiter_ = len(b) if maxiter is None else maxiter
    
    mA = linearOperator(A) if isinstance(A, AbsSparseMatrix) else A
    mM = noPreconditioner() if M is None else (linearOperator(M) if isinstance(M, AbsSparseMatrix) else M)
    
    solution = DoubleVector(len(b), 0.0) if x0 is None else copy(vector=x0)
    norms = internalSolve(mA, b, x0=solution, rtol=rtol, atol=atol, maxiter=maxiter_, M=mM);
    
    return [solution, norms] if residualNorms else solution
    
def cg(A, b, x0=None, *, rtol=1e-10, atol=0.0, maxiter=None, M=None, residualNorms=False):
    return _iterativeSolve(internalCG, A, b, x0, rtol=rtol, atol=atol, maxiter=maxiter, M=M, residualNorms=residualNorms)

def bicgstab(A, b, x0=None, *, rtol=1e-10, atol=0.0, maxiter=None, M=None, residualNorms=False):
    return _iterativeSolve(internalBiCGStab, A, b, x0, rtol=rtol, atol=atol, maxiter=maxiter, M=M, residualNorms=residualNorms)

def _makeSolve(solver, *,rtol, atol, maxiter):
    def solve(A, b):
        return solver(A, b, rtol=solve.rtol, atol=solve.atol, maxiter=solve.maxiter, M=diagonalPreconditioner(A))
    solve.rtol = rtol
    solve.atol = atol
    solve.maxiter = maxiter
    return solve
    
def makeCGSolver(*, rtol=1e-10, atol=0.0, maxiter=None):
    return _makeSolve(cg, rtol=rtol, atol=atol, maxiter=maxiter)

def makeBiCGStabSolver(*, rtol=1e-10, atol=0.0, maxiter=None):
    return _makeSolve(bicgstab, rtol=rtol, atol=atol, maxiter=maxiter)

def makeScalars(n, value=0.0):
    return [ScalarDouble( value ) for _ in range( n )]
    
def writeBasisOutput(basis, postmesh=None, writer=VtuOutput("output.vtu"), processors=[]):
    kwargs = {'basis': basis, 'writer' : writer if isinstance(writer, MeshWriter) else writer.meshWriter()}
    
    if postmesh is not None:
        kwargs['postmesh'] = postmesh
    if len(processors) > 0:
        convert = lambda p : type(p).__name__[:-2] != 'ElementProcessor'
        kwargs['processors'] = [(convertToElementProcessor(p) if convert(p) else p) for p in processors]
            
    internalWriteBasisOutput(**kwargs)
 
def writeMeshOutput(mesh, postmesh=None, writer=VtuOutput("output.vtu"), processors=[]):
    kwargs = {'mesh': mesh, 'writer' : writer if isinstance(writer, MeshWriter) else writer.meshWriter()}
    
    if postmesh is not None:
        kwargs['postmesh'] = postmesh
    if len(processors) > 0:
        kwargs['processors'] = processors
            
    internalWriteMeshOutput(**kwargs)
 
def _parseFunction(tree):
    tokens = []
    
    def _convert(node):
        id = _convert.index
        _convert.index += 1
        if isinstance(node, ast.AST):
            nodeType = node.__class__.__name__
            if nodeType == "Constant":
                tokens.append([id, nodeType, str(node.value)])
            elif nodeType == "BinOp":
                tokens.append([id, nodeType, node.op.__class__.__name__, _convert(node.left), _convert(node.right)])
            elif nodeType == "BoolOp" and len(node.values) == 2:
                tokens.append([id, nodeType, node.op.__class__.__name__, _convert(node.values[0]), _convert(node.values[1])])
            elif nodeType == "Compare" and len(node.comparators) == 1:
                tokens.append([id, nodeType, node.ops[0].__class__.__name__, _convert(node.left), _convert(node.comparators[0])])
            elif nodeType == "Call":
                tokens.append([id, nodeType, node.func.id] + [_convert(arg) for arg in node.args])
            elif nodeType == "Name" and node.id in {'x', 'y', 'z', 'r', 's', 't'}:
                tokens.append([id, "Input", str( { 'x' : 0, 'y' : 1, 'z' : 2, 'r' : 0, 's' : 1, 't' : 2 }[node.id] ) ])
            elif nodeType == "Subscript" and isinstance(node.slice, ast.Constant):
                tokens.append([id, "Input", str(node.slice.value)])
            elif nodeType == "UnaryOp":
                tokens.append([id, nodeType, node.op.__class__.__name__, _convert(node.operand)])
            elif nodeType == "IfExp":
                tokens.append([id, "Call", "select", _convert(node.test), _convert(node.body), _convert(node.orelse)])
            elif nodeType == "Num": # Legacy python 3.7
                tokens.append([id, "Constant", str(node.n)])
            elif nodeType == "Subscript" and node.slice.__class__.__name__ == "Index": # Legacy python 3.7
                tokens.append([id, "Input", str(node.slice.value.n)])
            else:
                raise(ValueError("Expression of type \"" + nodeType + "\" is not supported."))
        return str(id)
        
    _convert.index = 0
    _convert(tree)
    
    return [token[1:] for token in sorted(tokens, key=lambda token : token[0])]
    
def _parseScalarField(expr):
    if not isinstance(expr, str): raise ValueError("Expression must be a string")
    
    tree = ast.parse(expr).body
    
    if len(tree) != 1: raise ValueError("Expression string must contain one expression.")
    
    return _parseFunction(tree[0].value)
     
def _parseVectorField(expr):
    if not isinstance(expr, str): raise ValueError("Expression must be a string")
    
    expressionList = ast.parse(expr).body[0].value
    
    if not isinstance(expressionList, ast.List): 
        raise ValueError("Root expression is not a list.")
    
    return [_parseFunction(expr) for expr in expressionList.elts]
    
def scalarField(ndim, func=None, address=None):
    if address is not None:
        if func is not None: raise ValueError("Both function and address given.")
        return _scalarFieldFromAddress(ndim, address)
    if hasattr(func, "address"):
        return _scalarFieldFromAddress(ndim, func.address)
    if isinstance(func, (bool, int, float)):
        return _scalarFieldFromTree(ndim, _parseScalarField(str(float(func))))
    if isinstance(func, str):
        return _scalarFieldFromTree(ndim, _parseScalarField(func))
    raise ValueError("Invalid function input parameter.")
 
def vectorField(idim, func=None, odim=None, address=None):
    if (func is None) == (address is None): raise ValueError("Must specify either func or address.")
    
    if address is not None:
        if odim is None: raise ValueError("Passing address requires also specifying odim.")
        return _vectorFieldFromAddress(idim, odim, address)
    if hasattr(func, "address"):
        if odim is None: raise ValueError("Passing address requires also specifying odim.")
        return _vectorFieldFromAddress(idim, odim, func.address)
    if isinstance(func, (list, tuple)) and reduce(lambda a, b: a and b, [isinstance(v, (bool, int, float)) for v in func]):
        return _vectorFieldFromTree(idim, _parseVectorField(str([float(f) for f in func])))
    if isinstance(func, str):
        return _vectorFieldFromTree(idim, _parseVectorField(func))
    raise ValueError("Invalid function input parameter.")
  
def implicitFunction(ndim, func=None, address=None):
    return implicitThreshold(scalarField(ndim, func, address), 0.5)
 
def domainIntegrand(ndim, callback, types, maxdiff, tmpdofs=0):
    return _domainIntegrandFromAddress(ndim, callback.address, types, maxdiff, tmpdofs) 
    
#del os, sys, path
