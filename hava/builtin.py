from pathlib import Path

from .bytecode import HavaBuiltinFunction
from .errors import HavaRuntimeError


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

def hava_pop(target, key):
    if not isinstance(target, (list, dict)):
        raise HavaRuntimeError("pop sadece array veya dict üzerinde kullanılabilir.")
    if isinstance(target, list):
        if type(key) is not int:
            raise HavaRuntimeError("Array index değeri integer olmalı.")
        try:
            return target.pop(key)
        except IndexError:
            raise HavaRuntimeError("Array index sınır dışında.")
    if isinstance(target, dict):
        try:
            return target.pop(key)
        except KeyError:
            raise HavaRuntimeError("Dict içinde bu key bulunamadı.")
        except TypeError:
            raise HavaRuntimeError("Dict key değeri geçersiz.")
    return None

def hava_read_file(path):
    if not isinstance(path, str):
        raise HavaRuntimeError("read_file path değeri string olmalı.")
    try:
        return Path(path).read_text(encoding="utf-8")
    except FileNotFoundError:
        raise HavaRuntimeError(f"Dosya bulunamadı: {path}")
    except OSError as e:
        raise HavaRuntimeError(f"Dosya okunamadı: {e}")

def hava_write_file(path, content):
    if not isinstance(path, str):
        raise HavaRuntimeError("write_file path değeri string olmalı.")
    if not isinstance(content, str):
        raise HavaRuntimeError("write_file content değeri string olmalı.")
    try:
        Path(path).write_text(content, encoding="utf-8")
    except OSError as e:
        raise HavaRuntimeError(f"Dosya yazılamadı: {e}")
    return None

def hava_file_exists(path):
    if not isinstance(path, str):
        raise HavaRuntimeError("file_exists path değeri string olmalı.")
    return Path(path).exists()

BUILTINS = {
    "print": HavaBuiltinFunction("print", print, 1),
    "yaz": HavaBuiltinFunction("yaz", print, 1),

    "len": HavaBuiltinFunction("len", len, 1),
    "uzunluk": HavaBuiltinFunction("uzunluk", len, 1),

    "append": HavaBuiltinFunction("append", hava_append, 2),
    "ekle": HavaBuiltinFunction("ekle", hava_append, 2),

    "pop": HavaBuiltinFunction("pop", hava_pop, 2),
    "çıkar": HavaBuiltinFunction("çıkar", hava_pop, 2),
    "cikar": HavaBuiltinFunction("cikar", hava_pop, 2),

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

    "read_file": HavaBuiltinFunction("read_file", hava_read_file, 1),
    "dosya_oku": HavaBuiltinFunction("dosya_oku", hava_read_file, 1),

    "write_file": HavaBuiltinFunction("write_file", hava_write_file, 2),
    "dosya_yaz": HavaBuiltinFunction("dosya_yaz", hava_write_file, 2),

    "file_exists": HavaBuiltinFunction("file_exists", hava_file_exists, 1),
    "dosya_var_mi": HavaBuiltinFunction("dosya_var_mi", hava_file_exists, 1),
}