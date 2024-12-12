from Tokens import *
from Position import *
from Errors import *
from Nodes import *


#######################################
# PARSE RESULT
#######################################

class ParseResult:
  def __init__(self):
    self.error = None
    self.node = None
    self.last_registered_advance_count = 0
    self.advance_count = 0
    self.to_reverse_count = 0

  def register_advancement(self):
    self.last_registered_advance_count = 1
    self.advance_count += 1

  def register(self, res):
    self.last_registered_advance_count = res.advance_count
    self.advance_count += res.advance_count
    if res.error: self.error = res.error
    return res.node

  def try_register(self, res):
    if res.error:
      self.to_reverse_count = res.advance_count
      return None
    return self.register(res)

  def success(self, node):
    self.node = node
    return self

  def failure(self, error):
    if not self.error or self.last_registered_advance_count == 0:
      self.error = error
    return self

#######################################
# PARSER
#######################################

class Parser:
  def __init__(self, tokens):
    self.tokens = tokens
    self.tok_idx = -1
    self.advance()

  def advance(self):
    self.tok_idx += 1
    self.update_current_tok()
    return self.current_tok

  def reverse(self, amount=1):
    self.tok_idx -= amount
    self.update_current_tok()
    return self.current_tok

  def update_current_tok(self):
    if self.tok_idx >= 0 and self.tok_idx < len(self.tokens):
      self.current_tok = self.tokens[self.tok_idx]

  def parse(self):
    res = self.statements()
    if not res.error and self.current_tok.type != TT_EOF:
      return res.failure(InvalidSyntaxError(
        self.current_tok.pos_start, self.current_tok.pos_end,
        "Token cannot appear after previous tokens"
      ))
    return res

  ###################################

  def statements(self):
    res = ParseResult()
    statements = []
    pos_start = self.current_tok.pos_start.copy()

    while self.current_tok.type == TT_NEWLINE:
      res.register_advancement()
      self.advance()

    statement = res.register(self.statement())
    if res.error: return res
    statements.append(statement)

    more_statements = True

    while True:
      newline_count = 0
      while self.current_tok.type == TT_NEWLINE:
        res.register_advancement()
        self.advance()
        newline_count += 1
      if newline_count == 0:
        more_statements = False

      if not more_statements: break
      statement = res.try_register(self.statement())
      if not statement:
        self.reverse(res.to_reverse_count)
        more_statements = False
        continue
      statements.append(statement)

    return res.success(ListNode(
      statements,
      pos_start,
      self.current_tok.pos_end.copy()
    ))

  def statement(self):
    res = ParseResult()
    pos_start = self.current_tok.pos_start.copy()

    if self.current_tok.matches(TT_KEYWORD, 'RETURN'):
      res.register_advancement()
      self.advance()

      expr = res.try_register(self.expr())
      if not expr:
        self.reverse(res.to_reverse_count)
      return res.success(ReturnNode(expr, pos_start, self.current_tok.pos_start.copy()))

    if self.current_tok.matches(TT_KEYWORD, 'SigaMiPerro'):
      res.register_advancement()
      self.advance()
      return res.success(ContinueNode(pos_start, self.current_tok.pos_start.copy()))

    if self.current_tok.matches(TT_KEYWORD, 'CortalaMiPerro'):
      res.register_advancement()
      self.advance()
      return res.success(BreakNode(pos_start, self.current_tok.pos_start.copy()))

    if self.current_tok.matches(TT_IDENTIFIER, 'Ejenie'):
        res.register_advancement()
        self.advance()

        if self.current_tok.type == TT_LPAREN:
            res.register_advancement()
            self.advance()
            args = []

            if self.current_tok.type != TT_RPAREN:
                args.append(res.register(self.expr()))
                if res.error: return res

                while self.current_tok.type == TT_COMMA:
                    res.register_advancement()
                    self.advance()
                    args.append(res.register(self.expr()))
                    if res.error: return res

                if self.current_tok.type != TT_RPAREN:
                    return res.failure(InvalidSyntaxError(
                        self.current_tok.pos_start, self.current_tok.pos_end,
                        "Expected ',' or ')'"
                    ))

            res.register_advancement()
            self.advance()
            # Pasar los argumentos como una lista
            return res.success(PrintNode(args, pos_start, self.current_tok.pos_end.copy()))


    expr = res.register(self.expr())
    if res.error:
      return res.failure(InvalidSyntaxError(
        self.current_tok.pos_start, self.current_tok.pos_end,
        "Se esperaba un 'RETURN', 'SigaMiPerro', 'CortalaMiPerro', 'PoneleQue', 'PoneteAPensar', 'PasarLista', 'AhoritaQue', 'HacemeElParo', int, float, identifier, '+', '-', '(', '[' or 'NadaQueVer'"
      ))
    return res.success(expr)

  def expr(self):
    res = ParseResult()

    # Manejar 'PoneleQue'
    if self.current_tok.matches(TT_KEYWORD, 'PoneleQue'):
        res.register_advancement()
        self.advance()

        if self.current_tok.type != TT_IDENTIFIER:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Se esperaba un identificador después de 'PoneleQue'"
            ))

        var_name = self.current_tok
        res.register_advancement()
        self.advance()

        # Verificar si es '=' para una asignación
        if self.current_tok.type == TT_EQ:
            res.register_advancement()
            self.advance()

            # Verificar si es una instancia de clase con 'Nuevo'
            if self.current_tok.matches(TT_KEYWORD, 'Nuevo'):
                res.register_advancement()
                self.advance()

                # Verificar el nombre de la clase
                if self.current_tok.type != TT_IDENTIFIER:
                    return res.failure(InvalidSyntaxError(
                        self.current_tok.pos_start, self.current_tok.pos_end,
                        "Se esperaba un identificador para el nombre de la clase"
                    ))

                class_name = self.current_tok
                res.register_advancement()
                self.advance()

                # Verificar paréntesis vacíos '()'
                if self.current_tok.type != TT_LPAREN:
                    return res.failure(InvalidSyntaxError(
                        self.current_tok.pos_start, self.current_tok.pos_end,
                        "Se esperaba '(' después del nombre de la clase"
                    ))

                res.register_advancement()
                self.advance()

                if self.current_tok.type != TT_RPAREN:
                    return res.failure(InvalidSyntaxError(
                        self.current_tok.pos_start, self.current_tok.pos_end,
                        "Se esperaba ')' después de '('"
                    ))

                res.register_advancement()
                self.advance()

                # Crear nodo para la instanciación de clase
                return res.success(VarAssignNode(var_name, ClassInstantiationNode(class_name)))

            # Si no es 'Nuevo', manejar como una asignación normal
            expr = res.register(self.expr())
            if res.error: return res
            return res.success(VarAssignNode(var_name, expr))

        return res.failure(InvalidSyntaxError(
            self.current_tok.pos_start, self.current_tok.pos_end,
            "Se esperaba '=' después del identificador"
        ))

    # Manejo de otras expresiones
    node = res.register(self.bin_op(self.comp_expr, ((TT_KEYWORD, 'y'), (TT_KEYWORD, 'o'))))

    if res.error:
        return res.failure(InvalidSyntaxError(
            self.current_tok.pos_start, self.current_tok.pos_end,
            "Se esperaba un 'PoneleQue', 'PoneteAPensar', 'PasarLista', 'AhoritaQue', 'HacemeElParo', int, float, identifier, '+', '-', '(', '[' o 'NadaQueVer'"
        ))

    return res.success(node)


  def comp_expr(self):
    res = ParseResult()

    if self.current_tok.matches(TT_KEYWORD, 'NadaQueVer'):
        op_tok = self.current_tok
        res.register_advancement()
        self.advance()

        node = res.try_register(self.comp_expr())
        if not node:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Se esperaba algo despues de 'NadaQueVer'"
            ))
        return res.success(UnaryOpNode(op_tok, node))

    node = res.try_register(self.bin_op(
        self.arith_expr,
        (TT_EE, TT_NE, TT_LT, TT_GT, TT_LTE, TT_GTE, (TT_KEYWORD, 'NadaQueVer'))
    ))
    if not node:
        return res.failure(InvalidSyntaxError(
            self.current_tok.pos_start, self.current_tok.pos_end,
            "Se esperaba un int, float, identifier, '+', '-', '(', '[', 'PoneteAPensar', 'PasarLista', 'AhoritaQue', 'HacemeElParo' or 'NadaQueVer'"
        ))

    return res.success(node)

  def arith_expr(self):
    return self.bin_op(self.term, (TT_PLUS, TT_MINUS))

  def term(self):
    return self.bin_op(self.factor, (TT_MUL, TT_DIV))

  def factor(self):
    res = ParseResult()
    tok = self.current_tok

    if tok.type in (TT_PLUS, TT_MINUS):
      res.register_advancement()
      self.advance()
      factor = res.register(self.factor())
      if res.error: return res
      return res.success(UnaryOpNode(tok, factor))

    return self.power()

  def power(self):
    return self.bin_op(self.call, (TT_POW, ), self.factor)

  def call(self):
    res = ParseResult()
    atom = res.register(self.atom())
    if res.error: return res

    if self.current_tok.type == TT_LPAREN:  # Function call detected
        res.register_advancement()
        self.advance()
        arg_nodes = []

        if self.current_tok.type != TT_RPAREN:  # If arguments are present
            arg_nodes.append(res.register(self.expr()))
            if res.error:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "Expected ')', expression, or ','"
                ))

            while self.current_tok.type == TT_COMMA:
                res.register_advancement()
                self.advance()
                arg_nodes.append(res.register(self.expr()))
                if res.error: return res

            if self.current_tok.type != TT_RPAREN:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "Expected ',' or ')'"
                ))

        res.register_advancement()
        self.advance()
        return res.success(CallNode(atom, arg_nodes))  # Return a CallNode with arguments

    return res.success(atom)

  def atom(self):
    res = ParseResult()
    tok = self.current_tok

    if tok.type in (TT_INT, TT_FLOAT):
        res.register_advancement()
        self.advance()
        return res.success(NumberNode(tok))

    elif tok.type == TT_STRING:
        res.register_advancement()
        self.advance()
        return res.success(StringNode(tok))

    elif tok.type == TT_IDENTIFIER:
        res.register_advancement()
        self.advance()

        # Comprobar si es una llamada a método: obj.metodo()
        if self.current_tok.type == TT_DOT:
            res.register_advancement()
            self.advance()

            if self.current_tok.type != TT_IDENTIFIER:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "Se esperaba el nombre del método después de '.'"
                ))

            method_name_tok = self.current_tok
            res.register_advancement()
            self.advance()

            if self.current_tok.type != TT_LPAREN:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "Se esperaba '(' después del nombre del método"
                ))

            res.register_advancement()
            self.advance()

            # Obtener los argumentos del método
            arg_nodes = []
            if self.current_tok.type != TT_RPAREN:
                arg_nodes.append(res.register(self.expr()))
                if res.error: return res

                while self.current_tok.type == TT_COMMA:
                    res.register_advancement()
                    self.advance()
                    arg_nodes.append(res.register(self.expr()))
                    if res.error: return res

                if self.current_tok.type != TT_RPAREN:
                    return res.failure(InvalidSyntaxError(
                        self.current_tok.pos_start, self.current_tok.pos_end,
                        "Se esperaba ',' o ')'"
                    ))

            res.register_advancement()
            self.advance()
            return res.success(MethodCallNode(tok, method_name_tok, arg_nodes))

        # Si no es una llamada a método, es una variable normal
        return res.success(VarAccessNode(tok))

    elif tok.type == TT_LPAREN:
        res.register_advancement()
        self.advance()
        expr = res.register(self.expr())
        if res.error: return res
        if self.current_tok.type == TT_RPAREN:
            res.register_advancement()
            self.advance()
            return res.success(expr)
        else:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Se esperaba ')'"
            ))

    elif tok.type == TT_LSQUARE:
        list_expr = res.register(self.list_expr())
        if res.error: return res
        return res.success(list_expr)

    elif tok.matches(TT_KEYWORD, 'Clase'):
        # Manejo de definición de clases
        class_def = res.register(self.class_def())
        if res.error: return res
        return res.success(class_def)
    
    elif tok.matches(TT_KEYWORD, 'Propio'):
      res.register_advancement()
      self.advance()

      if self.current_tok.type == TT_DOT:
          res.register_advancement()
          self.advance()

          if self.current_tok.type != TT_IDENTIFIER:
              return res.failure(InvalidSyntaxError(
                  self.current_tok.pos_start, self.current_tok.pos_end,
                  "Se esperaba un identificador después de 'Propio.'"
              ))

          attribute_name_tok = self.current_tok
          res.register_advancement()
          self.advance()

          # Crear un nodo de acceso a atributos
          return res.success(AttributeAccessNode(tok, attribute_name_tok))



    elif tok.matches(TT_KEYWORD, 'PoneteAPensar'):
        if_expr = res.register(self.if_expr())
        if res.error: return res
        return res.success(if_expr)

    elif tok.matches(TT_KEYWORD, 'PasarLista'):
        for_expr = res.register(self.for_expr())
        if res.error: return res
        return res.success(for_expr)

    elif tok.matches(TT_KEYWORD, 'AhoritaQue'):
        while_expr = res.register(self.while_expr())
        if res.error: return res
        return res.success(while_expr)

    elif tok.matches(TT_KEYWORD, 'HacemeElParo'):
        func_def = res.register(self.func_def())
        if res.error: return res
        return res.success(func_def)

    return res.failure(InvalidSyntaxError(
        tok.pos_start, tok.pos_end,
        "Se esperaba un int, float, string, identifier, 'Clase', '+', '-', '(', '[', 'PoneteAPensar', 'PasarLista', 'AhoritaQue', 'HacemeElParo'"
    ))


  def list_expr(self):
    res = ParseResult()
    element_nodes = []
    pos_start = self.current_tok.pos_start.copy()

    if self.current_tok.type != TT_LSQUARE:
      return res.failure(InvalidSyntaxError(
        self.current_tok.pos_start, self.current_tok.pos_end,
        f"Expected '['"
      ))

    res.register_advancement()
    self.advance()

    if self.current_tok.type == TT_RSQUARE:
      res.register_advancement()
      self.advance()
    else:
      element_nodes.append(res.register(self.expr()))
      if res.error:
        return res.failure(InvalidSyntaxError(
          self.current_tok.pos_start, self.current_tok.pos_end,
          "Se esperaba un ']', 'PoneleQue', 'PoneteAPensar', 'PasarLista', 'AhoritaQue', 'HacemeElParo', int, float, identifier, '+', '-', '(', '[' or 'NadaQueVer'"
        ))

      while self.current_tok.type == TT_COMMA:
        res.register_advancement()
        self.advance()

        element_nodes.append(res.register(self.expr()))
        if res.error: return res

      if self.current_tok.type != TT_RSQUARE:
        return res.failure(InvalidSyntaxError(
          self.current_tok.pos_start, self.current_tok.pos_end,
          f"Expected ',' or ']'"
        ))

      res.register_advancement()
      self.advance()

    return res.success(ListNode(
      element_nodes,
      pos_start,
      self.current_tok.pos_end.copy()
    ))

  def if_expr(self):
    res = ParseResult()
    all_cases = res.register(self.if_expr_cases('PoneteAPensar'))
    if res.error: return res
    cases, else_case = all_cases
    return res.success(IfNode(cases, else_case))

  def if_expr_b(self):
    return self.if_expr_cases('Decidite')

  def if_expr_c(self):
    res = ParseResult()
    else_case = None

    if self.current_tok.matches(TT_KEYWORD, 'HaceteLoco'):
      res.register_advancement()
      self.advance()

      if self.current_tok.type == TT_NEWLINE:
        res.register_advancement()
        self.advance()

        statements = res.register(self.statements())
        if res.error: return res
        else_case = (statements, True)

        if self.current_tok.matches(TT_KEYWORD, 'Cheque'):
          res.register_advancement()
          self.advance()
        else:
          return res.failure(InvalidSyntaxError(
            self.current_tok.pos_start, self.current_tok.pos_end,
            "Se esperaba un 'Cheque'"
          ))
      else:
        expr = res.register(self.statement())
        if res.error: return res
        else_case = (expr, False)

    return res.success(else_case)

  def if_expr_b_or_c(self):
    res = ParseResult()
    cases, else_case = [], None

    if self.current_tok.matches(TT_KEYWORD, 'Decidite'):
      all_cases = res.register(self.if_expr_b())
      if res.error: return res
      cases, else_case = all_cases
    else:
      else_case = res.register(self.if_expr_c())
      if res.error: return res

    return res.success((cases, else_case))

  def if_expr_cases(self, case_keyword):
    res = ParseResult()
    cases = []
    else_case = None

    if not self.current_tok.matches(TT_KEYWORD, case_keyword):
      return res.failure(InvalidSyntaxError(
        self.current_tok.pos_start, self.current_tok.pos_end,
        f"Expected '{case_keyword}'"
      ))

    res.register_advancement()
    self.advance()

    condition = res.register(self.expr())
    if res.error: return res

    if not self.current_tok.matches(TT_KEYWORD, 'Tonces'):
      return res.failure(InvalidSyntaxError(
        self.current_tok.pos_start, self.current_tok.pos_end,
        f"Se esperaba un 'Tonces'"
      ))

    res.register_advancement()
    self.advance()

    if self.current_tok.type == TT_NEWLINE:
      res.register_advancement()
      self.advance()

      statements = res.register(self.statements())
      if res.error: return res
      cases.append((condition, statements, True))

      if self.current_tok.matches(TT_KEYWORD, 'Cheque'):
        res.register_advancement()
        self.advance()
      else:
        all_cases = res.register(self.if_expr_b_or_c())
        if res.error: return res
        new_cases, else_case = all_cases
        cases.extend(new_cases)
    else:
      expr = res.register(self.statement())
      if res.error: return res
      cases.append((condition, expr, False))

      all_cases = res.register(self.if_expr_b_or_c())
      if res.error: return res
      new_cases, else_case = all_cases
      cases.extend(new_cases)

    return res.success((cases, else_case))

  def for_expr(self):
    res = ParseResult()

    if not self.current_tok.matches(TT_KEYWORD, 'PasarLista'):
        return res.failure(InvalidSyntaxError(
            self.current_tok.pos_start, self.current_tok.pos_end,
            "Se esperaba un 'PasarLista'"
        ))
    res.register_advancement()
    self.advance()

    if not self.current_tok.matches(TT_KEYWORD, 'PoneleQue'):
        return res.failure(InvalidSyntaxError(
            self.current_tok.pos_start, self.current_tok.pos_end,
            "Expected 'PoneleQue' despues de 'PasarLista'"
        ))
    res.register_advancement()
    self.advance()

    if self.current_tok.type != TT_IDENTIFIER:
        return res.failure(InvalidSyntaxError(
            self.current_tok.pos_start, self.current_tok.pos_end,
            "Expected identifier"
        ))
    var_name = self.current_tok
    res.register_advancement()
    self.advance()

    if self.current_tok.type != TT_EQ:
        return res.failure(InvalidSyntaxError(
            self.current_tok.pos_start, self.current_tok.pos_end,
            "Expected '='"
        ))
    res.register_advancement()
    self.advance()

    start_value = res.register(self.expr())
    if res.error: return res

    if not self.current_tok.matches(TT_KEYWORD, 'Hasta'):
        return res.failure(InvalidSyntaxError(
            self.current_tok.pos_start, self.current_tok.pos_end,
            "Se esperaba un 'Hasta'"
        ))
    res.register_advancement()
    self.advance()

    end_value = res.register(self.expr())
    if res.error: return res

    if self.current_tok.matches(TT_KEYWORD, 'De'):
        res.register_advancement()
        self.advance()
        step_value = res.register(self.expr())
        if res.error: return res
    else:
        step_value = None

    if not self.current_tok.matches(TT_KEYWORD, 'Tonces'):
        return res.failure(InvalidSyntaxError(
            self.current_tok.pos_start, self.current_tok.pos_end,
            "Se esperaba un 'Tonces'"
        ))
    res.register_advancement()
    self.advance()

    if self.current_tok.type == TT_NEWLINE:
        res.register_advancement()
        self.advance()

        body = res.register(self.statements())
        if res.error: return res

        if not self.current_tok.matches(TT_KEYWORD, 'Cheque'):
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Se esperaba un 'Cheque' para terminar de 'PasarLista'"
            ))
        res.register_advancement()
        self.advance()

        return res.success(ForNode(var_name, start_value, end_value, step_value, body, True))
    else:
        body = res.register(self.statement())
        if res.error: return res
        return res.success(ForNode(var_name, start_value, end_value, step_value, body, False))


  def while_expr(self):
    res = ParseResult()

    if not self.current_tok.matches(TT_KEYWORD, 'AhoritaQue'):
      return res.failure(InvalidSyntaxError(
        self.current_tok.pos_start, self.current_tok.pos_end,
        f"Se esperaba un 'AhoritaQue'"
      ))

    res.register_advancement()
    self.advance()

    condition = res.register(self.expr())
    if res.error: return res

    if not self.current_tok.matches(TT_KEYWORD, 'Tonces'):
      return res.failure(InvalidSyntaxError(
        self.current_tok.pos_start, self.current_tok.pos_end,
        f"Se esperaba un 'Tonces'"
      ))

    res.register_advancement()
    self.advance()

    if self.current_tok.type == TT_NEWLINE:
      res.register_advancement()
      self.advance()

      body = res.register(self.statements())
      if res.error: return res

      if not self.current_tok.matches(TT_KEYWORD, 'Cheque'):
        return res.failure(InvalidSyntaxError(
          self.current_tok.pos_start, self.current_tok.pos_end,
          f"Se esperaba un 'Cheque'"
        ))

      res.register_advancement()
      self.advance()

      return res.success(WhileNode(condition, body, True))

    body = res.register(self.statement())
    if res.error: return res

    return res.success(WhileNode(condition, body, False))

  def func_def(self):
    res = ParseResult()

    if not self.current_tok.matches(TT_KEYWORD, 'HacemeElParo'):
        return res.failure(InvalidSyntaxError(
            self.current_tok.pos_start, self.current_tok.pos_end,
            f"Se esperaba un 'HacemeElParo'"
        ))

    res.register_advancement()
    self.advance()

    if self.current_tok.type == TT_IDENTIFIER:
        var_name_tok = self.current_tok
        res.register_advancement()
        self.advance()
    else:
        var_name_tok = None

    if self.current_tok.type != TT_LPAREN:
        return res.failure(InvalidSyntaxError(
            self.current_tok.pos_start, self.current_tok.pos_end,
            "Expected '('"
        ))

    res.register_advancement()
    self.advance()
    arg_name_toks = []

    if self.current_tok.type == TT_IDENTIFIER:
        arg_name_toks.append(self.current_tok)
        res.register_advancement()
        self.advance()

        while self.current_tok.type == TT_COMMA:
            res.register_advancement()
            self.advance()

            if self.current_tok.type != TT_IDENTIFIER:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "Expected identifier"
                ))

            arg_name_toks.append(self.current_tok)
            res.register_advancement()
            self.advance()

    if self.current_tok.type != TT_RPAREN:
        return res.failure(InvalidSyntaxError(
            self.current_tok.pos_start, self.current_tok.pos_end,
            "Expected ',' or ')'"
        ))

    res.register_advancement()
    self.advance()

    if self.current_tok.type == TT_ARROW:
        res.register_advancement()
        self.advance()

        # Allow body to start on a new line
        if self.current_tok.type == TT_NEWLINE:
            res.register_advancement()
            self.advance()

        body = res.register(self.expr())
        if res.error: return res

        return res.success(FuncDefNode(
            var_name_tok,
            arg_name_toks,
            body,
            True  # Auto-return for arrow functions
        ))

    if self.current_tok.type != TT_NEWLINE:
        return res.failure(InvalidSyntaxError(
            self.current_tok.pos_start, self.current_tok.pos_end,
            "Expected '->' or NEWLINE"
        ))

    res.register_advancement()
    self.advance()

    body = res.register(self.statements())
    if res.error: return res

    if not self.current_tok.matches(TT_KEYWORD, 'Cheque'):
        return res.failure(InvalidSyntaxError(
            self.current_tok.pos_start, self.current_tok.pos_end,
            "Se esperaba un 'Cheque'"
        ))

    res.register_advancement()
    self.advance()

    return res.success(FuncDefNode(
        var_name_tok,
        arg_name_toks,
        body,
        False  # No auto-return for block functions
    ))

  def class_def(self):
    res = ParseResult()

    if not self.current_tok.matches(TT_KEYWORD, 'Clase'):
        return res.failure(InvalidSyntaxError(
            self.current_tok.pos_start, self.current_tok.pos_end,
            "Se esperaba 'Clase'"
        ))

    res.register_advancement()
    self.advance()

    if self.current_tok.type != TT_IDENTIFIER:
        return res.failure(InvalidSyntaxError(
            self.current_tok.pos_start, self.current_tok.pos_end,
            "Se esperaba un identificador para el nombre de la clase"
        ))

    class_name_tok = self.current_tok
    res.register_advancement()
    self.advance()

    if self.current_tok.type != TT_LBRACE:
        return res.failure(InvalidSyntaxError(
            self.current_tok.pos_start, self.current_tok.pos_end,
            "Se esperaba '{' para el cuerpo de la clase"
        ))

    res.register_advancement()
    self.advance()

    body_node = res.register(self.statements())
    if res.error: return res

    if self.current_tok.type != TT_RBRACE:
        return res.failure(InvalidSyntaxError(
            self.current_tok.pos_start, self.current_tok.pos_end,
            "Se esperaba '}' para cerrar el cuerpo de la clase"
        ))

    res.register_advancement()
    self.advance()

    return res.success(ClassDefNode(class_name_tok, body_node))


  ###################################

  def bin_op(self, func_a, ops, func_b=None):
    if func_b is None:
        func_b = func_a

    res = ParseResult()
    left = res.register(func_a())
    if res.error: return res

    while self.current_tok.type in ops or (self.current_tok.type, self.current_tok.value) in ops:
        op_tok = self.current_tok
        res.register_advancement()
        self.advance()

        if op_tok.matches(TT_KEYWORD, 'NadaQueVer'):
            op_tok = Token(TT_NE, pos_start=op_tok.pos_start, pos_end=op_tok.pos_end)

        right = res.register(func_b())
        if res.error: return res

        left = BinOpNode(left, op_tok, right)

    return res.success(left)