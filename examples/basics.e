; ── E-Calculus: The Basics ──────────────────────────────────
;
; Everything begins with E(x, y) = exp(x) - ln(y) and the constant 1.

; The constant
1                       ; => 1

; The fundamental operator
(E 1 1)                 ; => e (2.718...)

; Nesting
(E (E 1 1) 1)           ; => exp(e) = e^e (15.154...)
(E 1 (E 1 1))           ; => exp(1) - ln(e) = e - 1 (1.718...)

; ── Named values ──
(def e (E 1 1))
(print "e =" e)

(def e-minus-1 (E 1 (E 1 1)))
(print "e - 1 =" e-minus-1)

(def e-to-the-e (E (E 1 1) 1))
(print "e^e =" e-to-the-e)

; ── Trees: code as data ──
(def t '(E 1 1))
(print "quoted:" t)

; Evaluate the tree back to a number
(print "eval'd:" (eval t))

; Destructure with match
(print "match leaf:"
  (match '1 "it's a leaf" (fn (l r) "it's a node")))

(print "match node:"
  (match '(E 1 1) "leaf" (fn (l r) "node")))

; Extract children
(print "left child of (E 1 1):"
  (match '(E 1 1) "leaf" (fn (l r) l)))

; ── Building trees programmatically ──
(def pair (fn (a b) (node a b)))
(def fst  (fn (p) (match p leaf (fn (l r) l))))
(def snd  (fn (p) (match p leaf (fn (l r) r))))

(def p (pair '(E 1 1) '(E (E 1 1) 1)))
(print "pair:" p)
(print "fst:" (fst p))
(print "snd:" (snd p))
(print "eval fst:" (eval (fst p)))
(print "eval snd:" (eval (snd p)))
