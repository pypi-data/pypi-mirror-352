import math
import numpy as np
import sympy as sp
from scipy import integrate
from scipy.special import eval_jacobi, eval_legendre, eval_genlaguerre, eval_hermite
import matplotlib.pyplot as plt
import scipy.integrate as integrate

x = sp.symbols('x')  # общий символ x для sympy

class ChebyshevFirstKind:

    def __init__(self, n):
        self.n = n

    def size(self):
        return self.n

    def evaluate(self, x_val):
        n = self.n
        """Аналитическая формула"""
        return np.cos(n * np.arccos(x_val))

    def recurrent(self, x_val):
        """Рекуррентная формула вычисления T_n(x)"""
        n = self.n
        if n == 0:
            return 1
        elif n == 1:
            return x_val
        else:
            T_0 = 1
            T_1 = x_val
            for i in range(2, n + 1):
                T_n = 2 * x_val * T_1 - T_0
                T_0, T_1 = T_1, T_n
            return T_n

    def diff_eq(self):
        '''Подставляет многочлен Чебышева 1-го рода порядка n
        в уравнение (1-x²)y\'\' - xy\' + n²y = 0 '''
        n = self.n
        y = sp.chebyshevt(n, x)

        # Вычисляем первую и вторую производные
        first_derivative = sp.diff(y, x)
        second_derivative = sp.diff(first_derivative, x)
        # Составляем уравнение
        result = (1 - x ** 2) * second_derivative - x * first_derivative + n ** 2 * y
        return result

    def generating_function(self, x_val, r):
        """Вычисляет сумму: ∑_{i=0}^{n-1} r^i * T_i(x_val)"""
        return sum(r ** i * np.cos(i * np.arccos(x_val)) for i in range(self.n))

    def roots(self):
        """Корни T_n"""
        n = self.n
        return [float(round(np.cos((2 * k - 1) * np.pi / (2 * n)), 4)) for k in range(1, n + 1)]

    def orthogonal_with(self, other):
        """Вычисляет интеграл ортогональности между T_n(x) и T_m(x)"""
        x = sp.Symbol('x')
        T_n = sp.chebyshevt(self.n, x)
        T_m = sp.chebyshevt(other.n, x)
        integrand = T_n * T_m / sp.sqrt(1 - x ** 2)
        return sp.integrate(integrand, (x, -1, 1))

    def plot(self, num_points=500):
        """Построение графика T_n"""
        n = self.n
        x = np.linspace(-1, 1, num_points)
        y = np.cos(n * np.arccos(x))
        plt.plot(x, y, label=f"T_{n}(x)")
        plt.title(f"Полином Чебышёва первого рода T_{n}(x)")
        plt.xlabel("x")
        plt.ylabel(f"T_{n}(x)")
        plt.grid(True)
        plt.legend()
        plt.show()

class ChebyshevSecondKind:
    """Свойства полиномов Чебышёва второго рода"""

    def __init__(self, n):
        self.n = n

    def size(self):
        return self.n

    def evaluate(self, x_val):
        n = self.n
        return np.sin((n + 1) * np.arccos(x_val)) / np.sqrt(1 - x_val**2)

    def recurrent(self, x_val):
        n = self.n
        if n == 0:
            return 1
        elif n == 1:
            return 2 * x_val
        else:
            U0, U1 = 1, 2 * x_val
            for _ in range(2, n + 1):
                U0, U1 = U1, 2 * x_val * U1 - U0
            return U1

    def roots(self):
        n = self.n
        return [float(round(np.cos(k * np.pi / (n + 1)), 4)) for k in range(1, n + 1)]

    def orthogonal_with(self, other):
        T_n = sp.chebyshevu(self.n, x)
        T_m = sp.chebyshevu(other.n, x)
        integrand = T_n * T_m * sp.sqrt(1 - x**2)
        return sp.integrate(integrand, (x, -1, 1))

    def plot(self, num_points=500):
        n = self.n
        x_vals = np.linspace(-1, 1, num_points)
        y_vals = [self.evaluate(x_val) for x_val in x_vals]
        plt.plot(x_vals, y_vals, label=f"U_{n}(x)")
        plt.title(f"Полином Чебышёва второго рода U_{n}(x)")
        plt.xlabel("x")
        plt.ylabel(f"U_{n}(x)")
        plt.grid(True)
        plt.legend()
        plt.show()


