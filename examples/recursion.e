; ── E-Calculus: Recursion via Trees ────────────────────────
;
; Trees are natural numbers: leaf = 0, (node leaf t) = succ(t).
; With letrec, we get recursion.

; ── Peano numbers as E-trees ──
(def zero leaf)
(def succ (fn (n) (node n leaf)))

(def one   (succ zero))
(def two   (succ one))
(def three (succ two))
(def four  (succ three))
(def five  (succ four))

(print "three =" three)

; ── Is it zero? ──
(def zero? (fn (n) (match n 1 (fn (l r) 0))))

; ── Predecessor ──
(def pred (fn (n) (match n leaf (fn (l r) l))))

; ── Addition ──
(letrec ((add (fn (a b)
  (if (zero? a)
    b
    (add (pred a) (succ b))))))
  (print "2 + 3 =" (tree-depth (add two three))))

; ── Factorial (result as tree depth) ──
(letrec ((mul (fn (a b)
  (letrec ((go (fn (i acc)
    (if (zero? i)
      acc
      (letrec ((add-b (fn (x y)
        (if (zero? x) y (add-b (pred x) (succ y))))))
        (go (pred i) (add-b b acc)))))))
    (go a zero)))))

  ; 4! = 24
  (print "4! =" (tree-depth (mul four (mul three two)))))
