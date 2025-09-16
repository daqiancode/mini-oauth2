import random,string



def rand_str(n:int, enable_upper:bool=True)->str:
    if enable_upper:
        return ''.join(random.choices(string.ascii_lowercase + string.digits + string.ascii_uppercase, k=n))
    else:
        return ''.join(random.choices(string.ascii_lowercase + string.digits, k=n))
    
    
def rand_num(n:int)->str:
    return ''.join(random.choices(string.digits, k=n))