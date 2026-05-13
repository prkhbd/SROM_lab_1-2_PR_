import math
import time

def measure_time(func, *args, index=None):
    start = time.time()
    res = func(*args)
    end = time.time()
    if index is not None:
        res = res[index]
    return res, end - start


def chunker(obj, n):
    return zip(*([iter(obj)] * n))

def to_hex(num_list):
    if num_list is None or num_list == [0]:
        return '0'
    i = len(num_list) - 1
    while num_list[i] == 0:
        i -= 1
        if i == -1:
            return '0'
    num_list.reverse()
    hex_str = ''
    for x in num_list:
        h = hex(x)[2:].rjust(8, '0')
        hex_str += h
    num_list.reverse()
    return hex_str.lstrip('0').swapcase()

def from_hex(hex_str):
    n = math.ceil(len(hex_str) / 8)
    if len(hex_str) % 8 != 0:
        hex_str = hex_str.rjust(n*8, '0')
    decs = [int(''.join(chunk),16) for chunk in chunker(hex_str,8)]
    decs.reverse()
    return decs


num_A = input('Enter A: ')
num_B = input('Enter B: ')
num_M = input('Enter M: ')

A = from_hex(num_A)
B = from_hex(num_B)
M = from_hex(num_M)


def add_long(a, b):
    max_len = max(len(a), len(b))
    res = []
    carry = 0
    for i in range(max_len):
        x = a[i] if i < len(a) else 0
        y = b[i] if i < len(b) else 0
        s = x + y + carry
        res.append(s & 0xFFFFFFFF)
        carry = s >> 32
    if carry > 0:
        res.append(carry)
    return res

def sub_long(a, b):
    res = []
    borrow = 0
    max_len = max(len(a), len(b))
    for i in range(max_len):
        x = a[i] if i < len(a) else 0
        y = b[i] if i < len(b) else 0
        diff = x - y - borrow
        if diff >= 0:
            res.append(diff)
            borrow = 0
        else:
            res.append((1 << 32) + diff)
            borrow = 1
    while len(res) > 1 and res[-1] == 0:
        res.pop()
    return res

def mul_long(a, b):
    if compare_long(a,b) == -1:
        a, b = b, a
    res = [0]*(len(a)+len(b))
    for i in range(len(b)):
        carry = 0
        for j in range(len(a)):
            t = res[i+j] + a[j]*b[i] + carry
            res[i+j] = t & 0xFFFFFFFF
            carry = t >> 32
        if carry > 0:
            res[i+len(a)] += carry
    while len(res) > 1 and res[-1] == 0:
        res.pop()
    return res

def divmod_long(a, b):
    if a==b:
        return [1], [0]
    r = a.copy()
    q = [0]
    k = bit_length(b)
    while compare_long(r,b) != -1:
        t = bit_length(r)
        shifted = shift_bits_high(b, t - k)
        if compare_long(r, shifted) < 0:
            t -= 1
            shifted = shift_bits_high(b, t - k)
        r = sub_long(r, shifted)
        q = add_long(q, shift_bits_high([1], t - k))
    return q, r

def sq_long(a):
    return mul_long(a, a)

def power_long(a, b):
    res = [1]
    for i in range(bit_length(b)):
        if bit_check(b,i):
            res = mul_long(res, a)
        a = mul_long(a, a)
    return res

# -------------------- Додаткові функції --------------------
def compare_long(a,b):
    while len(a)>1 and a[-1]==0: a.pop()
    while len(b)>1 and b[-1]==0: b.pop()
    if len(a) != len(b):
        return 1 if len(a)>len(b) else -1
    for i in reversed(range(len(a))):
        if a[i] != b[i]:
            return 1 if a[i]>b[i] else -1
    return 0

def shift_high(a, n):
    return [0]*n + a

def shift_low(a,n):
    return a[n:] if len(a)>n else [0]