class LegendrePolynomial:
    """Свойства многочленов Лежандра"""

    def __init__(self, n):
        self.n = n
        self.symbol = x

    def size(self):
        return self.n

    def evaluate(self, x_val):
        return eval_legendre(self.n, x_val)

    def rodrigues(self):
        """Формула Родрига (символьный вывод)"""
        n = self.n
        return (1 / (2**n * sp.factorial(n))) * sp.diff((x**2 - 1)**n, x, n)

    def rodrigues_numeric(self, x_val):
        """Значение по формуле Родрига"""
        expr = self.rodrigues()
        return float(expr.subs(x, x_val))

    def recurrent(self, x_val):
        """Рекуррентная формула"""
        n = self.n
        if n == 0:
            return 1
        elif n == 1:
            return x_val
        else:
            P0, P1 = 1, x_val
            for i in range(2, n + 1):
                P0, P1 = P1, ((2 * i - 1) * x_val * P1 - (i - 1) * P0) / i
            return P1

    def orthogonal_with(self, other):
        """Интеграл ортогональности с другим многочленом"""
        m = other.n
        n = self.n
        P_m = sp.legendre(m, x)
        P_n = sp.legendre(n, x)
        return sp.integrate(P_m * P_n, (x, -1, 1))

    def generating_function(self, x_val, w):
        """
        Сумма первых n членов производящей функции:
        ∑ wⁿ Pₙ(x)
        """

        return sum(w**i * eval_legendre(i, x_val) for i in range(self.n))


    def diff_eq(self):
        """Дифференциальное уравнение"""
        n = self.n
        y = sp.legendre(n, x)
        dy = sp.diff(y, x)
        d2y = sp.diff(dy, x)
        return (1 - x**2) * d2y - 2 * x * dy + n * (n + 1) * y

    def estimate(self):
        """Оценка модуля |P_n(x)| на [-1, 1]"""
        return 1  # максимум модуля многочлена Лежандра на [-1,1] равен 1

    def plot(self, num_points=500):
        """График P_n(x)"""
        n = self.n
        x_vals = np.linspace(-1, 1, num_points)
        y_vals = eval_legendre(n, x_vals)
        plt.plot(x_vals, y_vals, label=f"P_{n}(x)")
        plt.title(f"Многочлен Лежандра P_{n}(x)")
        plt.xlabel("x")
        plt.ylabel(f"P_{n}(x)")
        plt.grid(True)
        plt.legend()
        plt.show()


class LaguerrePolynomial:
    """Свойства обобщённых полиномов Лагерра (Чебышёва-Лаггера)"""

    def __init__(self, n, alpha=0):
        self.n = n
        self.alpha = alpha

    def size(self):
        return self.n

    def evaluate(self, x_val):
        return eval_genlaguerre(self.n, self.alpha, x_val)

    def orthogonal_with(self, other):
        """Ортогональность: ∫₀^∞ x^α e^{-x} Lₘ^α(x)·Lₙ^α(x) dx"""
        alpha = self.alpha
        n, m = self.n, other.n

        integrand = lambda x1: x1 ** alpha * np.exp(-x1) * \
            eval_genlaguerre(n, alpha, x1) * eval_genlaguerre(m, alpha, x1)

        result, _ = integrate.quad(integrand, 0, np.inf)
        return 0 if abs(result) < 1e-3 else result

    def generating_function(self, x_val, t, n_terms=0):
        """
        Производящая функция:
        ∑ Lₙ^α(x) tⁿ
        """
        if n_terms == 0:
            n_terms = self.n
        return sum(
            eval_genlaguerre(n, self.alpha, x_val) * t**n
            for n in range(n_terms)
        )

    def recurrent(self, x_val):
        """
        Рекуррентное соотношение:
        (n+1)L_{n+1} = (2n+1+α−x)L_n − (n+α)L_{n−1}
        """
        n = self.n
        alpha = self.alpha

        if n == 0:
            return 1
        elif n == 1:
            return 1 + alpha - x_val
        else:
            L0 = 1
            L1 = 1 + alpha - x_val
            for i in range(2, n + 1):
                L_next = ((2 * i - 1 + alpha - x_val) * L1 - (i - 1 + alpha) * L0) / i
                L0, L1 = L1, L_next
            return L1

    def diff_eq(self):
        """
        Дифференциальное уравнение:
        x·y'' + (1 + α - x)·y' + n·y = 0
        """
        n = self.n
        alpha = self.alpha
        y = sp.assoc_laguerre(n, alpha, x)
        dy = sp.diff(y, x)
        d2y = sp.diff(dy, x)
        return x * d2y + (1 + alpha - x) * dy + n * y

    def plot(self, num_points=500):
        """График L_n^α(x)"""
        x_vals = np.linspace(0, 20, num_points)
        y_vals = self.evaluate(x_vals)
        plt.plot(x_vals, y_vals, label=f"L_{self.n}^{self.alpha}(x)")
        plt.title(f"Обобщённый полином Лагерра L_{self.n}^{self.alpha}(x)")
        plt.xlabel("x")
        plt.ylabel(f"L_{self.n}^{self.alpha}(x)")
        plt.grid(True)
        plt.legend()
        plt.show()


