"""Calcolatrice scientifica a pulsanti. AST chiuso, niente eval libero."""

from __future__ import annotations

import ast
import math
import operator
from typing import Any

_OPS: dict[type, Any] = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}

_TRIG = frozenset({"sin", "cos", "tan", "asin", "acos", "atan"})
_FUNS: dict[str, Any] = {
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "asin": math.asin,
    "acos": math.acos,
    "atan": math.atan,
    "sqrt": math.sqrt,
    "ln": math.log,
    "log": math.log10,
    "exp": math.exp,
    "abs": abs,
    "fact": math.factorial,
}
_CONST = {"pi": math.pi, "e": math.e}

_BUTTONS = {
    "add": "+",
    "sub": "-",
    "mul": "*",
    "div": "/",
    "dot": ".",
    "lp": "(",
    "rp": ")",
    "pow": "**",
    "pi": "pi",
    "e": "e",
    "sin": "sin(",
    "cos": "cos(",
    "tan": "tan(",
    "asin": "asin(",
    "acos": "acos(",
    "atan": "atan(",
    "sqrt": "sqrt(",
    "ln": "ln(",
    "log": "log(",
    "exp": "exp(",
    "fact": "fact(",
    "inv": "1/(",
}

CONV_GROUPS: dict[str, tuple[str, tuple[str, ...]]] = {
    "len": (
        "Lunghezza",
        ("km_mi", "mi_km", "m_ft", "ft_m", "cm_in", "in_cm", "m_yd", "yd_m"),
    ),
    "mass": ("Massa", ("kg_lb", "lb_kg", "g_oz", "oz_g")),
    "temp": ("Temperatura", ("c_f", "f_c", "c_k", "k_c")),
    "spd": ("Velocità", ("kmh_mph", "mph_kmh", "ms_kmh", "kmh_ms")),
    "vol": ("Volume", ("l_gal", "gal_l", "ml_l", "l_ml")),
    "ang": ("Angoli", ("deg_rad", "rad_deg")),
    "sky": ("Cielo", ("au_km", "km_au", "ly_km", "km_ly")),
    "time": ("Tempo", ("h_min", "min_h", "d_h", "h_d")),
}

CONVERSIONS: dict[str, tuple[str, str, float, float]] = {
    "km_mi": ("km", "miglia", 0.621371, 0.0),
    "mi_km": ("miglia", "km", 1.609344, 0.0),
    "m_ft": ("m", "piedi", 3.280839895, 0.0),
    "ft_m": ("piedi", "m", 0.3048, 0.0),
    "cm_in": ("cm", "pollici", 1 / 2.54, 0.0),
    "in_cm": ("pollici", "cm", 2.54, 0.0),
    "m_yd": ("m", "iarde", 1.0936132983, 0.0),
    "yd_m": ("iarde", "m", 0.9144, 0.0),
    "kg_lb": ("kg", "libbre", 2.2046226218, 0.0),
    "lb_kg": ("libbre", "kg", 0.45359237, 0.0),
    "g_oz": ("g", "once", 1 / 28.349523125, 0.0),
    "oz_g": ("once", "g", 28.349523125, 0.0),
    "c_f": ("°C", "°F", 1.8, 32.0),
    "f_c": ("°F", "°C", 5.0 / 9.0, -32.0 * 5.0 / 9.0),
    "c_k": ("°C", "K", 1.0, 273.15),
    "k_c": ("K", "°C", 1.0, -273.15),
    "kmh_mph": ("km/h", "mph", 0.621371, 0.0),
    "mph_kmh": ("mph", "km/h", 1.609344, 0.0),
    "ms_kmh": ("m/s", "km/h", 3.6, 0.0),
    "kmh_ms": ("km/h", "m/s", 1 / 3.6, 0.0),
    "l_gal": ("l", "gal (US)", 0.2641720524, 0.0),
    "gal_l": ("gal (US)", "l", 3.785411784, 0.0),
    "ml_l": ("ml", "l", 0.001, 0.0),
    "l_ml": ("l", "ml", 1000.0, 0.0),
    "deg_rad": ("°", "rad", math.pi / 180.0, 0.0),
    "rad_deg": ("rad", "°", 180.0 / math.pi, 0.0),
    "au_km": ("UA", "km", 149597870.7, 0.0),
    "km_au": ("km", "UA", 1 / 149597870.7, 0.0),
    "ly_km": ("a.l.", "km", 9.4607304725808e12, 0.0),
    "km_ly": ("km", "a.l.", 1 / 9.4607304725808e12, 0.0),
    "h_min": ("ore", "min", 60.0, 0.0),
    "min_h": ("min", "ore", 1 / 60.0, 0.0),
    "d_h": ("giorni", "ore", 24.0, 0.0),
    "h_d": ("ore", "giorni", 1 / 24.0, 0.0),
}


