import sympy
import random
import urllib.parse

def check(answer, correct_answer):
    if sympy.simplify(sympy.parsing.parse_expr(answer, transformations = 'all') - correct_answer) == 0:
        return True

    else:
        return False

def html_problem(expr):
    return sympy.printing.mathml(expr)

def image(expr):
    return f'https://latex.codecogs.com/png.latex?{urllib.parse.quote(sympy.latex(expr))}'

def black_background_image(image_link):
    return 'https://latex.codecogs.com/png.latex?\\bg_black\\color{White}' + f'{urllib.parse.quote(sympy.latex(image_link))}'

def set_seed(seed):
    random.seed(seed)

class Base:
    @staticmethod
    def init():
        global x, y; x, y = sympy.symbols('x y')
        global f; f = sympy.Function('f')
        sympy.init_printing()

    @staticmethod
    def generate():
        terms = []
        num_terms = random.choices([1, 2, 3], weights = [2, 2, 1])[0]
        can_div = True

        if num_terms == 3:
            can_div = False

        for _ in range(num_terms):
            coeff = random.randint(1, 5)
            power = random.randint(1, 3)
            shift = random.randint(1, 5)
            root_degree = random.randint(2, 4)

            term_type = random.choices(['poly', 'trig', 'exp', 'exponential', 'log', 'root'], weights = [7, 3, 2, 3, 2, 1])[0]

            if term_type == 'poly':
                terms.append(coeff * x ** power)

            elif term_type == 'trig':
                f = random.choices([sympy.sin, sympy.cos, sympy.tan, sympy.cot, sympy.sec, sympy.csc], weights = [3, 2, 2, 1, 1, 1])[0]
                terms.append(coeff * f(x))
                can_div = False

            elif term_type == 'exp':
                terms.append(coeff * sympy.exp(x))

            elif term_type == 'exponential':
                terms.append(coeff * (power ** x))
                can_div = False

            elif term_type == 'log':
                terms.append(coeff * sympy.log(x + shift))
                can_div = False

            elif term_type == 'root':
                inside = x + shift
                if root_degree == 2:
                    root_expr = sympy.sqrt(inside)
                else:
                    root_expr = sympy.root(inside, root_degree)
                terms.append(coeff * root_expr)
                can_div = False

        expr = sum(terms)
        if can_div and random.choice([True, False, False]):
            whole_div_shift = random.randint(1, 3)
            power = random.randint(1, 3)
            coeff = random.randint(1, 3)
            expr = expr / (coeff * (x + whole_div_shift) ** power)

        return expr

    @staticmethod
    def equation(expr):
        return sympy.Eq(sympy.Function('f')(x), expr)

    @staticmethod
    def question(self):
        raise NotImplementedError('Subclasses should implement this!')

    @staticmethod
    def answer(self, expr):
        raise NotImplementedError('Subclasses should implement this!')

class RandomDerivative(Base):
    @staticmethod
    def question():
        return sympy.Eq(sympy.Function('f\'')(x), sympy.Symbol('...'))

    @staticmethod
    def answer(expr):
        return sympy.simplify(sympy.diff(expr, x))

class RandomIntegral(Base):
    @staticmethod
    def question():
        return sympy.Eq(sympy.Integral(sympy.Function('f')(x)), sympy.Symbol('...'))

    @staticmethod
    def answer(expr):
        return sympy.simplify(sympy.integrate(expr, x))