def shift_bits_high(num, w):
    if w<=0 or num==[0]: return num.copy()
    res = shift_high(num.copy(), w//32)
    rem = w%32
    if rem>0:
        for _ in range(rem):
            last = (res[-1] >> 31) & 1
            for j in reversed(range(1,len(res))):
                res[j] = ((res[j]<<1) | ((res[j-1]>>31)&1)) & 0xFFFFFFFF
            res[0] = (res[0]<<1) & 0xFFFFFFFF
            if last: res.append(last)
    while len(res)>1 and res[-1]==0: res.pop()
    return res

def shift_bits_low(num, w):
    if w<=0 or num==[0]: return num
    res = num.copy()
    for _ in range(w//32): res.pop(0)
    rem = w%32
    if rem>0:
        for _ in range(rem):
            last = (res[0]&1)<<31
            for j in range(len(res)-1):
                res[j] = ((res[j]>>1)|((res[j+1]&1)<<31)) & 0xFFFFFFFF
            res[-1] = (res[-1]>>1 | last) & 0xFFFFFFFF
    while len(res)>1 and res[-1]==0: res.pop()
    return res

def bit_check(a,i):
    return (a[i//32] >> (i%32)) & 1

def bit_length(a):
    return (len(a)-1)*32 + a[-1].bit_length()

# -------------------- Алгоритми --------------------
def gcd_long(a,b):
    d = [1]
    comp_count=0
    sub_count=0
    while a[0]%2==0 and b[0]%2==0:
        a=shift_bits_low(a,1)
        b=shift_bits_low(b,1)
        d=shift_bits_high(d,1)
    while a[0]%2==0:
        a=shift_bits_low(a,1)
    zero = [0]
    while compare_long(b, zero)!=0:
        comp_count+=1
        while b[0]%2==0:
            b=shift_bits_low(b,1)
        cmp = compare_long(a,b)
        comp_count+=1
        if cmp==1:
            a, b = b, sub_long(a,b)
            sub_count+=1
        elif cmp==-1:
            a, b = a, sub_long(b,a)
            sub_count+=1
        else:
            b = [0]
    return mul_long(d,a), comp_count, sub_count

def lcm_long(a,b):
    g = gcd_long(a,b)[0]
    return divmod_long(mul_long(a,b), g)[0]

def mu_eval(module):
    k = len(module)
    beta = shift_high([1], 2*k)
    return divmod_long(beta, module)[0]

def barrett_reduction(val, module, mu):
    k = len(module)
    q = shift_bits_low(val.copy(), (k-1)*32)
    q = mul_long(q, mu)
    q = shift_bits_low(q, (k+1)*32)
    r = sub_long(val, mul_long(q, module))
    while compare_long(r,module)>=0:
        r = sub_long(r,module)
    return r

def add_mod(a,b,mod):
    return divmod_long(add_long(a,b), mod)[1]

def sub_mod(a,b,mod):
    return divmod_long(sub_long(a,b), mod)[1] if compare_long(a,b)>=0 else divmod_long(add_long(a, sub_long(mod,b)), mod)[1]

def mul_mod(a,b,mod):
    mu = mu_eval(mod)
    return barrett_reduction(mul_long(a,b), mod, mu)

def sq_mod(a,mod):
    return mul_mod(a,a,mod)

def pow_mod(a,b,mod):
    a_mod = divmod_long(a,mod)[1]
    b_mod = b
    res = [1]
    mu = mu_eval(mod)
    for i in range(bit_length(b_mod)):
        if bit_check(b_mod,i):
            res = barrett_reduction(mul_long(res,a_mod), mod, mu)
        a_mod = barrett_reduction(mul_long(a_mod,a_mod), mod, mu)
    return res



q_res, t = measure_time(lambda x,y: divmod_long(x,y)[0], A,B)
r_res, t_r = measure_time(lambda x,y: divmod_long(x,y)[1], A,B)
print(f'A / B = {to_hex(q_res)} ({t:.6f}s)')
print(f'A mod B = {to_hex(r_res)} ({t_r:.6f}s)')

sum_res, t = measure_time(add_long, A,B)
print(f'A + B = {to_hex(sum_res)} ({t:.6f}s)')

sub_res, t = measure_time(sub_long, A,B)
print(f'A - B = {to_hex(sub_res)} ({t:.6f}s)')

mul_res, t = measure_time(mul_long, A,B)
print(f'A * B = {to_hex(mul_res)} ({t:.6f}s)')

sq_res, t = measure_time(sq_long, A)
print(f'A^2 = {to_hex(sq_res)} ({t:.6f}s)')
gcd_res, gcd_time = measure_time(gcd_long, A,B,index=0)
print(f'GCD = {to_hex(gcd_res)} ({gcd_time:.6f}s)')

lcm_res, lcm_time = measure_time(lcm_long, A,B)
print(f'LCM = {to_hex(lcm_res)} ({lcm_time:.6f}s)')

mod_sum, t = measure_time(add_mod,A,B,M)
print(f'(A+B)modM = {to_hex(mod_sum)} ({t:.6f}s)')

mod_sub, t = measure_time(sub_mod,A,B,M)
print(f'(A-B)modM = {to_hex(mod_sub)} ({t:.6f}s)')

mod_mul, t = measure_time(mul_mod,A,B,M)
print(f'(A*B)modM = {to_hex(mod_mul)} ({t:.6f}s)')

mod_sq, t = measure_time(sq_mod,A,M)
print(f'(A^2)modM = {to_hex(mod_sq)} ({t:.6f}s)')

mod_pow, t = measure_time(pow_mod,A,B,M)
print(f'(A^B)modM = {to_hex(mod_pow)} ({t:.6f}s)')
