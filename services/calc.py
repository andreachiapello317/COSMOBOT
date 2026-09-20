"""Calcolatrice a pulsanti. Solo aritmetica, niente eval libero."""

from __future__ import annotations

import ast
import operator
from typing import Any

_OPS: dict[type, Any] = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Mod: operator.mod,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}

_BUTTONS = {
    "add": "+",
    "sub": "-",
    "mul": "*",
    "div": "/",
    "dot": ".",
    "lp": "(",
    "rp": ")",
}


def normalize_expr(expr: str) -> str:
    text = (
        str(expr or "")
        .replace("×", "*")
        .replace("÷", "/")
        .replace("−", "-")
        .replace(",", ".")
        .replace(" ", "")
    )
    return text[:48]


def _eval_node(node: ast.AST) -> float:
    if isinstance(node, ast.Expression):
        return _eval_node(node.body)
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return float(node.value)
    if isinstance(node, ast.UnaryOp) and type(node.op) in _OPS:
        return float(_OPS[type(node.op)](_eval_node(node.operand)))
    if isinstance(node, ast.BinOp) and type(node.op) in _OPS:
        left = _eval_node(node.left)
        right = _eval_node(node.right)
        if isinstance(node.op, ast.Div) and right == 0:
            raise ZeroDivisionError("zero")
        return float(_OPS[type(node.op)](left, right))
    raise ValueError("espressione non valida")


def evaluate(expr: str) -> float:
    cleaned = normalize_expr(expr)
    if not cleaned:
        raise ValueError("vuota")
    tree = ast.parse(cleaned, mode="eval")
    for child in ast.walk(tree):
        if isinstance(child, ast.Call | ast.Attribute | ast.Name | ast.Subscript):
            raise ValueError("espressione non valida")
    value = _eval_node(tree)
    if abs(value) > 1e12:
        raise ValueError("troppo grande")
    return value


def format_number(value: float) -> str:
    if abs(value - round(value)) < 1e-12:
        return str(int(round(value)))
    text = f"{value:.10f}".rstrip("0").rstrip(".")
    return text or "0"


def apply_key(expr: str, key: str, *, just_eq: bool = False) -> tuple[str, bool, str | None]:
    """Applica un tasto. Ritorna (espressione, just_eq, errore)."""
    current = normalize_expr(expr)
    if key == "c":
        return "", False, None
    if key == "bs":
        return current[:-1], False, None
    if key == "eq":
        try:
            return format_number(evaluate(current)), True, None
        except ZeroDivisionError:
            return current, False, "Non si divide per zero."
        except Exception:
            return current, False, "Espressione non valida."
    token = _BUTTONS.get(key, key if key.isdigit() else "")
    if not token:
        return current, just_eq, None
    if just_eq and token.isdigit():
        return token, False, None
    if just_eq and token == ".":
        return "0.", False, None
    if token == "." and (not current or current[-1] in "+-*/("):
        token = "0."
    next_expr = normalize_expr(current + token)
    return next_expr, False, None
