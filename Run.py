from Lexer import *
from Parser import *
from Interpreter import *
from Context import *
from Tokens import *
#######################################
# RUN
#######################################

global_symbol_table = SymbolTable()
global_symbol_table.set("Nada", Boolean.null)
global_symbol_table.set("Casaca", Boolean.false)
global_symbol_table.set("Real", Boolean.true)
global_symbol_table.set("MATH_PI", Number.math_PI)
global_symbol_table.set("Ejenie", BuiltInFunction.print)
global_symbol_table.set("PRINT_RET", BuiltInFunction.print_ret)
global_symbol_table.set("Sampale", BuiltInFunction.input)
global_symbol_table.set("INPUT_INT", BuiltInFunction.input_int)
global_symbol_table.set("CLEAR", BuiltInFunction.clear)
global_symbol_table.set("CLS", BuiltInFunction.clear)
global_symbol_table.set("EsEntero", BuiltInFunction.is_number)
global_symbol_table.set("EsChambre", BuiltInFunction.is_string)
global_symbol_table.set("EsFilaIndia", BuiltInFunction.is_list)
global_symbol_table.set("EsParo", BuiltInFunction.is_function)
global_symbol_table.set("Metele", BuiltInFunction.append)
global_symbol_table.set("Saca", BuiltInFunction.pop)
global_symbol_table.set("EXTEND", BuiltInFunction.extend)
global_symbol_table.set("Mide", BuiltInFunction.len)
global_symbol_table.set("RUN", BuiltInFunction.run)
global_symbol_table.set("__input__", String(""))


def run(fn, text):
  lexer = Lexer(fn, text)
  tokens, error = lexer.make_tokens()
  if error: return None, error

  parser = Parser(tokens)
  ast = parser.parse()
  if ast.error: return None, ast.error

  interpreter = Interpreter()
  context = Context('<program>')
  context.symbol_table = global_symbol_table
  result = interpreter.visit(ast.node, context)

  if result.error:
    return None, result.error
  else:
    return None, None
