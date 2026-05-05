import random

def random_bits_to_hex(bits: int) -> str:
    if bits <= 0:
        raise ValueError("додат")

    number = random.getrandbits(bits)
    return hex(number)[2:]  
print(random_bits_to_hex(2048))    

