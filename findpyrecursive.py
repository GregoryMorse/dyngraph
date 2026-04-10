#https://hg.python.org/cpython/file/tip/Tools/parser/unparse.py
#designed to handle basic function recursion, static class function, and instance class function recursion
#will not handle dynamic code scenarios or perhaps other non-standard variants
#does not handle corecursion unless from nested function, it could be solved by building a call graph
#CWE-674: Uncontrolled Recursion https://cwe.mitre.org/data/definitions/674.html
def dispatch(fname, tree, classname=None):
  import ast
  for t in ast.walk(tree):
    if isinstance(t, ast.ClassDef):
      for b in t.body: dispatch(fname, b, t.name)
    elif isinstance(t, (ast.FunctionDef, ast.AsyncFunctionDef)):
      for item in ast.walk(t):
        if isinstance(item, ast.Call):
          if isinstance(item.func, ast.Name):
            if item.func.id == t.name:
              print("Recursion detected: " + fname + " " + t.name)
              break
          elif isinstance(item.func, ast.Attribute) and not classname is None:
            if isinstance(item.func.value, ast.Name):
              if item.func.value.id == classname:
                if item.func.attr == t.name:
                  print("Class Static Recursion detected: " + fname + " " + classname + " " + item.func.attr)
                  break
              elif item.func.value.id == "self":
                if item.func.attr == t.name:
                  print("Class Recursion detected: " + fname + " " + classname + " " + item.func.attr)
                  break
def check_file(filename):
  #import parser
  import tokenize
  import ast
  with open(filename, "rb") as pyfile:
    encoding = tokenize.detect_encoding(pyfile.readline)[0]
  with open(filename, "r", encoding=encoding) as pyfile:
    source = pyfile.read()
  tree = compile(source, filename, "exec", ast.PyCF_ONLY_AST)
  dispatch(filename, tree)

def enum_py_dir(dirname):
  import glob
  import os
  return glob.glob(os.path.join(dirname, "*.py"))
for fname in enum_py_dir("."): check_file(fname)