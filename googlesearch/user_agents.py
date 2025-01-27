import random

def get_useragent():
    """
    Generates a random user agent string for Lynx browser with improved variation
    """
    lynx_versions = [
        f"Lynx/{random.randint(2, 3)}.{random.randint(8, 9)}.{random.randint(0, 2)}",
        f"Lynx/{random.randint(2, 3)}.{random.randint(8, 9)}.{random.randint(0, 2)}-ssl",
        f"Lynx/{random.randint(2, 3)}.{random.randint(8, 9)}.{random.randint(0, 2)}-libssl"
    ]
    
    libwww_versions = [
        f"libwww-FM/{random.randint(2, 3)}.{random.randint(13, 15)}",
        f"libwww-FM/{random.randint(2, 3)}.{random.randint(13, 15)}-pre.{random.randint(1,5)}"
    ]
    
    ssl_versions = [
        f"SSL-MM/{random.randint(1, 2)}.{random.randint(3, 5)}",
        f"OpenSSL/{random.randint(1, 3)}.{random.randint(0, 4)}.{random.randint(0, 9)}"
    ]

    return f"{random.choice(lynx_versions)} {random.choice(libwww_versions)} {random.choice(ssl_versions)}"
