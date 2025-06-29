import re

def validar_rut(rut: str, dv: str) -> bool:
    rut = rut.replace(".", "").replace("-", "")
    if not rut.isdigit():
        return False
    if not dv or len(dv) != 1:
        return False
    dv = dv.upper()
    
    suma = 0
    multiplo = 2
    for c in reversed(rut):
        suma += int(c) * multiplo
        multiplo = multiplo + 1 if multiplo < 7 else 2
    
    dv_esperado = 11 - (suma % 11)
    if dv_esperado == 11:
        dv_esperado = '0'
    elif dv_esperado == 10:
        dv_esperado = 'K'
    else:
        dv_esperado = str(dv_esperado)
    
    return dv == dv_esperado

def validar_telefono(telefono: str) -> bool:
    return len(telefono) == 9 and telefono.startswith("9") and telefono.isdigit()

def validar_email(email: str) -> bool:
    patron = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return bool(re.match(patron, email))