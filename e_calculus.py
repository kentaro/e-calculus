"""
E-Calculus: A homoiconic language built on E(x, y) = exp(x) - ln(y).

Every expression is a binary tree: leaves are `1`, internal nodes are `E`.
With quote/match/eval, this tree becomes both code and data — a Lisp
that grew from a single mathematical operator.
"""

from __future__ import annotations

import math
import readline
import sys
from dataclasses import dataclass
from typing import Union


# ── AST ──────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class Num:
    value: float

    def __repr__(self) -> str:
        if self.value == int(self.value):
            return str(int(self.value))
        return f"{self.value:.10g}"


@dataclass(frozen=True)
class Sym:
    name: str

    def __repr__(self) -> str:
        return self.name


@dataclass(frozen=True)
class List:
    items: tuple

    def __repr__(self) -> str:
        return "(" + " ".join(repr(i) for i in self.items) + ")"


Expr = Union[Num, Sym, List]


# ── Values ───────────────────────────────────────────────────────────

@dataclass(frozen=True)
class VNum:
    """A numeric value (the result of evaluating an E-expression)."""
    value: float

    def __repr__(self) -> str:
        if self.value == int(self.value) and abs(self.value) < 1e15:
            return str(int(self.value))
        return f"{self.value:.10g}"


@dataclass(frozen=True)
class VTree:
    """A quoted E-tree: either a Leaf(1) or a Node(left, right)."""
    tag: str  # "leaf" or "node"
    children: tuple = ()

    def __repr__(self) -> str:
        if self.tag == "leaf":
            return "1"
        l, r = self.children
        return f"(E {l!r} {r!r})"


@dataclass(frozen=True)
class VFn:
    """A closure (user-defined function)."""
    params: tuple[str, ...]
    body: Expr
    env: dict

    def __repr__(self) -> str:
        return f"(fn ({' '.join(self.params)}) ...)"


@dataclass(frozen=True)
class VBuiltin:
    """A built-in function."""
    name: str
    func: object

    def __repr__(self) -> str:
        return f"<builtin:{self.name}>"


@dataclass(frozen=True)
class VStr:
    """A string value."""
    value: str

    def __repr__(self) -> str:
        return self.value


Value = Union[VNum, VTree, VFn, VBuiltin, VStr]

LEAF = VTree("leaf")


# ── Lexer ────────────────────────────────────────────────────────────

def tokenize(src: str) -> list[str]:
    tokens = []
    i = 0
    while i < len(src):
        c = src[i]
        if c in " \t\n\r":
            i += 1
        elif c == ";":
            while i < len(src) and src[i] != "\n":
                i += 1
        elif c == "'":
            tokens.append("'")
            i += 1
        elif c in "()":
            tokens.append(c)
            i += 1
        elif c == '"':
            j = i + 1
            while j < len(src) and src[j] != '"':
                if src[j] == "\\":
                    j += 1
                j += 1
            tokens.append(src[i : j + 1])
            i = j + 1
        else:
            j = i
            while j < len(src) and src[j] not in " \t\n\r();'\"":
                j += 1
            tokens.append(src[i:j])
            i = j
    return tokens


# ── Parser ───────────────────────────────────────────────────────────

def parse(tokens: list[str], pos: int = 0) -> tuple[Expr, int]:
    if pos >= len(tokens):
        raise SyntaxError("unexpected end of input")
    tok = tokens[pos]

    if tok == "'":
        expr, pos = parse(tokens, pos + 1)
        return List((Sym("quote"), expr)), pos

    if tok == "(":
        items = []
        pos += 1
        while pos < len(tokens) and tokens[pos] != ")":
            expr, pos = parse(tokens, pos)
            items.append(expr)
        if pos >= len(tokens):
            raise SyntaxError("missing closing )")
        return List(tuple(items)), pos + 1

    if tok == ")":
        raise SyntaxError("unexpected )")

    # string literal?
    if tok.startswith('"') and tok.endswith('"'):
        return Sym(tok), pos + 1  # store as Sym, resolve in eval

    # number?
    try:
        return Num(float(tok)), pos + 1
    except ValueError:
        pass

    return Sym(tok), pos + 1


def parse_all(src: str) -> list[Expr]:
    tokens = tokenize(src)
    exprs = []
    pos = 0
    while pos < len(tokens):
        expr, pos = parse(tokens, pos)
        exprs.append(expr)
    return exprs


