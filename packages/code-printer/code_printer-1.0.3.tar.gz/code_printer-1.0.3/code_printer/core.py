"""
Core functionality for the Code Printer package
"""

class CodePrinter:
    def __init__(self):
        #set of 10 codes 
        self.codes = {
            1: """#Do little Method

from sympy import *
a=Matrix([[4,10,8],[10,26,26],[8,26,61]])
b=Matrix([44,128,214])
print("A matrix")
display(a)
print("B matrix")
display(b)

u11=a[0,0]
u12=a[0,1]
u13=a[0,2]
l21=a[1,0]/u11
u22=a[1,1]-l21*u12
u23=a[1,2]-l21*u13
l31=a[2,0]/u11
l32=(a[2,1]-l31*u12)/u22
u33=a[2,2]-l31*u13-l32*u23

l=Matrix([[1,0,0],[l21,1,0],[l31,l32,1]])
u=Matrix([[u11,u12,u13],[0,u22,u23],[0,0,u33]])

print("L matrix")
display(l)
print("U matrix")
display(u)

y=l.solve(b)
x=u.solve(y)

print("The solution is")
display(x)

""",
            2: """#Crouts Method

from sympy import *
a=Matrix([[4,10,8],[10,26,26],[8,26,61]])
b=Matrix([44,128,214])
print("A matrix")
display(a)
print("B matrix")
display(b)

l11=a[0,0]
u12=a[0,1]/l11
u13=a[0,2]/l11
l21=a[1,0]
l22=a[1,1]-l21*u12
u23=(a[1,2]-l21*u13)/l22
l31=a[2,0]
l32=a[2,1]-l31*u12
l33=a[2,2]-l31*u13-l32*u23

l=Matrix([[l11,0,0],[l21,l22,0],[l31,l32,l33]])
u=Matrix([[1,u12,u13],[0,1,u23],[0,0,1]])

print("L matrix")
display(l)
print("U matrix")
display(u)

y=l.solve(b)
x=u.solve(y)

print("The solution is")
display(x)
""",

            3: """#cholesky Method

a=Matrix([[4,10,8],[10,26,26],[8,26,61]])
b=Matrix([44,128,214])
print("A matrix")
display(a)
print("B matrix")
display(b)

l11=sqrt(a[0,0])
l21=a[0,1]/l11
l31=a[0,2]/l11
l22=sqrt(a[1,1]-l21**2)
l32=(a[1,2]-l21*l31)/l22
l33=sqrt(a[2,2]-l31**2-l32**2)

l=Matrix([[l11,0,0],[l21,l22,0],[l31,l32,l33]])
print("L matrix")
display(l)
y=l.solve(b)
x=l.T.solve(y)
print("The solution is")
display(x)
""",

            4: """#SVD-SINGULAR VALUE DECOMPOSITION

import cv2
import numpy as np
import matplotlib.pyplot as plt

img=r"download.jpeg"
A=cv2.imread(img,0)

u,s,vt=np.linalg.svd(A,full_matrices=False)
k=int(input("Enter the value of Compression"))
compressed=np.dot(u[:,:k],np.dot(np.diag(s[:k]),vt[:k,:]))

plt.imshow(A,cmap="grey")
plt.title("Real image")
plt.show()

plt.imshow(compressed,cmap="grey")
plt.title("Compressed image")
""",

            5: """#PCA PRINCIPAL COMPONENT ANALYSIS
from sympy import *
print("The dataset is")
a=Matrix([[19,22,6,3,2,20],[12,6,9,15,13,5]])
display(a)
n = len(a[0, :])
x1 = sum(a[0, :]) / n
x2 = sum(a[1, :]) / n
x = a
for j in range(n):
    x[0, j] -= x1
    x[1, j] -= x2
print("x matrix is")
display(x)

s=(x*x.T)/(n-1)
print("Covariance Matrix")
display(s)

l=max(list(s.eigenvals()))
print(l)

for val, mul, vects in s.eigenvects():
    print(vects)
    if val == l:
       v = vecs[0]  
       break

e=v/v.norm()
y=e.T*x
print("The first Principal component is ")
display(y.evalf())
""",

            6: """#GRADIENT OF A MATRIX WRT A MATRIX

from sympy import *
x0,x1,x2,x3=symbols("x0 x1 x2 x3")
f=Matrix([[x0**2*x1*x2,x1**2*x2*x3],[x1*x3**2,x1*x2**3]])
x=Matrix([[x0,x1],[x2,x3]])



frows,fcols=f.shape
xrows,xcols=x.shape

grad=sp.MutableDenseNDimArray.zeros(xrows,xcols,frows,fcols)

for i in range(xrows):
    for j in range (xcols):
        for k in range(frows):
            for h in range(fcols):
                grad[i,j,k,h]=diff(f[k,h],x[i,j])
display(grad)
""",

            7: """#AUTOMATIC Differentiation
            from sympy import *

x,a,b,c,d,k =  symbols("x a b c d k")
g=log(sin(x)**2)+sin(x)**2+exp(sin(x)**2)

a = x
b = sin(a)
c = b**2
d = log(c)
k = exp(c)
g = d + c + k


result = g.diff(x)

display(result)
""",

            8: """#steepest descent method / gradient descent
from sympy import *
x,y,z=symbols("x y z")
f=x-y+2*x**2+2*x*y+y**2
fx=f.diff(x)
fy=f.diff(y)

del_f=Matrix([fx,fy])
h=hessian(f,(x,y))
display(h)
display(del_f)

a=Matrix([0,0])
b=del_f.subs({x:0,y:0})

while(True):
    s=-1*b
    l1=(s.T*s)
    l2=(s.T*h*s)
    l=l1[0]/l2[0]
    a=a+l*s
    b=del_f.subs({x:a[0],y:a[1]})

    if abs(b[0])<=0.01 and abs(b[1])<=0.01:
        display(a.evalf())
        break
""",

            9: """#hessian matrix optimization
from sympy import *

x,y,z=symbols("x y z")
f=x**2+y**2+z**2+x*y+z*x+y*z
print("The function is ")
display(f)

fx=diff(f,x)
fy=diff(f,y)
fz=diff(f,z)
a=solve((fx,fy,fz),(x,y,z))
s=[a[x],a[y],a[z]]
print("The stationary points are")
display(s)

h=hessian(f,(x,y,z))
print("The hessian matrix is")
display(h)

e=list(h.eigenvals())
print("The eigen values are")
print(e)

countp=0
countn=0

for i in e:
        
    if(i>=0):
        countp+=1
        if countp==len(e):
            print("The points are local minima")
            break
            
    elif(i<0):
        countn-=1
        if countn==len(e):
            print("The points are local maxima")
            break

if countp!= len(e) and countn != len(e):
    print("Saddle Point")

result=f.subs({x:s[0],y:s[1],z:s[2]})
print("The solution is",result)
""",

            10: """#Newton Method

x,y,z= symbols('x y z')
f=x-y+2*x**2+2*x*y+y**2
print("The function is")
display(f)

fx=diff(f,x)
fy=diff(f,y)


del_f=Matrix([fx,fy])
h=hessian(f,(x,y))
h_i=h**-1
print("Hessian Matrix")
display(h)

print("Hessian Inverse Matrix")
display(h_i)

a=Matrix([0,0])
b=del_f.subs({x:a[0],y:a[1]})

for i in range(2):
    a=a-h_i*b
    b=del_f.subs({x:a[0],y:a[1]})

print("minimum point is")
display(a)

solution=f.subs({x:a[0],y:a[1]})
print("The solution is",solution)
""",
                11:"""#Lagrange Multiplier Method

from sympy import *
x,y,z,l1,l2=symbols("x y z l1 l2")
f=4*y-2*z
h1=2*x-y-z-2
h2=x**2+y**2-1

F=f+l1*h1+l2*h2
Fx=diff(F,x)
Fy=diff(F,y)
Fz=diff(F,z)
Fl1 = diff(F, l1)
Fl2 = diff(F, l2)

sol=solve((Fx,Fy,Fz,h1,h2),(x,y,z,l1,l2))
print(sol)
f1=f.subs({x:sol[0][0],y:sol[0][1],z:sol[0][2]})
print("f1:",f1)
f2=f.subs({x:sol[1][0],y:sol[1][1],z:sol[1][2]})
print("f2",f2)

if(f1>f2):
    print("f1 is maximum vaue")
    print("f2 is minimum value")

elif(f1<f2):
    print("f2 is maximum vaue")
    print("f1 is minimum value")  """,

                12:"""#Fibonacii search method

from sympy import *
x=symbols("x")
f=x**2-2.6*x+2
print("The function is")
display(f)
a,b=-2,3

def fib(n):
    if n==0:
        return 1
    if n==1:
        return 1
    else:
        return fib(n-1)+fib(n-2)

n=6
for i in range(1,n+1):
    print("Iteration",i)
    l=(fib(n-i)/fib(n-i+1))*(b-a)
    x1=b-l
    x2=a+l
    fx1=f.subs({x:x1})
    fx2=f.subs({x:x2})

    if fx1>fx2:
        print("point a will be replaced")
        a,b=x1,b
        print(a,b,"\n")
    elif fx1<fx2:
        print("point b will be replaced")
        a,b=a,x2
        print(a,b,"\n")
        
x_min=(a+b)/2
f_min=f.subs({x:x_min})

print("minimum value of x is",x_min)
print("mininmum value of f is",f_min)"""
        }
    
    def print(self, code_number):
        """Print a specific code by number"""
        if code_number in self.codes:
            print(f"🤖 Machine Learning Code #{code_number}:")
            print("=" * 60)
            print(self.codes[code_number])
            print("=" * 60)
            return True
        else:
            print(f"❌ Error: Code #{code_number} not found.")
            print(f"Available codes: {', '.join(map(str, sorted(self.codes.keys())))}")
            return False
    
    def print_all_codes(self):
        """Print all codes"""
        print("🤖 All Machine Learning Algorithms:")
        print("=" * 70)
        algorithm_names = [
            "Do Little Method",
            "Crouts Method",
            "Cholesky", 
            "SVD SINGULAR VALUE DECOMPOSITION",
            "PCA PRINCIPAL COMPONENT ANALYSIS",
            "GRADIENT OF A MATRIX WRT A MATRIX",
            "Automatic differentiation",
            "steepest descent method / gradient descent",
            "hessian matrix optimization",
            "Newton Raphson Method",
            "Lagrange Multiplier Method",
            "Fibonacii search method"
            
        ]
        
        for num in sorted(self.codes.keys()):
            print(f"\n🔢 Code #{num}: {algorithm_names[num-1]}")
            print("-" * 60)
            print(self.codes[num])
            print("-" * 60)
    
    def list_codes(self):
        """List all available code numbers with previews"""
        print("🤖 Available Machine Learning Algorithms:")
        print("=" * 70)
        algorithm_names = [
            "Do Little Method",
            "Crouts Method",
            "Cholesky", 
            "SVD SINGULAR VALUE DECOMPOSITION",
            "PCA PRINCIPAL COMPONENT ANALYSIS",
            "GRADIENT OF A MATRIX WRT A MATRIX",
            "Automatic differentiation",
            "steepest descent method / gradient descent",
            "hessian matrix optimization",
            "Newton Raphson Method",
            "Lagrange Multiplier Method",
            "Fibonacii search method"
        ]
        
        for num in sorted(self.codes.keys()):
            print(f"  {num:2d}: {algorithm_names[num-1]}")
        print("=" * 70)
        print("💡 Use 'code-printer <number>' to view a specific algorithm")
        print("💡 Use 'code-printer --all' to view all algorithms")
    
    def search(self, keyword):
        """Search for codes containing a keyword"""
        matches = []
        algorithm_names = [
            "Do Little Method",
            "Crouts Method",
            "Cholesky", 
            "SVD SINGULAR VALUE DECOMPOSITION",
            "PCA PRINCIPAL COMPONENT ANALYSIS",
            "GRADIENT OF A MATRIX WRT A MATRIX",
            "Automatic differentiation",
            "steepest descent method / gradient descent",
            "hessian matrix optimization",
            "Newton Raphson Method",
            "Lagrange Multiplier Method",
            "Fibonacii search method"
        ]
        
        for num, code in self.codes.items():
            if (keyword.lower() in code.lower() or 
                keyword.lower() in algorithm_names[num-1].lower()):
                matches.append((num, algorithm_names[num-1]))
        
        if matches:
            print(f"🔍 Found {len(matches)} algorithm(s) matching '{keyword}':")
            print("=" * 70)
            for num, name in matches:
                print(f"  {num:2d}: {name}")
        else:
            print(f"❌ No algorithms found matching '{keyword}'")

# Test the functionality
if __name__ == "__main__":
    printer = CodePrinter()
    
    print("🤖 Machine Learning Code Printer Demo")
    print("=" * 50)
    
    print("\n📋 Available algorithms:")
    printer.list_codes()
    
    print(f"\n🔍 Searching for 'regression':")
    printer.search_codes("regression")
    
    print(f"\n📄 Showing Code #1 (Your Candidate Elimination Algorithm):")
    printer.print_code(1)