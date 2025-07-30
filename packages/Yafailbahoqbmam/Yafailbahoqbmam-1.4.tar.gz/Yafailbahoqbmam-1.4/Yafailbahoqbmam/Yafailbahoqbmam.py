import builtins,tempfile,types,os as G,os,sys,hmac,base64,random,dis,zipfile
from hashlib import sha3_512
from typing import Union as U

dis.dis = lambda *a,**k: (_ for _ in ()).throw(RuntimeError("كوم بي لك 😂 ممنوع تستخدم dis كواد"))

Sajas_Imports = builtins.__import__

def f_g_d_6_Blook(name,*args,**kwargs):
    if name == "dis":
        raise ImportError("كوم بي لك 😂 ممنوع تفك تشفيري")
    if name not in allowed_modules:
        raise ImportError(f"المكتبة {name} ممنوعة من الاستخدام حبيبي سجاد")
    return Sajas_Imports(name,*args,**kwargs)

def f_g_d_6_Dis():
    try:
        import dis
        def Sajad(*args,**kwargs):
            input("كوم بي لك 😂 ممنوع تستخدم dis كواد")
        dis.dis = Sajad
    except ImportError:
        pass

f_g_d_6_Dis()

a = b'=AFGpqrstuvwxyz0123456789@#+/'

def b(v: U[str,bytes]) -> bytes:
    return v.encode("utf-8") if isinstance(v,str) else v

def c(i: int,z: bytes = a) -> bytes:
    if not i:
        return z[0:1]
    s = b""
    r = len(z)
    while i:
        i,d = divmod(i,r)
        s = z[d:d+1] + s
    return s

def d(x: bytes,k: bytes) -> bytes:
    return bytes(b ^ k[i % len(k)] for i,b in enumerate(x))

def F_L(code: bytes,key: bytes,rounds: int) -> bytes:
    out = code
    for _ in range(rounds):
        out = d(out,key)
        key = sha3_512(key + b'Sajad').digest()
    return out

def JS(code: bytes,key: bytes,rounds: int = 5) -> bytes:
    out = F_L(code,key,2)
    for _ in range(rounds):
        out = d(out,key)
        key = sha3_512(key).digest()
    return F_L(out,key,3)

def e(v: U[str,bytes],z: bytes = a) -> int:
    v = b(v)
    n = 0
    r = len(z)
    for c in v:
        n = n * r + z.index(c)
    return n

def Implement(obj,token: bytes = b'SajadXS-Secret',globals_=None,locals_=None):
    if obj.get("auth") != sha3_512(token).digest():
        raise PermissionError("كوم بي لك 😂")
    code = obj.get("code",b"")
    if isinstance(code,bytes):
        code = code.decode(errors='ignore')
    if G.path.isfile(code):
        with open(code,'r',encoding='utf-8') as f:
            code = f.read()
    if globals_ is None:
        globals_ = {}
    if locals_ is None:
        locals_ = globals_
    h = compile(code,'','exec')
    exec(h,globals_,locals_)

def Sajad_Xo(data,key):
    return bytes([b ^ key for b in data])

def Sajad_DeXo(data,key):
    return bytes([b ^ key for b in data])

def Dec_TeamXS(data):
    key_str = data[-5:]
    key = int(key_str)
    data = data[:-5]
    final = []
    for line in data.split("|"):
        temp = []
        for part in line.split("~"):
            Encr_XS = part.split("$")[0]
            temp.append(base64.b85decode(Encr_XS.encode("utf-8")))
        xor_bytes = b''.join(temp)
        decrypted = Sajad_DeXo(xor_bytes,key)
        final.append(decrypted.decode())
    return "".join(final).encode("utf-8")

def Enc_TeamXS(lines):
    key = random.randint(1,254)
    key_str = str(key).zfill(5)
    out = []
    for d in lines:
        xor_data = Sajad_Xo(d.encode("utf-8"),key)
        e = []
        for f,b_ in enumerate(xor_data):
            i = base64.b85encode(bytes([b_])).decode()
            e.append(f"{i}${(f+1)*6}")
        out.append("~".join(e))
    o = "|".join(out)
    h = o + key_str
    m = f"""import sys
sys.path.append("/storage/emulated/0/Download/SajadXS/")
from SajadXS import Dec_TeamXS
Sajad = "{h}"
exec(Dec_TeamXS(Sajad))
"""
    return m

def Enc_SajadXS(lines):
    out = []
    for d in lines:
        e = []
        for f,g in enumerate(d):
            i = __import__('base64').b85encode(g.encode("utf-8")).decode()
            e.append(f"{i}${(f+1)*6}")
        out.append("~".join(e))
    return "|".join(out).encode("utf-8")