# ── Evaluator ────────────────────────────────────────────────────────

def e_op(x: float, y: float) -> float:
    """The fundamental operator: E(x, y) = exp(x) - ln(y)."""
    if y <= 0:
        raise ValueError(f"E(x, y): y must be positive, got {y}")
    return math.exp(x) - math.log(y)


def eval_expr(expr: Expr, env: dict) -> Value:
    # Number literal
    if isinstance(expr, Num):
        return VNum(expr.value)

    # Symbol lookup
    if isinstance(expr, Sym):
        # String literal
        if expr.name.startswith('"') and expr.name.endswith('"'):
            return VStr(expr.name[1:-1])
        if expr.name in env:
            return env[expr.name]
        raise NameError(f"undefined: {expr.name}")

    # List (application or special form)
    if not isinstance(expr, List) or len(expr.items) == 0:
        raise SyntaxError(f"cannot evaluate: {expr!r}")

    head = expr.items[0]
    args = expr.items[1:]

    # ── Special forms ──

    if isinstance(head, Sym):
        # (E x y) — the fundamental operator
        if head.name == "E":
            if len(args) != 2:
                raise SyntaxError("E takes exactly 2 arguments")
            xv = eval_expr(args[0], env)
            yv = eval_expr(args[1], env)
            if not isinstance(xv, VNum) or not isinstance(yv, VNum):
                raise TypeError(f"E expects numbers, got {xv!r} and {yv!r}")
            return VNum(e_op(xv.value, yv.value))

        # (quote expr) — return expression as tree
        if head.name == "quote":
            if len(args) != 1:
                raise SyntaxError("quote takes exactly 1 argument")
            return to_tree(args[0], env)

        # (eval tree) — evaluate a tree value
        if head.name == "eval":
            if len(args) != 1:
                raise SyntaxError("eval takes exactly 1 argument")
            tree = eval_expr(args[0], env)
            if not isinstance(tree, VTree):
                raise TypeError(f"eval expects a tree, got {tree!r}")
            return eval_tree(tree)

        # (match expr leaf-case (fn (l r) node-case))
        if head.name == "match":
            if len(args) != 3:
                raise SyntaxError("match takes exactly 3 arguments")
            tree = eval_expr(args[0], env)
            if not isinstance(tree, VTree):
                raise TypeError(f"match expects a tree, got {tree!r}")
            if tree.tag == "leaf":
                return eval_expr(args[1], env)
            else:
                fn = eval_expr(args[2], env)
                l, r = tree.children
                return apply_fn(fn, [l, r])

        # (fn (params...) body)
        if head.name == "fn":
            if len(args) != 2:
                raise SyntaxError("fn takes (params) and body")
            params = tuple(
                p.name for p in args[0].items
            ) if isinstance(args[0], List) else (args[0].name,)
            return VFn(params, args[1], env.copy())

        # (def name expr)
        if head.name == "def":
            if len(args) != 2:
                raise SyntaxError("def takes name and expr")
            name = args[0].name if isinstance(args[0], Sym) else str(args[0])
            val = eval_expr(args[1], env)
            env[name] = val
            return val

        # (let ((n v) ...) body)
        if head.name == "let":
            if len(args) != 2:
                raise SyntaxError("let takes bindings and body")
            bindings = args[0]
            body = args[1]
            new_env = env.copy()
            if isinstance(bindings, List):
                for b in bindings.items:
                    if isinstance(b, List) and len(b.items) == 2:
                        name = b.items[0].name
                        val = eval_expr(b.items[1], new_env)
                        new_env[name] = val
            return eval_expr(body, new_env)

        # (if cond then else)
        if head.name == "if":
            if len(args) != 3:
                raise SyntaxError("if takes 3 arguments")
            cond = eval_expr(args[0], env)
            if isinstance(cond, VNum) and cond.value == 0:
                return eval_expr(args[2], env)
            return eval_expr(args[1], env)

        # (letrec ((n v) ...) body) — recursive let
        if head.name == "letrec":
            if len(args) != 2:
                raise SyntaxError("letrec takes bindings and body")
            new_env = env.copy()
            if isinstance(args[0], List):
                for b in args[0].items:
                    if isinstance(b, List) and len(b.items) == 2:
                        name = b.items[0].name
                        new_env[name] = VNum(0)  # placeholder
                for b in args[0].items:
                    if isinstance(b, List) and len(b.items) == 2:
                        name = b.items[0].name
                        val = eval_expr(b.items[1], new_env)
                        new_env[name] = val
                        # patch closures to see the recursive env
                        if isinstance(val, VFn):
                            new_env[name] = VFn(val.params, val.body, new_env)
            return eval_expr(args[1], new_env)

    # ── Function application ──
    fn = eval_expr(head, env)
    vals = [eval_expr(a, env) for a in args]
    return apply_fn(fn, vals)


