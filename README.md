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

Every character is derived from `e = E(1, 1)`. No numeric literal other than `1` appears:

```scheme
(def e (E 1 1))                  ; e ≈ 2.718

; Building blocks — all derived from e
(def r3  (round e))              ; 3  = round(e)
(def r7  (round (* e e)))        ; 7  = round(e²)
(def r15 (round (E (E 1 1) 1)))  ; 15 = round(e^e)
(def r20 (round (* e (* e e))))  ; 20 = round(e³)

; Small numbers — derived from r3 and the constant 1
(def two  (- r3 1))              ; 2 = 3 - 1
(def four (+ r3 1))              ; 4 = 3 + 1
(def five (+ r3 two))            ; 5 = 3 + 2
(def six  (* r3 two))            ; 6 = 3 * 2
(def nine (* r3 r3))             ; 9 = 3 * 3

(def E-char (fn (n) (chr (round n))))

(display
  (E-char (* r3 (+ r20 four)))        ; H  = 3 * 24   = 72
  (E-char (- (* r15 r7) four))        ; e  = 105 - 4  = 101
  (E-char (+ (* r15 r7) r3))          ; l  = 105 + 3  = 108
  (E-char (+ (* r15 r7) r3))          ; l  = 108
  (E-char (+ (* r15 r7) six))         ; o  = 105 + 6  = 111
  (E-char (- (* r7 r7) five))         ; ,  = 49 - 5   = 44
  (E-char (* (* four four) two))       ; SP = 16 * 2   = 32
  (E-char (* r3 (+ r20 (+ r7 two))))  ; W  = 3 * 29   = 87
  (E-char (+ (* r15 r7) six))         ; o  = 111
  (E-char (+ (* r15 r7) nine))        ; r  = 105 + 9  = 114
  (E-char (+ (* r15 r7) r3))          ; l  = 108
  (E-char (- (* r15 r7) five))        ; d  = 105 - 5  = 100
  (E-char (+ r20 (+ r7 six))))        ; !  = 20 + 13  = 33
; => Hello, World!
```

Four numbers — 3, 7, 15, 20 — all born from `E(1, 1)`, are enough to reach every ASCII character. Every other number is built from these and `1`.

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