def normalize_expr(expr: str) -> str:
    text = str(expr or "")
    for src, dst in (
        ("×", "*"),
        ("÷", "/"),
        ("−", "-"),
        (",", "."),
        ("π", "pi"),
        ("^", "**"),
        (" ", ""),
    ):
        text = text.replace(src, dst)
    while "****" in text:
        text = text.replace("****", "**")
    return text[:96]


def _eval_node(node: ast.AST, *, deg: bool) -> float:
    if isinstance(node, ast.Expression):
        return _eval_node(node.body, deg=deg)
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return float(node.value)
    if isinstance(node, ast.Name) and node.id in _CONST:
        return float(_CONST[node.id])
    if isinstance(node, ast.UnaryOp) and type(node.op) in _OPS:
        return float(_OPS[type(node.op)](_eval_node(node.operand, deg=deg)))
    if isinstance(node, ast.BinOp) and type(node.op) in _OPS:
        left = _eval_node(node.left, deg=deg)
        right = _eval_node(node.right, deg=deg)
        if isinstance(node.op, ast.Div) and right == 0:
            raise ZeroDivisionError("zero")
        return float(_OPS[type(node.op)](left, right))
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in _FUNS:
        if len(node.args) != 1 or node.keywords:
            raise ValueError("espressione non valida")
        name = node.func.id
        value = _eval_node(node.args[0], deg=deg)
        if name == "fact":
            if value < 0 or value != int(value) or value > 20:
                raise ValueError("fattoriale")
            return float(math.factorial(int(value)))
        if deg and name in {"sin", "cos", "tan"}:
            value = math.radians(value)
        out = float(_FUNS[name](value))
        if deg and name in {"asin", "acos", "atan"}:
            out = math.degrees(out)
        if not math.isfinite(out):
            raise ValueError("non finito")
        return out
    raise ValueError("espressione non valida")


def evaluate(expr: str, *, deg: bool = True) -> float:
    cleaned = normalize_expr(expr)
    if not cleaned:
        raise ValueError("vuota")
    tree = ast.parse(cleaned, mode="eval")
    for child in ast.walk(tree):
        if isinstance(child, ast.Attribute | ast.Subscript):
            raise ValueError("espressione non valida")
        if isinstance(child, ast.Name) and child.id not in _CONST and child.id not in _FUNS:
            raise ValueError("espressione non valida")
        if isinstance(child, ast.Call) and (
            not isinstance(child.func, ast.Name) or child.func.id not in _FUNS
        ):
            raise ValueError("espressione non valida")
    value = _eval_node(tree, deg=deg)
    if abs(value) > 1e16:
        raise ValueError("troppo grande")
    return value


def format_number(value: float) -> str:
    if not math.isfinite(value):
        return "—"
    if abs(value) >= 1e8 or (0 < abs(value) < 1e-4):
        return f"{value:.8g}"
    if abs(value - round(value)) < 1e-12:
        return str(int(round(value)))
    text = f"{value:.10f}".rstrip("0").rstrip(".")
    return text or "0"


def apply_key(
    expr: str,
    key: str,
    *,
    just_eq: bool = False,
    deg: bool = True,
) -> tuple[str, bool, str | None]:
    """Applica un tasto. Ritorna (espressione, just_eq, errore)."""
    current = normalize_expr(expr)
    if key == "c":
        return "", False, None
    if key == "bs":
        return current[:-1], False, None
    if key == "eq":
        try:
            return format_number(evaluate(current, deg=deg)), True, None
        except ZeroDivisionError:
            return current, False, "Non si divide per zero."
        except Exception:
            return current, False, "Espressione non valida."
    token = _BUTTONS.get(key, key if key.isdigit() else "")
    if not token:
        return current, just_eq, None
    starts_fresh = token[:1].isdigit() or token in {"pi", "e"} or token.endswith("(")
    if just_eq and starts_fresh and not token.endswith("("):
        if token == ".":
            return "0.", False, None
        return token, False, None
    if just_eq and token.endswith("("):
        current = ""
    if token == "." and (not current or current[-1] in "+-*/("):
        token = "0."
    next_expr = normalize_expr(current + token)
    return next_expr, False, None


def percent_of(part: float, whole: float) -> float:
    return whole * part / 100.0


def percent_ratio(value: float, whole: float) -> float:
    if whole == 0:
        raise ZeroDivisionError("zero")
    return value * 100.0 / whole


def percent_change(value: float, pct: float, *, up: bool) -> float:
    delta = value * pct / 100.0
    return value + delta if up else value - delta


def parse_percent_request(text: str) -> tuple[str, float] | None:
    return None


def convert_value(kind: str, value: float) -> tuple[float, str, str]:
    if kind not in CONVERSIONS:
        raise ValueError("conversione sconosciuta")
    src, dst, mul, add = CONVERSIONS[kind]
    return value * mul + add, src, dst


def conversion_label(kind: str) -> str:
    if kind not in CONVERSIONS:
        return ""
    src, dst, _mul, _add = CONVERSIONS[kind]
    return f"{src} → {dst}"