def apply_fn(fn: Value, args: list[Value]) -> Value:
    if isinstance(fn, VBuiltin):
        return fn.func(*args)
    if isinstance(fn, VFn):
        if len(args) != len(fn.params):
            raise TypeError(f"{fn!r} expects {len(fn.params)} args, got {len(args)}")
        new_env = fn.env.copy()
        for p, a in zip(fn.params, args):
            new_env[p] = a
        return eval_expr(fn.body, new_env)
    raise TypeError(f"not callable: {fn!r}")


def to_tree(expr: Expr, env: dict) -> VTree:
    """Convert a source expression to a VTree, evaluating unquoted sub-expressions."""
    if isinstance(expr, Num):
        if expr.value == 1:
            return LEAF
        raise ValueError("only 1 is a valid tree leaf")
    if isinstance(expr, Sym):
        # look up symbol — if it's a tree, return it; if number, error
        val = eval_expr(expr, env)
        if isinstance(val, VTree):
            return val
        raise TypeError(f"quote: {expr.name} is not a tree ({val!r})")
    if isinstance(expr, List):
        if len(expr.items) == 0:
            raise SyntaxError("empty list in quote")
        h = expr.items[0]
        if isinstance(h, Sym) and h.name == "E" and len(expr.items) == 3:
            l = to_tree(expr.items[1], env)
            r = to_tree(expr.items[2], env)
            return VTree("node", (l, r))
        if isinstance(h, Sym) and h.name == "unquote" and len(expr.items) == 2:
            val = eval_expr(expr.items[1], env)
            if isinstance(val, VTree):
                return val
            raise TypeError(f"unquote: expected tree, got {val!r}")
        raise SyntaxError(f"inside quote, only E and unquote are allowed: {expr!r}")
    raise SyntaxError(f"cannot quote: {expr!r}")


def eval_tree(tree: VTree) -> VNum:
    """Evaluate a VTree back to a number using E semantics."""
    if tree.tag == "leaf":
        return VNum(1.0)
    l, r = tree.children
    lv = eval_tree(l)
    rv = eval_tree(r)
    return VNum(e_op(lv.value, rv.value))


# ── Built-in functions ───────────────────────────────────────────────

def make_builtins() -> dict:
    env = {}

    # Arithmetic helpers (bootstrapped from E, but provided for convenience)
    env["+"] = VBuiltin("+", lambda a, b: VNum(a.value + b.value))
    env["-"] = VBuiltin("-", lambda a, b: VNum(a.value - b.value))
    env["*"] = VBuiltin("*", lambda a, b: VNum(a.value * b.value))
    env["/"] = VBuiltin("/", lambda a, b: VNum(a.value / b.value))
    env["exp"] = VBuiltin("exp", lambda a: VNum(math.exp(a.value)))
    env["ln"] = VBuiltin("ln", lambda a: VNum(math.log(a.value)))

    # Comparison
    env["="] = VBuiltin("=", lambda a, b: VNum(1.0 if _val(a) == _val(b) else 0.0))
    env["<"] = VBuiltin("<", lambda a, b: VNum(1.0 if _val(a) < _val(b) else 0.0))
    env[">"] = VBuiltin(">", lambda a, b: VNum(1.0 if _val(a) > _val(b) else 0.0))

    # Tree constructors
    env["leaf"] = LEAF
    env["node"] = VBuiltin("node", lambda l, r: VTree("node", (l, r)))
    env["leaf?"] = VBuiltin("leaf?", lambda t: VNum(1.0 if isinstance(t, VTree) and t.tag == "leaf" else 0.0))
    env["node?"] = VBuiltin("node?", lambda t: VNum(1.0 if isinstance(t, VTree) and t.tag == "node" else 0.0))
    env["left"] = VBuiltin("left", lambda t: t.children[0] if isinstance(t, VTree) and t.tag == "node" else (_ for _ in ()).throw(TypeError("not a node")))
    env["right"] = VBuiltin("right", lambda t: t.children[1] if isinstance(t, VTree) and t.tag == "node" else (_ for _ in ()).throw(TypeError("not a node")))

    # Numeric helpers
    env["round"] = VBuiltin("round", lambda a: VNum(round(a.value)))
    env["floor"] = VBuiltin("floor", lambda a: VNum(math.floor(a.value)))
    env["mod"] = VBuiltin("mod", lambda a, b: VNum(a.value % b.value))

    # Character / string
    env["chr"] = VBuiltin("chr", lambda a: VStr(chr(int(a.value))))
    env["ord"] = VBuiltin("ord", lambda a: VNum(float(ord(a.value[0]))) if isinstance(a, VStr) else VNum(float(ord(str(a.value)[0]))))
    env["str-join"] = VBuiltin("str-join", lambda *args: VStr("".join(
        a.value if isinstance(a, VStr) else repr(a) for a in args)))
    env["display"] = VBuiltin("display", _display)

    # IO
    env["print"] = VBuiltin("print", _print)
    env["tree-depth"] = VBuiltin("tree-depth", _tree_depth)

    return env


