from sympy import StrPrinter

class SimplePrinter(StrPrinter):
    def _print_And(self, expr):
        return "".join(map(self._print, expr.args))
    
    def _print_Or(self, expr):
        return " + ".join(map(self._print, expr.args))
    
    def _print_Not(self, expr):
        return self._print(expr.args[0]) + "'"

def simply(expr):
    return SimplePrinter().doprint(expr)