import tkinter as tk

def sib(n):
    x=1
    for i in range(1,n+1):
        x=x*i
    return x

def golabi(a,b):
    m=0
    for i in range(a,b+1):
        m+=i
    return m

def tameshk(a,b):
    x=a
    if b>a:
        x=b
    return x

def porteghal(n):
    while n**0.5%1!=0:
        n-=1
    return n

def talebi(n):
    t=0
    while n!=0:
        t+=1
        n//=10
    return t

def havij(n):
    m=0
    while n!=0:
        m=m*10+n%10
        n//=10
    return m

def kivi(n):
    m=0
    for i in range(1,n):
        if n%i==0:
            m+=1
    if m==n:
        j='yes'
    else:
        j='no'
    return j

def khiar(n):
    j="yes"
    for i in range(2,n):
        if n%i==0:
            j="no"
    return j

def holoo(a,b):
    i=a
    while a%i!=0 or b%i!=0:
        i-=1
    return i

def ananas(n):
    a=0
    b=1
    for i in range(n):
        t=a+b
        a=b
        b=t
    return a

def aloo(n,a):
    t=0
    while n!=0:
        if n%10==a:
            t=+t
        n//= 10
    return t

def moz(n):
    t=0
    for i in range(1,n+1):
            if n%i == 0:
                t+=1
    return t

def anar(n):
    if n <0:
        n = -n
    return n

def angoor(n):
    while n!=0:
        print(n%10)
        n//=10
    return

def albaloo(a,b):
    for i in range(a,b+1):
        print(i)
    return

def help():
    root = tk.Tk()
    root.title("Function Aliases Explanation")

    explanation = (
        "This file defines several numeric functions and assigns them shorter alias names for easier use.\n\n"
        "Here is a list of functions and their meanings:\n\n"
        "- sib(n): Factorial of n   => alias: factorial\n"
        "- golabi(a, b): Sum from a to b   => alias: sum\n"
        "- tameshk(a, b): Maximum of a and b   => alias: compare\n"
        "- porteghal(n): Largest perfect square <= n   => alias: perfect_square\n"
        "- talebi(n): Count digits in n   => alias: sum_digits\n"
        "- havij(n): Reverse digits of n   => alias: reverse\n"
        "- kivi(n): Check if n is a perfect number   => alias: perfect\n"
        "- khiar(n): Check if n is a prime number   => alias: check_prime\n"
        "- holoo(a, b): GCD of a and b   => alias: gcd\n"
        "- ananas(n): nth Fibonacci number   => alias: fibonacci\n"
        "- aloo(n, a): Count how many times digit a appears in n   => alias: count_digit\n"
        "- moz(n): Count number of divisors   => alias: count_divisor\n"
        "- anar(n): Absolute value of n   => alias: absolute\n"
        "- angoor(n): Print digits from last to first   => alias: print_reverse\n"
        "- albaloo(a, b): Print numbers from a to b   => alias: print_atob"
    )

    label = tk.Label(
        root,
        text=explanation,
        font=("Arial", 11),
        justify="left",
        wraplength=550,
        padx=20,
        pady=20
    )
    label.pack()

    button = tk.Button(
        root,
        text="Close",
        font=("Arial", 12),
        command=root.destroy
    )
    button.pack(pady=(0, 20))

    root.mainloop()


factorial = sib
sum = golabi
compare = tameshk
perfect_square = porteghal
sum_digits = talebi
reverse = havij
perfect = kivi
check_prime = khiar
gcd = holoo
fibonacci = ananas
count_digit = aloo
count_divisor = moz
absolute = anar
print_reverse = angoor
print_atob = albaloo
