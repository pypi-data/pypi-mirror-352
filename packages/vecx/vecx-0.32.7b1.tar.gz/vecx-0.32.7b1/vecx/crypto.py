
def get_checksum(key:str)->int:
    # Convert last two characters of key to integer
    return int(key[-2:], 16)