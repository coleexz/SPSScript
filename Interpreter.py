from Lexer import *
from Parser import *
from Errors import *
from Context import *
from Tokens import *
from RTResult import *
from Values import *

#######################################
# INTERPRETER
#######################################

class Interpreter:
  def visit(self, node, context):
    method_name = f'visit_{type(node).__name__}'
    method = getattr(self, method_name, self.no_visit_method)
    return method(node, context)

  def no_visit_method(self, node, context):
    raise Exception(f'No visit_{type(node).__name__} method defined')

  ###################################

  def visit_NumberNode(self, node, context):
    return RTResult().success(
      Number(node.tok.value).set_context(context).set_pos(node.pos_start, node.pos_end)
    )

  def visit_StringNode(self, node, context):
    return RTResult().success(
      String(node.tok.value).set_context(context).set_pos(node.pos_start, node.pos_end)
    )

  def visit_ListNode(self, node, context):
    res = RTResult()
    elements = []

    for element_node in node.element_nodes:
      elements.append(res.register(self.visit(element_node, context)))
      if res.should_return(): return res

    return res.success(
      List(elements).set_context(context).set_pos(node.pos_start, node.pos_end)
    )

  def visit_VarAccessNode(self, node, context):
    res = RTResult()
    var_name = node.var_name_tok.value
    value = context.symbol_table.get(var_name)

    if not value:
      return res.failure(RTError(
        node.pos_start, node.pos_end,
        f"'{var_name}' is not defined",
        context
      ))

    value = value.copy().set_pos(node.pos_start, node.pos_end).set_context(context)
    return res.success(value)

  def visit_VarAssignNode(self, node, context):
    res = RTResult()
    var_name = node.var_name_tok.value
    value = res.register(self.visit(node.value_node, context))
    if res.should_return(): return res

    context.symbol_table.set(var_name, value)
    return res.success(value)

  def visit_BinOpNode(self, node, context):
    res = RTResult()
    left = res.register(self.visit(node.left_node, context))
    if res.should_return(): return res
    right = res.register(self.visit(node.right_node, context))
    if res.should_return(): return res

    if node.op_tok.type == TT_PLUS:
      result, error = left.added_to(right)
    elif node.op_tok.type == TT_MINUS:
      result, error = left.subbed_by(right)
    elif node.op_tok.type == TT_MUL:
      result, error = left.multed_by(right)
    elif node.op_tok.type == TT_DIV:
      result, error = left.dived_by(right)
    elif node.op_tok.type == TT_POW:
      result, error = left.powed_by(right)
    elif node.op_tok.type == TT_EE:
      result, error = left.get_comparison_eq(right)
    elif node.op_tok.type == TT_NE:
      result, error = left.get_comparison_ne(right)
    elif node.op_tok.type == TT_LT:
      result, error = left.get_comparison_lt(right)
    elif node.op_tok.type == TT_GT:
      result, error = left.get_comparison_gt(right)
    elif node.op_tok.type == TT_LTE:
      result, error = left.get_comparison_lte(right)
    elif node.op_tok.type == TT_GTE:
      result, error = left.get_comparison_gte(right)
    elif node.op_tok.matches(TT_KEYWORD, 'y'):
      result, error = Boolean(left.is_true() and right.is_true()).set_context(context), None
    elif node.op_tok.matches(TT_KEYWORD, 'o'):
      result, error = Boolean(left.is_true() or right.is_true()).set_context(context), None

    if error:
      return res.failure(error)
    else:
      return res.success(result.set_pos(node.pos_start, node.pos_end))

  def visit_UnaryOpNode(self, node, context):
    res = RTResult()
    number = res.register(self.visit(node.node, context))
    if res.should_return(): return res

    error = None

    if node.op_tok.type == TT_MINUS:
      number, error = number.multed_by(Number(-1))
    elif node.op_tok.matches(TT_KEYWORD, 'NadaQueVer'):
      number, error = number.notted()

    if error:
      return res.failure(error)
    else:
      return res.success(number.set_pos(node.pos_start, node.pos_end))

  def visit_IfNode(self, node, context):
    res = RTResult()

    for condition, expr, should_return_null in node.cases:
      condition_value = res.register(self.visit(condition, context))
      if res.should_return(): return res

      if condition_value.is_true():
        expr_value = res.register(self.visit(expr, context))
        if res.should_return(): return res
        return res.success(Boolean.null if should_return_null else expr_value)

    if node.else_case:
      expr, should_return_null = node.else_case
      expr_value = res.register(self.visit(expr, context))
      if res.should_return(): return res
      return res.success(Boolean.null if should_return_null else expr_value)

    return res.success(Boolean.null)

  def visit_ForNode(self, node, context):
    res = RTResult()
    elements = []

    start_value = res.register(self.visit(node.start_value_node, context))
    if res.should_return(): return res

    end_value = res.register(self.visit(node.end_value_node, context))
    if res.should_return(): return res

    if node.step_value_node:
      step_value = res.register(self.visit(node.step_value_node, context))
      if res.should_return(): return res
    else:
      step_value = Number(1)

    i = start_value.value

    if step_value.value >= 0:
      condition = lambda: i < end_value.value
    else:
      condition = lambda: i > end_value.value

    while condition():
      context.symbol_table.set(node.var_name_tok.value, Number(i))
      i += step_value.value

      value = res.register(self.visit(node.body_node, context))
      if res.should_return() and res.loop_should_continue == False and res.loop_should_break == False: return res

      if res.loop_should_continue:
        continue

      if res.loop_should_break:
        break

      elements.append(value)

    return res.success(
      Boolean.null if node.should_return_null else
      List(elements).set_context(context).set_pos(node.pos_start, node.pos_end)
    )

  def visit_WhileNode(self, node, context):
    res = RTResult()
    elements = []

    while True:
      condition = res.register(self.visit(node.condition_node, context))
      if res.should_return(): return res

      if not condition.is_true():
        break

      value = res.register(self.visit(node.body_node, context))
      if res.should_return() and res.loop_should_continue == False and res.loop_should_break == False: return res

      if res.loop_should_continue:
        continue

      if res.loop_should_break:
        break

      elements.append(value)

    return res.success(
      Boolean.null if node.should_return_null else
      List(elements).set_context(context).set_pos(node.pos_start, node.pos_end)
    )

  def visit_FuncDefNode(self, node, context):
    res = RTResult()

    func_name = node.var_name_tok.value if node.var_name_tok else None
    body_node = node.body_node
    arg_names = [arg_name.value for arg_name in node.arg_name_toks]
    func_value = Function(func_name, body_node, arg_names, node.should_auto_return).set_context(context).set_pos(node.pos_start, node.pos_end)

    if node.var_name_tok:
      context.symbol_table.set(func_name, func_value)

    return res.success(func_value)

  def visit_CallNode(self, node, context):
    res = RTResult()
    args = []

    value_to_call = res.register(self.visit(node.node_to_call, context))
    if res.should_return(): return res
    value_to_call = value_to_call.copy().set_pos(node.pos_start, node.pos_end)

    for arg_node in node.arg_nodes:
      args.append(res.register(self.visit(arg_node, context)))
      if res.should_return(): return res

    return_value = res.register(value_to_call.execute(args))
    if res.should_return(): return res
    return_value = return_value.copy().set_pos(node.pos_start, node.pos_end).set_context(context)
    return res.success(return_value)

  def visit_ReturnNode(self, node, context):
    res = RTResult()

    if node.node_to_return:
      value = res.register(self.visit(node.node_to_return, context))
      if res.should_return(): return res
    else:
      value = Boolean.null

    return res.success_return(value)

  def visit_ContinueNode(self, node, context):
    return RTResult().success_continue()

  def visit_BreakNode(self, node, context):
    return RTResult().success_break()

  def visit_PrintNode(self, node, context):
        res = RTResult()

        # Evaluate all expressions in the PrintNode
        values = []
        for expr in node.exprs:
            value = res.register(self.visit(expr, context))
            if res.should_return(): return res
            values.append(value)

        # Print the concatenated string representations of all evaluated values
        print(" ".join(map(str, values)))

        return res.success(Boolean.null)
  
  def visit_ClassDefNode(self, node, context):
    res = RTResult()
    methods = {}

    # Iterar sobre los elementos del cuerpo de la clase
    if isinstance(node.body_node, ListNode):
        for statement in node.body_node.element_nodes:
            if isinstance(statement, FuncDefNode):
                # Reutilizar visit_FuncDefNode para crear la función
                func_res = self.visit_FuncDefNode(statement, context)
                if func_res.error: return func_res

                func_name = statement.var_name_tok.value
                methods[func_name] = func_res.value  # Registrar el método
                print(f"[DEBUG] Método registrado: {func_name}")

    # Crear el objeto de la clase con los métodos
    class_object = Object(node.class_name_tok.value, methods)
    context.symbol_table.set(node.class_name_tok.value, class_object)
    print(f"[DEBUG] Clase registrada: {node.class_name_tok.value}")
    return res.success(None)





  def visit_ClassInstantiationNode(self, node, context):
    class_def = context.symbol_table.get(node.class_name_tok.value)
    if not class_def:
        return RTResult().failure(RTError(
            node.pos_start, node.pos_end,
            f"La clase '{node.class_name_tok.value}' no está definida",
            context
        ))

    # Crear una instancia con los métodos de la clase
    instance = Object(node.class_name_tok.value, class_def.attributes.copy())
    return RTResult().success(instance)



  def visit_MethodCallNode(self, node, context):
    # Obtener el objeto desde la tabla de símbolos
    obj = context.symbol_table.get(node.object_name_tok.value)
    print(f"[DEBUG] Obj: {obj}")
    if not isinstance(obj, Object):
        return RTResult().failure(RTError(
            node.pos_start, node.pos_end,
            f"'{node.object_name_tok.value}' no es un objeto válido",
            context
        ))

    # Obtener el método del objeto
    method = obj.attributes.get(node.method_name_tok.value)
    print(f"[DEBUG] method: {method}")
    if not method or not isinstance(method, Function):
        print(f"Entro al coso este")
        return RTResult().failure(RTError(
            node.pos_start, node.pos_end,
            f"'{node.method_name_tok.value}' no es un método válido o no existe",
            context
        ))

    # Evaluar los argumentos del método
    print(f"Paso el if")
    res = RTResult()
    args = []
    for arg_node in node.args:
        arg = res.register(self.visit(arg_node, context))
        if res.should_return(): return res
        args.append(arg)

    # Ejecutar el método con los argumentos
    return_value = res.register(method.execute(args))
    print(f"[DEBUG] Return value: {return_value}")

    if res.should_return():
      print(f"Paso el if2 {res}")
      return res

    return res.success(return_value)
