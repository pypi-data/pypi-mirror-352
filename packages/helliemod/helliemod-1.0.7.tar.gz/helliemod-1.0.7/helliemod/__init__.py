import tkinter as tk

# محاسبه فاکتوریل یک عدد
# Calculate the factorial of a number
def fact(n):
    x = 1
    for i in range(1, n + 1):
        x = x * i
    return x

# مقایسه دو عدد و بازگرداندن عدد بزرگ‌تر
# Compare two numbers and return the larger one
def compare(a, b):
    x = a
    if b > a:
        x = b
    return x

# محاسبه تعداد ارقام یک عدد
# Calculate the number of digits in a number
def digits(n):
    t = 0
    while n != 0:
        t = t + 1
        n = n // 10
    return t

# محاسبه مجموع ارقام یک عدد
# Calculate the sum of the digits of a number
def sum_digits(n):
    sum = 0
    while n != 0:
        sum = sum + n % 10
        n = n // 10
    return sum

# محاسبه مقلوب یک عدد
# Calculate the reverse of a number
def reverse(n):
    m = 0
    while n != 0:
        m = m * 10 + n % 10
        n = n // 10
    return m

# بررسی اول بودن یک عدد
# Check if a number is prime
def check_prime(n):
    flag = True
    for i in range(2, n):
        if n % i == 0:
            flag = False
    return flag

# محاسبه کوچک‌ترین مضرب مشترک (ک.م.م)
# Calculate the least common multiple (LCM)
def lcm(a, b):
    i = compare(a, b)
    while i % a != 0 or i % b != 0:
        i = i + 1
    return i

# محاسبه بزرگ‌ترین مقسوم‌علیه مشترک (ب.م.م)
# Calculate the greatest common divisor (GCD)
def gcd(a, b):
    for i in range(a, 0, -1):
        if a % i == 0 and b % i == 0:
            return i

# محاسبه قدر مطلق یک عدد
# Calculate the absolute value of a number
def abso_value(n):
    if n < 0:
        n = -n
    return n

# تولید دنباله فیبوناچی تا عدد مشخص
# Generate the Fibonacci sequence up to a specific number
def fib_seq(n):
    seq = []
    a = 1
    b = 1
    seq.append(a)
    seq.append(b)
    for i in range(n - 2):
        c = a + b
        seq.append(c)
        b, a = c, b
    return str(seq)

# محاسبه مجموع اعداد بین دو عدد با فاصله مشخص
# Calculate the sum of numbers between two numbers with a specific step
def sum_atob(a, b, c=1):
    return sum(range(a, b + 1, c))


def help():
    window = tk.Tk()
    window.title("Math Function Explanations")

    info = (
        "This program includes various mathematical functions implemented in Python using basic logic.",
        "\n\nFunction descriptions:\n",
        "- fact(n): Calculates the factorial of n.\n",
        "- compare(a, b): Returns the larger of a and b.\n",
        "- digits(n): Returns the number of digits in n.\n",
        "- sum_digits(n): Returns the sum of digits in n.\n",
        "- reverse(n): Returns the reverse of the digits in n.\n",
        "- check_prime(n): Checks if n is a prime number.\n",
        "- lcm(a, b): Returns the least common multiple of a and b.\n",
        "- gcd(a, b): Returns the greatest common divisor of a and b.\n",
        "- abso_value(n): Returns the absolute value of n.\n",
        "- fib_seq(n): Returns the first n numbers of the Fibonacci sequence.\n",
        "- sum_atob(a, b, c): Returns the sum from a to b with step c (default step is 1).\n"
    )

    label = tk.Label(
        window,
        text="".join(info),
        font=("Arial", 12),
        justify="left",
        padx=20,
        pady=20,
        wraplength=500
    )
    label.pack()

    button = tk.Button(
        window,
        text="Close",
        font=("Arial", 12),
        command=window.destroy
    )
    button.pack(pady=(0, 20))

    window.mainloop()