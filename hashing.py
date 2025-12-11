import hashlib



def hashed(text: str) -> str: 
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


print("admin: ", hashed("admin"))
print("tech: ", hashed("tech"))
