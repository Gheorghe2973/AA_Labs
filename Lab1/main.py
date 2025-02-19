import time
import math
import matplotlib.pyplot as plt


def fib_recursive(n):
    if n <= 1:
        return n
    return fib_recursive(n - 1) + fib_recursive(n - 2)

def fib_dp(n):
    if n < 0:
        raise ValueError("n must be non-negative")
    if n <= 1:
        return n
    dp = [0] * (n + 1)
    dp[0], dp[1] = 0, 1
    for i in range(2, n + 1):
        dp[i] = dp[i - 1] + dp[i - 2]
    return dp[n]

def matrix_mult(A, B):
    return [[A[0][0]*B[0][0] + A[0][1]*B[1][0],
             A[0][0]*B[0][1] + A[0][1]*B[1][1]],
            [A[1][0]*B[0][0] + A[1][1]*B[1][0],
             A[1][0]*B[0][1] + A[1][1]*B[1][1]]]

def matrix_pow(M, n):
    if n == 1:
        return M
    if n % 2 == 0:
        half = matrix_pow(M, n // 2)
        return matrix_mult(half, half)
    else:
        return matrix_mult(M, matrix_pow(M, n - 1))

def fib_matrix(n):
    if n == 0:
        return 0
    if n == 1:
        return 1
    M = [[1, 1],
         [1, 0]]
    result = matrix_pow(M, n - 1)
    return result[0][0]

def fib_binet(n):
    phi = (1 + math.sqrt(5)) / 2
    psi = (1 - math.sqrt(5)) / 2
    return int(round((phi**n - psi**n) / math.sqrt(5)))

def fib_iterative(n):
    if n < 0:
        raise ValueError("n must be non-negative")
    if n == 0:
        return 0
    if n == 1:
        return 1
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b

def fib_fast_doubling(n):
    def _fib(n):
        if n == 0:
            return (0, 1)
        a, b = _fib(n // 2)
        c = a * (2 * b - a)
        d = a * a + b * b
        if n % 2 == 0:
            return (c, d)
        else:
            return (d, c + d)
    return _fib(n)[0]

def fib_gen():
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b

def fib_via_generator(n):
    g = fib_gen()
    val = None
    for _ in range(n + 1):
        val = next(g)
    return val

def main():
    print("Choose a Fibonacci algorithm method (enter the number):")
    print("1: Naive Recursive Method")
    print("2: Dynamic Programming Method")
    print("3: Matrix Power Method")
    print("4: Binet's Formula Method")
    print("5: Iterative Method (Constant Space)")
    print("6: Fast Doubling Method")
    print("7: Generator-Based Method")
    
    try:
        choice = int(input("Your choice (1-7): "))
    except ValueError:
        print("Invalid input. Please enter a number between 1 and 7.")
        return

    methods = {
        1: fib_recursive,
        2: fib_dp,
        3: fib_matrix,
        4: fib_binet,
        5: fib_iterative,
        6: fib_fast_doubling,
        7: fib_via_generator
    }
    
    if choice not in methods:
        print("Invalid choice. Please run the script again and choose a number between 1 and 7.")
        return

    fib_function = methods[choice]
    
    if choice == 1:
        input_values = [5, 7, 10, 12, 15, 17, 20, 22, 25, 27, 30, 32, 35, 37, 40, 42, 45]
    else:
        input_values = [501, 631, 794, 1000, 1259, 1585, 1995, 2512, 3162, 3981, 5012, 6310, 7943, 10000, 12589, 15849]
    
    times = [] 
    print("\nExecuting Fibonacci computation with n-values as columns:")
    
    header = "n-th term:\t" + "\t".join(str(n) for n in input_values)
    print(header)
    
    time_row = "Time (sec):\t"
    for n in input_values:
        start = time.perf_counter()
        _ = fib_function(n)
        end = time.perf_counter()
        elapsed = end - start
        times.append(elapsed)
        time_row += f"{elapsed:.6f}\t"
    print(time_row)
    
    plt.figure(figsize=(10, 6))
    plt.plot(input_values, times, marker='o', linestyle='-', color='b')
    plt.xlabel("n-th Fibonacci Term")
    plt.ylabel("Execution Time (seconds)")
    plt.title("Execution Time vs. n-th Fibonacci Term")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("fibonacci_plot7.png")


if __name__ == "__main__":
    main()