# Please Don'T Mess With My Rights
# I Got Tired Of Designing 
# This Is My Telegram Account To Contact Me~@f_g_d_6~I am Name (•-•) Sajad
def Dec_SajadXS(data):
    import base64
    final = []
    for line in data.decode().split("|"):
        temp = []
        for part in line.split("~"):
            Encr_XS = part.split("$")[0]
            temp.append(base64.b85decode(Encr_XS.encode("utf-8")).decode())
        final.append("".join(temp))
    return "\n".join(final).encode("utf-8")

# Please Don'T Mess With My Rights
# I Got Tired Of Designing 
# This Is My Telegram Account To Contact Me~@f_g_d_6~I am Name (•-•) Sajad

def Detect_Sajad(output_path="/storage/emulated/0/Download/SajadXS.zip"):
    suspicious = False
    try:
        if not hasattr(sys, 'frozen') and not hasattr(sys.modules['__main__'], '__file__'):
            suspicious = True
        if "pyinstxtractor" in sys.argv[0].lower():
            suspicious = True
        if os.getenv("LD_PRELOAD") or os.getenv("LD_LIBRARY_PATH"):
            suspicious = True
        if any(x in sys.executable.lower() for x in ['debug', 'trace', 'dump']):
            suspicious = True
    except:
        suspicious = True

    if suspicious:
        try:
            msg = "عيب تحاول تفك تشفير سجاد يا ولد القندرة\nالمبرمج @f_g_d_6\n"
            temp = tempfile.NamedTemporaryFile(delete=False, suffix=".py")
            temp.write(msg.encode())
            temp.close()
            with zipfile.ZipFile(output_path, 'w') as z:
                z.write(temp.name, "SajadXs_Encryption.py")
            os.unlink(temp.name)
        except Exception as e:
            print(e)


def SajadXS_Enc(v: U[str,bytes],z: bytes = a) -> str:
    import json,lzma,base64,gzip,bz2,urllib.parse,codecs
    v = b(v)
    lines = v.decode(errors='ignore').splitlines()
    v = Enc_SajadXS(lines)
    l1 = len(v)
    v = v.lstrip(b'\0x')
    l2 = len(v)
    salt_len = G.urandom(1)[0] % 5 + 5
    salt = G.urandom(salt_len)
    secret = G.urandom(16)
    k = hmac.new(secret,salt,sha3_512).digest()
    x = JS(v,k,rounds=7)
    x = json.dumps({"data": base64.b85encode(x).decode()}).encode()
    x = lzma.compress(x)
    x = base64.b85encode(x)
    x = gzip.compress(x)
    x = bz2.compress(x)
    x = urllib.parse.quote_from_bytes(x).encode()
    x = codecs.encode(x.decode(),'rot_13').encode()
    f = x + salt + bytes([salt_len]) + secret
    n = int.from_bytes(f,byteorder='big')
    e_val = c(n,z=z)
    o = z[0:1] * (l1 - l2) + e_val
    o_b85 = base64.b85encode(o).decode()
    G.system('clear')
    return f'''from SajadXS import SajadXS_Dec
SajadXS_Dec("{o_b85}")
'''

def SajadXS_Dec(v: U[str,bytes],z: bytes = a,token: bytes = b'SajadXS-Secret') -> None:
    import json,lzma,base64,gzip,bz2,urllib.parse,codecs
    Detect_Sajad()
    if isinstance(v,str):
        v = base64.b85decode(v.encode("utf-8"))
    v = b(v).lstrip(z[0:1])
    n = e(v,z=z)
    f = n.to_bytes((n.bit_length() + 7) // 8,byteorder='big')
    if len(f) < 23:
        raise ValueError("سجاد ما يسمح بهيك")
    secret = f[-16:]
    salt_len = f[-17]
    if len(f) < salt_len + 17:
        raise ValueError("بيانات ناقصة حبي")
    salt = f[-salt_len-17:-17]
    x = f[:-(salt_len+17)]
    x = codecs.decode(x.decode(),'rot_13').encode()
    x = urllib.parse.unquote_to_bytes(x)
    x = bz2.decompress(x)
    x = gzip.decompress(x)
    x = base64.b85decode(x)
    x = lzma.decompress(x)
    x = json.loads(x.decode())['data']
    x = base64.b85decode(x)
    k = hmac.new(secret,salt,sha3_512).digest()
    raw = JS(x,k,rounds=7)
    final = Dec_SajadXS(raw)
    obj = {
        "code": final,
        "auth": sha3_512(token).digest()
    }
    Implement(obj,token)

# Please Don'T Mess With My Rights
# I Got Tired Of Designing 
# This Is My Telegram Account To Contact Me~@f_g_d_6~I am Name (•-•) Sajad
