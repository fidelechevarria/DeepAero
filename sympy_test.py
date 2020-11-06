from sympy import symbols, hessian, Function, N
import numpy as np

x, y = symbols('x y')
f = symbols('f', cls=Function)

f = (1/2)*np.power(x, 2) + 5*np.power(y, 2) + (2/3)*np.power((x-2), 4) + 8*np.power((y+1), 4)

H = hessian(f, [x, y]).subs([(x,1), (y,1)])
print(np.array(H))
print(N(H.condition_number()))
print(hessian(f, [x, y]))