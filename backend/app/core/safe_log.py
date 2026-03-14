"""
安全控制台输出，避免在 Windows GBK 等环境下因 emoji/Unicode 导致 UnicodeEncodeError。
所有 print 均使用 ASCII 安全回退，确保不因编码问题抛出异常。
"""
import sys


def _safe_str(obj: object) -> str:
    """将对象转为字符串，若含无法编码的字符则回退为 ASCII 安全形式"""
    try:
        s = str(obj)
        if sys.stdout.encoding:
            s.encode(sys.stdout.encoding)
        return s
    except (UnicodeEncodeError, AttributeError):
        return repr(obj).encode("ascii", "replace").decode("ascii")


def safe_print(*args, **kwargs) -> None:
    """与 print 行为一致，但保证在 GBK 等环境下不抛出 UnicodeEncodeError"""
    try:
        print(*args, **kwargs)
    except UnicodeEncodeError:
        sep = kwargs.get("sep", " ")
        end = kwargs.get("end", "\n")
        file = kwargs.get("file", sys.stdout)
        safe_parts = [_safe_str(a) for a in args]
        file.write(sep.join(safe_parts) + end)
        if kwargs.get("flush", False):
            file.flush()
