def validar_rut(rut):
    """Valida que el RUT tenga el formato correcto"""
    # Eliminar puntos y guión
    rut = rut.replace(".", "").replace("-", "")
    
    # Verificar largo mínimo
    if len(rut) < 8:
        return False
        
    # Verificar que termina en número o 'K'
    if not (rut[-1].isdigit() or rut[-1].upper() == 'K'):
        return False
        
    # Verificar que el resto son números
    return rut[:-1].isdigit()

def validar_texto(texto, min_longitud=1, max_longitud=50):
    """Valida que el texto tenga una longitud dentro del rango especificado"""
    return min_longitud <= len(texto) <= max_longitud

def validar_numero(texto):
    """Valida que el texto sea un número"""
    try:
        float(texto)
        return True
    except ValueError:
        return False

def validar_email(email):
    """Valida que el email tenga un formato básico correcto"""
    import re
    patron = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(patron, email))

def validar_telefono(telefono):
    """Valida que el teléfono tenga un formato correcto"""
    return len(telefono) >= 9 and telefono.isdigit()

def validar_precio(precio):
    """Valida que el precio sea un número positivo"""
    try:
        valor = float(precio)
        return valor > 0
    except ValueError:
        return False