def _val(v: Value) -> float:
    if isinstance(v, VNum):
        return v.value
    if isinstance(v, VTree):
        return 1.0 if v.tag == "leaf" else 0.0
    return 0.0


def _display(*args: Value) -> Value:
    """Print without spaces or newline quoting — for string output."""
    print("".join(a.value if isinstance(a, VStr) else repr(a) for a in args))
    return args[0] if args else VNum(0)


def _print(*args: Value) -> Value:
    print(" ".join(repr(a) for a in args))
    return args[0] if args else VNum(0)


def _tree_depth(t: Value) -> VNum:
    if not isinstance(t, VTree):
        return VNum(0)
    if t.tag == "leaf":
        return VNum(0)
    l, r = t.children
    return VNum(1 + max(_tree_depth(l).value, _tree_depth(r).value))


# ── REPL / File runner ───────────────────────────────────────────────

def run(src: str, env: dict | None = None) -> Value:
    if env is None:
        env = make_builtins()
    exprs = parse_all(src)
    result = VNum(0)
    for expr in exprs:
        result = eval_expr(expr, env)
    return result


def repl():
    env = make_builtins()
    print("E-Calculus v0.1.0")
    print("  E(x, y) = exp(x) - ln(y)")
    print("  Type (help) for examples, Ctrl-D to exit.\n")

    while True:
        try:
            line = input("E> ")
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not line.strip():
            continue

        # accumulate multi-line input if parens are unbalanced
        while line.count("(") > line.count(")"):
            try:
                line += "\n" + input(".. ")
            except (EOFError, KeyboardInterrupt):
                print()
                break

        if line.strip() == "(help)":
            print_help()
            continue

        try:
            exprs = parse_all(line)
            for expr in exprs:
                result = eval_expr(expr, env)
                if result is not None:
                    print(f"=> {result!r}")
        except Exception as exc:
            print(f"error: {exc}")


def print_help():
    print("""
; ── Core ──
(E x y)             ; exp(x) - ln(y)
1                   ; the constant

; ── Tree operations ──
'(E 1 1)            ; quote: E-tree as data
(match tree a f)    ; destructure: leaf→a, node→(f left right)
(eval tree)         ; evaluate tree back to number

; ── Definitions ──
(def name expr)
(fn (x y) body)
(let ((x 1)) body)
(letrec ((f (fn (n) ...))) (f 5))
(if cond then else)

; ── Examples ──
(E 1 1)                          ; => e
'(E 1 1)                         ; => (E 1 1) as tree
(eval '(E 1 1))                  ; => e
(match '(E 1 1) 0 (fn (l r) l))  ; => 1 (the left leaf)
(def e (E 1 1))                  ; bind e
""")


def main():
    if len(sys.argv) > 1:
        path = sys.argv[1]
        with open(path) as f:
            src = f.read()
        env = make_builtins()
        run(src, env)
    else:
        repl()


if __name__ == "__main__":
    main()