class JacobiPolynomial:
    """Свойства многочленов Якоби P_n^{(α, β)}(x)"""

    def __init__(self, n, alpha, beta):
        self.n = n
        self.alpha = alpha
        self.beta = beta

    def size(self):
        return self.n

    def evaluate(self, x_val):
        return eval_jacobi(self.n, self.alpha, self.beta, x_val)

    def rodrigues(self):
        """Формула Родрига (символьно)"""
        n, a, b = self.n, self.alpha, self.beta
        coeff = (-1) ** n / (2 ** n * math.factorial(n))
        term1 = (1 - x) ** (-a) * (1 + x) ** (-b)
        term2 = sp.diff((1 - x) ** (n + a) * (1 + x) ** (n + b), x, n)
        return coeff * term1 * term2

    def rodrigues_numeric(self, x_val):
        """Значение по формуле Родрига"""
        return float(self.rodrigues().subs(x, x_val))

    def orthogonal_with(self, other):
        """Интеграл ортогональности"""
        a, b = self.alpha, self.beta
        Pn = sp.jacobi(self.n, a, b, x)
        Pm = sp.jacobi(other.n, a, b, x)
        w = (1 - x) ** a * (1 + x) ** b
        return sp.integrate(Pn * Pm * w, (x, -1, 1))

    def inn(self):
        """Норма невзвешенного многочлена"""
        a, b, n = self.alpha, self.beta, self.n
        numerator = 2 ** (a + b + 1)
        denominator = math.factorial(n) * (2 * n + a + b + 1)
        gamma1 = math.gamma(n + a + 1)
        gamma2 = math.gamma(n + b + 1)
        gamma3 = math.gamma(n + a + b + 1)
        return numerator / denominator * (gamma1 * gamma2) / gamma3

    def lambda_n(self):
        """λₙ для нормированных многочленов"""
        a, b, n = self.alpha, self.beta, self.n
        num = 4 * n * (n + a) * (n + b) * (n + a + b)
        den = (2 * n + a + b - 1) * (2 * n + a + b)**2 * (2 * n + a + b + 1)
        return num / den

    def alpha_n(self):
        """αₙ для нормированных многочленов"""
        a, b, n = self.alpha, self.beta, self.n
        num = b**2 - a**2
        den = (2 * n + a + b) * (2 * n + a + b + 2)
        return num / den

    def J_hat(self, x_val):
        """Нормированный полином Якоби Ĵ_n(x_val)"""
        n, a, b = self.n, self.alpha, self.beta
        top = math.factorial(n) * (2 * n + a + b + 1) * math.gamma(n + a + b + 1)
        bottom = 2 ** (a + b + 1) * math.gamma(n + a + 1) * math.gamma(n + b + 1)
        norm = math.sqrt(top / bottom)
        return norm * eval_jacobi(n, a, b, x_val)

    def J_hat_recurrent(self, x_val):
        a, b, n = self.alpha, self.beta, self.n

        if n == 0:
            return JacobiPolynomial(a, b, 0).J_hat(x_val)
        elif n == 1:
            return JacobiPolynomial(a, b, 1).J_hat(x_val)

        # Начальные значения
        J0 = JacobiPolynomial(a, b, 0).J_hat(x_val)
        J1 = JacobiPolynomial(a, b, 1).J_hat(x_val)

        Jm2, Jm1 = J0, J1

        for k in range(1, n):
            jac_k = JacobiPolynomial(a, b, k)
            alpha_k = jac_k.alpha_n()
            lambda_k = jac_k.lambda_n()

            Jk = (x_val - alpha_k) * Jm1 - lambda_k * Jm2
            Jm2, Jm1 = Jm1, Jk

        return Jm1

    def generating_function(self, x_val, w, terms=10):
        """Производящая функция для многочленов Якоби: Σ P_n^{(α, β)}(x)·wⁿ"""
        result = 0
        for i in range(terms):
            # Используем временно изменяемый объект для вычисления нужной степени
            self.n = i
            result += w ** i * self.evaluate(x_val)
        return result

    def diff_eq(self):
        """Дифференциальное уравнение Якоби"""
        n, a, b = self.n, self.alpha, self.beta
        y = sp.jacobi(n, a, b, x)
        dy = sp.diff(y, x)
        d2y = sp.diff(dy, x)
        return (1 - x ** 2) * d2y + (b - a - (2 + a + b) * x) * dy + n * (n + a + b + 1) * y

    def estimate(self):
        """Оценка значения"""
        return f"|P_{self.n}^({self.alpha},{self.beta})(x)| ≤ C на [-1, 1] при α, β > -1"

    def plot(self, num_points=400):
        """График одного многочлена P_n^{(α, β)}(x) степени self.n"""
        x_vals = np.linspace(-1, 1, num_points)
        y_vals = [eval_jacobi(self.n, self.alpha, self.beta, x) for x in x_vals]

        plt.figure(figsize=(8, 5))
        plt.plot(x_vals, y_vals, label=f"$P_{{{self.n}}}^{{({self.alpha},{self.beta})}}(x)$")
        plt.title(f"Многочлен Якоби P_{self.n}^({self.alpha},{self.beta})(x)")
        plt.xlabel("x")
        plt.ylabel("P_n(x)")
        plt.grid(True)
        plt.legend()
        plt.tight_layout()
        plt.show()

