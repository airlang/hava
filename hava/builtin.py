from .bytecode import HavaBuiltinFunction

def hava_type(value):
    if isinstance(value, bool):
        return "bool"
    if isinstance(value, int):
        return "number"
    if isinstance(value, float):
        return "number"
    if isinstance(value, str):
        return "string"
    if value is None:
        return "none"
    return type(value).__name__

def hava_append(array, value):
    if not isinstance(array, list):
        raise TypeError("append sadece array üzerinde kullanılabilir.")
    array.append(value)
    return None

BUILTINS = {
    "print": HavaBuiltinFunction("print", print, 1),
    "yaz": HavaBuiltinFunction("yaz", print, 1),

    "len": HavaBuiltinFunction("len", len, 1),
    "uzunluk": HavaBuiltinFunction("uzunluk", len, 1),

    "append": HavaBuiltinFunction("append", hava_append, 2),
    "ekle": HavaBuiltinFunction("ekle", hava_append, 2),

    "type": HavaBuiltinFunction("type", hava_type, 1),
    "tür": HavaBuiltinFunction("tür", hava_type, 1),

    "str": HavaBuiltinFunction("str", str, 1),
    "yazı": HavaBuiltinFunction("yazı", str, 1),

    "int": HavaBuiltinFunction("int", int, 1),
    "sayı": HavaBuiltinFunction("sayı", int, 1),

    "float": HavaBuiltinFunction("float", float, 1),
    "ondalık": HavaBuiltinFunction("ondalık", float, 1),

    "abs": HavaBuiltinFunction("abs", abs, 1),
    "mutlak": HavaBuiltinFunction("mutlak", abs, 1),

    "round": HavaBuiltinFunction("round", round, 1),
    "yuvarla": HavaBuiltinFunction("yuvarla", round, 1),

    "max": HavaBuiltinFunction("max", max, None),
    "min": HavaBuiltinFunction("min", min, None),

    "pow": HavaBuiltinFunction("pow", pow, 2),
    "üs": HavaBuiltinFunction("üs", pow, 2),
}