# E-Calculus

A homoiconic programming language built on a single mathematical operator:

```
E(x, y) = exp(x) - ln(y)
```

and the constant `1`.

## Origin

A [physicist's paper](https://x.com/prywatnik/status/2043943516858986571) showed that all elementary mathematical functions — sin, cos, ln, √, π — can be expressed by nesting one operator `E(x, y) = exp(x) - ln(y)` with the constant `1`. The result is theoretically beautiful and practically absurd: expressing π requires dozens of nested E's.

This project takes the idea further. Instead of just computing numbers, what if we turned E-expressions into a _programming language_?

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

Leaves are `1`. Internal nodes are `E`. This structure is **isomorphic to Lisp's S-expressions**.

The problem is that `E` immediately collapses its tree into a single real number — it can't observe its own structure. The fix is three operations:

| Operation | What it does | Why it matters |
|-----------|-------------|----------------|
| `quote`   | Freeze the tree — don't evaluate | Turns code into data |
| `match`   | Destructure: leaf or E(left, right)? | Lets you inspect the tree |
| `eval`    | Collapse back to a number | Restores original E semantics |

With these three additions, E-trees become both **code and data**. You get a Lisp that grew from a single mathematical operator.

## Quick Start

```bash
# REPL
python3 e_calculus.py

# Run a file
python3 e_calculus.py examples/hello.e
```

Requires Python 3.11+. No dependencies.

## Language Reference

### Core

```scheme
1                     ; the constant
(E x y)               ; exp(x) - ln(y) — the fundamental operator
```

### Tree Operations (the three additions that make it a language)

```scheme
'(E 1 1)              ; quote: keep the tree as data, don't evaluate
(match tree a f)      ; if tree is a leaf → a, if tree is E(l,r) → (f l r)
(eval tree)           ; evaluate a quoted tree back to a number
```

### Definitions and Functions

```scheme
(def name expr)                 ; bind a name
(fn (x y) body)                 ; lambda
(let ((x 1) (y 2)) body)       ; let bindings
(letrec ((f (fn (n) ...))) body) ; recursive let
(if cond then else)             ; conditional (0 is falsy)
```

### Built-ins

```scheme
; Arithmetic (bootstrapped from E, provided for convenience)
(+ a b)  (- a b)  (* a b)  (/ a b)
(exp a)  (ln a)  (round a)  (floor a)  (mod a b)

; Comparison (returns 1 or 0)
(= a b)  (< a b)  (> a b)

; Trees
(node l r)        ; construct a tree node
(leaf? t)         ; is it a leaf?
(left t) (right t) ; children of a node
(tree-depth t)    ; depth of a tree

; Characters and strings
(chr n)           ; number → character
(ord c)           ; character → number
(display ...)     ; print concatenated output
(print ...)       ; print space-separated with repr
```

## Examples

### The Basics

```scheme
(E 1 1)               ; => 2.718281828 (e)
(E (E 1 1) 1)         ; => 15.15426224 (e^e)
(E 1 (E 1 1))         ; => 1.718281828 (e - 1)

'(E 1 1)              ; => (E 1 1) — a tree, not a number
(eval '(E 1 1))       ; => 2.718281828 — back to a number

; Destructure a tree
(match '(E 1 1)
  "leaf"
  (fn (l r) "node"))  ; => "node"
```

### Pairs from Trees

```scheme
(def pair (fn (a b) (node a b)))
(def fst  (fn (p) (match p leaf (fn (l r) l))))
(def snd  (fn (p) (match p leaf (fn (l r) r))))

(def p (pair '(E 1 1) '(E (E 1 1) 1)))
(eval (fst p))        ; => e
(eval (snd p))        ; => e^e
```

### Natural Numbers as Trees

```scheme
; Peano encoding: leaf = 0, (node n leaf) = succ(n)
(def zero leaf)
(def succ (fn (n) (node n leaf)))
(def pred (fn (n) (match n leaf (fn (l r) l))))
(def zero? (fn (n) (match n 1 (fn (l r) 0))))

(letrec ((add (fn (a b)
  (if (zero? a) b (add (pred a) (succ b))))))
  (tree-depth (add (succ (succ zero)) (succ (succ (succ zero))))))
; => 5
```

### Hello, World!

Every character is derived from `e = E(1, 1)`:

```scheme
(def e (E 1 1))                  ; 2.718...
(def r3  (round e))              ; 3
(def r7  (round (* e e)))        ; 7
(def r15 (round (E (E 1 1) 1)))  ; 15  ← from e^e
(def r20 (round (* e (* e e))))  ; 20

(display
  (chr (* r3 (+ r20 (+ r3 1))))         ; H  = 3*24       = 72
  (chr (- (* r15 r7) (+ r3 1)))         ; e  = 15*7 - 4   = 101
  (chr (+ (* r15 r7) r3))               ; l  = 15*7 + 3   = 108
  (chr (+ (* r15 r7) r3))               ; l  = 108
  (chr (+ (* r15 r7) (* r3 (- r3 1))))  ; o  = 15*7 + 6   = 111
  (chr (- (* r7 r7) (+ r3 (- r3 1))))   ; ,  = 7*7 - 5    = 44
  (chr (* (* (+ r3 1) (+ r3 1)) (- r3 1)))  ; SP = 4*4*2  = 32
  (chr (* r3 (+ r20 (+ r7 (- r3 1)))))  ; W  = 3*29       = 87
  (chr (+ (* r15 r7) (* r3 (- r3 1))))  ; o  = 111
  (chr (+ (* r15 r7) (* r3 r3)))        ; r  = 15*7 + 9   = 114
  (chr (+ (* r15 r7) r3))               ; l  = 108
  (chr (- (* r15 r7) (+ r3 (- r3 1))))  ; d  = 15*7 - 5   = 100
  (chr (+ r20 (+ r7 (+ r3 r3)))))       ; !  = 20+7+6     = 33
; => Hello, World!
```

Four numbers — 3, 7, 15, 20 — all born from `E(1, 1)`, are enough to reach every ASCII character.

## Architecture

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

**Without quote/match/eval**: E is a calculator. You nest E's and 1's, get a real number, done.

**With quote/match/eval**: E is a programming language. Trees are both the data structure and the syntax. You can build trees, take them apart, and run them — the trinity of operations that makes Lisp, Lisp.

## Running the Examples

```bash
python3 e_calculus.py examples/basics.e     # fundamentals
python3 e_calculus.py examples/hello.e      # Hello, World!
python3 e_calculus.py examples/recursion.e  # Peano arithmetic, factorial
python3 e_calculus.py examples/self-eval.e  # homoiconicity, tree surgery
```

## License

MIT
