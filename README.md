# E-Calculus

A homoiconic programming language built on a single mathematical operator:

```
E(x, y) = exp(x) - ln(y)
```

and the constant `1`.

## Origin

A [physicist's paper](https://x.com/prywatnik/status/2043943516858986571) showed that all elementary mathematical functions — sin, cos, ln, √, π — can be expressed by nesting one operator `E(x, y) = exp(x) - ln(y)` with the constant `1`. Theoretically beautiful, practically absurd: expressing π requires dozens of nested E's.

This project takes the idea in a different direction. Instead of just computing numbers, what if we turned E-expressions into a _programming language_?

## The Key Insight: E-Trees Are S-Expressions

Every E-expression is a binary tree:

```
E(E(1, E(1, 1)), 1)

        E
       / \
      E    1
     / \
    1   E
       / \
      1   1
```

Leaves are `1`. Internal nodes are `E`. This is **structurally identical to Lisp's S-expressions**.

The problem is that E immediately collapses its tree into a single real number — it cannot observe its own structure. The fix is three operations:

| Operation | What it does | Why it matters |
|-----------|-------------|----------------|
| `quote`   | Freeze the tree — don't evaluate | Turns code into data |
| `match`   | Destructure: leaf or E(left, right)? | Lets you inspect the tree |
| `eval`    | Collapse back to a number | Restores original E semantics |

That's it. E-trees become both **code and data**. A Lisp that grew from one mathematical operator.

## Hello, World!

Every character is a **pure E-tree** — only `E` and `1`. No arithmetic. No numeric literals. Each tree was found by exhaustive search over E-expressions up to depth 6: the search explores how `exp(x) - ln(y)` compositions happen to land near specific ASCII codes.

```scheme
(def msg
  (node
    '(E (E (E (E 1 (E (E 1 1) 1)) (E 1 (E 1 1)))   ; H = 72 ≈ 72.04
        (E 1 (E (E 1 1) (E 1 1))))
        (E (E 1 (E (E 1 1) 1)) (E 1 (E 1 1))))
  (node
    '(E (E (E 1 (E 1 1)) (E 1 1))                    ; e = 101 ≈ 100.89
        (E (E 1 (E (E 1 1) (E 1 1)))
           (E (E 1 (E 1 1)) (E (E 1 1) 1))))
  ; ... l, l, o, ',', ' ', W, o, r, l, d, !
  ; (each one a similar nested E-tree — see examples/hello.e)
  leaf)))

; match walks the list. eval recovers each character.
(letrec ((decode (fn (tree)
  (match tree
    ""
    (fn (char-tree rest)
      (str-join (chr (round (eval char-tree)))
                (decode rest)))))))
  (display (decode msg)))
; => Hello, World!
```

The message is a linked list of quoted E-trees. `match` destructures each cons cell. `eval` collapses a quoted E-tree back to a real number — the ASCII code. `chr` and `round` turn that into a character.

The data **is** E-expressions. `eval` gives them back their meaning. This is homoiconicity: code = data = trees.

## Quick Start

```bash
python3 e_calculus.py                            # REPL
python3 e_calculus.py examples/hello.e           # Hello, World!
python3 e_calculus.py examples/basics.e          # fundamentals
python3 e_calculus.py examples/recursion.e       # Peano arithmetic, factorial
python3 e_calculus.py examples/self-eval.e       # tree surgery, homoiconicity
```

Requires Python 3.11+. No dependencies.

## Language Reference

### Core

```scheme
1                     ; the constant
(E x y)               ; exp(x) - ln(y)
```

### Tree Operations

```scheme
'(E 1 1)              ; quote — keep the tree as data
(match tree a f)      ; if leaf → a, if E(l,r) → (f l r)
(eval tree)           ; evaluate a quoted tree back to a number
```

### Definitions and Functions

```scheme
(def name expr)                  ; bind a name
(fn (x y) body)                  ; lambda
(let ((x 1) (y 2)) body)        ; let bindings
(letrec ((f (fn (n) ...))) body) ; recursive let
(if cond then else)              ; conditional (0 is falsy)
```

### Built-ins

```scheme
; Arithmetic (convenience wrappers, bootstrapped from E)
(+ a b)  (- a b)  (* a b)  (/ a b)
(exp a)  (ln a)  (round a)  (floor a)  (mod a b)

; Comparison
(= a b)  (< a b)  (> a b)

; Trees
(node l r)  (leaf? t)  (node? t)  (left t)  (right t)  (tree-depth t)

; Characters and output
(chr n)  (ord c)  (display ...)  (print ...)  (str-join ...)
```

## How It Works

```
              E(x, y) = exp(x) - ln(y)
                        │
                   E-expression tree
                  ╱         │         ╲
            quote          eval        match
         (freeze)      (collapse)   (inspect)
              ╲         │         ╱
               homoiconic language
              (code = data = trees)
```

**Without quote/match/eval**: E is a calculator. Nest E's and 1's, get a real number, done.

**With quote/match/eval**: E is a programming language. Trees are both data and syntax. You can build them, take them apart, and run them.

## Tools

`tools/find_ascii_trees.py` — the exhaustive search that finds E-trees evaluating to specific ASCII codes. This is how the Hello, World! character encodings were discovered.

```bash
python3 tools/find_ascii_trees.py
```

## License

MIT
