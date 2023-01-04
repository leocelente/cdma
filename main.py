from itertools import islice
from collections.abc import Iterable

# Type annotations
Byte = int
Bit = int
Chip = int

def to_bin(n: Byte) -> list[Bit]:
    '''Converts from number to list of bits'''
    significant = [int(c) for c in bin(n)[2:]]
    bits = [0] * (8 - len(significant))
    bits.extend(significant)
    return bits

# string -> bytes -> bits -> chips

def to_bytes(text: str) -> Iterable[Byte]:
    '''Converts from string to list to stream of bytes'''
    for c in text.encode('utf-8'):
        yield Byte(c)


def to_bits(data: Iterable[Byte]) -> Iterable[Bit]:
    '''Converts from bytes to stream of bits'''
    for byte in data:
        for i in to_bin(byte):
            yield i


def to_chips(bits: Iterable[Bit], code: Byte) -> Iterable[Chip]:
    '''Converts from bits to encoded chips'''
    for bit in bits:
        for chip in to_bin(code):
            chip = -1 if chip == 0 else 1
            if bit > 0:
                yield chip
            else:
                yield -chip


def mix(*chips) -> Iterable[Chip]:
    '''Creates superposition of chips'''
    for chip in zip(*chips):
        yield sum(chip)


# chips -> correlation -> bits -> ? bytes

def get_correlation(chips: Iterable[Chip], code: Byte) -> Iterable[int]:
    '''Correlates chips using code, streams correlation of whole bit'''
    code_bits = to_bin(code)
    it = iter(chips)
    while (window := list(islice(it, 8))):
        bit_correlation = 0
        for i in range(8):
            bit_correlation += window[i] * code_bits[i]
        yield bit_correlation


def get_bits(correlations: Iterable[int]) -> Iterable[tuple[Bit, int]]:
    '''Detects bit and forwards its correlation'''
    for bit_correlation in correlations:
        bit = 1 if bit_correlation > 0 else 0
        yield (bit, bit_correlation)


def get_bytes(bits: Iterable[tuple[Bit, int]], threshold: int = 10) -> Iterable[Byte]:
    '''Checks correlation of bits, if above a threshold streams as a byte'''
    it = iter(bits)
    while (window := list(islice(it, 8))):
        byte_correlation = sum(map(lambda x: x[1]**2, window))
        byte = sum([window[8-i-1][0] * 2**i for i in range(8)])
        if byte_correlation > threshold:
            yield byte


def get_str(data: Iterable[Byte]) -> str:
    '''Joins stream of bytes in a string'''
    return ''.join(map(chr, data))


if __name__ == "__main__":
    u1 = to_chips(to_bits(to_bytes("Zenith   ")), 0b01101110)
    u2 = to_chips(to_bits(to_bytes("Aerospace")), 0b10101101)
    u3 = to_chips(to_bits(to_bytes("UUUUUUUUU")), 0b11010001)
    out = list(mix(u1, u2, u3))
    
    from numpy.random import normal
    noise = normal(0, 0.3, len(out))
    out = list(mix(out, noise))

    u1 = get_str(get_bytes(get_bits(get_correlation(out, 0b01101110))))
    u2 = get_str(get_bytes(get_bits(get_correlation(out, 0b10101101))))
    u3 = get_str(get_bytes(get_bits(get_correlation(out, 0b11010001))))
    print(f"u1: {u1}\nu2: {u2}\nu3: {u3}")

    from matplotlib import pyplot as plt
    sample_correlation = list(get_bits(get_correlation(out, 0b01101110)))
    plt.figure()
    plt.step(range(len(sample_correlation)), sample_correlation, where='mid')
    plt.grid()
    plt.show()