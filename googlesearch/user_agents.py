import random

def get_useragent():
    """
    Generates a random user agent string mimicking Lynx browser to bypass Google's JS detection
    """
    lynx_versions = [
        "2.8.9rel.1",
        "2.9.0dev.4",
        "2.8.8rel.2",
        "2.8.9pre.1",
        "2.9.0pre.5"
    ]
    
    libwww_versions = [
        "2.14",
        "2.15",
        "3.14",
        "3.15"
    ]
    
    ssl_versions = [
        "1.4",
        "1.5",
        "2.3",
        "2.4"
    ]
    
    openssl_versions = [
        "1.1.1",
        "1.1.2",
        "3.0.1",
        "3.0.2"
    ]

    lynx_version = f"Lynx/{random.choice(lynx_versions)}"
    libwww_version = f"libwww-FM/{random.choice(libwww_versions)}"
    ssl_mm_version = f"SSL-MM/{random.choice(ssl_versions)}"
    openssl_version = f"OpenSSL/{random.choice(openssl_versions)}"
    
    return f"{lynx_version} {libwww_version} {ssl_mm_version} {openssl_version}"