class HermitePolynomial:
    """Свойства многочленов Эрмита"""

    def __init__(self, n):
        self.n = n

    def evaluate(self, x_val):
        if isinstance(x_val, (int, float, np.ndarray)):
            return eval_hermite(self.n, x_val)
        else:
            return sp.hermite(self.n, x_val)

    def recurrent(self, x_val):
        n = self.n
        if n == 0:
            return np.ones_like(x_val)
        elif n == 1:
            return 2 * x_val

        H0 = np.ones_like(x_val)
        H1 = 2 * x_val
        for i in range(2, n + 1):
            Hn = 2 * x_val * H1 - 2 * (i - 1) * H0
            H0, H1 = H1, Hn
        return H1

    def generating_function(self, x_val, t_val, n_terms=0):
        """Сумма производящей функции: Σ Hₙ(x)tⁿ/n!"""
        if np.abs(t_val) >= 1:
            raise ValueError("Параметр t должен удовлетворять условию |t| < 1.")

        result = np.zeros_like(x_val, dtype=float)
        if n_terms == 0:
            n_terms = self.n

        for n in range(n_terms + 1):
            term = eval_hermite(n, x_val) * (t_val ** n) / math.factorial(n)
            result += term
        return result

    def orthogonal_with(self, other):
        """Интеграл ортогональности:
        ∫ Hₘ(x)·Hₙ(x)·e^{-x²} dx = sqrt(pi)·2ⁿ·n!·δₘₙ
        """
        m, n = self.n, other.n
        Hm = sp.hermite(m, x)
        Hn = sp.hermite(n, x)
        integrand = Hm * Hn * sp.exp(-x ** 2)
        integral = sp.integrate(integrand, (x, -sp.oo, sp.oo))
        return sp.simplify(integral)

    def diff_eq(self):
        """Дифференциальное уравнение Эрмита: y'' - 2x·y' + 2n·y = 0"""
        n = self.n
        y = sp.hermite(n, x)
        dy = sp.diff(y, x)
        d2y = sp.diff(dy, x)
        return d2y - 2 * x * dy + 2 * n * y

    def plot(self, x_range=(-3, 3), points=400):
        """График многочлена Эрмита Hₙ(x)"""
        x_vals = np.linspace(x_range[0], x_range[1], points)
        y_vals = eval_hermite(self.n, x_vals)

        plt.plot(x_vals, y_vals, label=f"H_{self.n}(x)")
        plt.title(f"Многочлен Эрмита H_{self.n}(x)")
        plt.xlabel("x")
        plt.ylabel("Hₙ(x)")
        plt.grid(True)
        plt.legend()
        plt.tight_layout()
        plt.show()