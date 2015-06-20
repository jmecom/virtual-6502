def check_bit(val, idx):
    """ Checks if a specific bit in a number is set """
    return val & (1 << idx)

def set_bit(val, idx):
    """ Sets a specific bit in a number """
    return val | (1 << idx)

def clear_bit(val, idx):
    """ Clears a specific bit in a number """
    return val & ~(1 << idx)

def copy_bit(a, b, idx):
    """ Copies the specified bit from a to b """
    if check_bit(a, idx):
        return set_bit(b, idx)
    else:
        return clear_bit(b, idx)
