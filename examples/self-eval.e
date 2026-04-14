; ── E-Calculus: Self-reference ─────────────────────────────
;
; The key insight: E-trees are both data and code.
; quote freezes evaluation, eval resumes it.
; This gives us homoiconicity — the essence of Lisp.

; ── A tree that evaluates to e ──
(def tree-e '(E 1 1))
(print "tree:" tree-e)
(print "value:" (eval tree-e))

; ── A deeper tree: e^e ──
(def tree-ee '(E (E 1 1) 1))
(print "tree:" tree-ee)
(print "value:" (eval tree-ee))

; ── Build a tree, then evaluate it ──
; node constructor builds trees at runtime
(def my-tree (node leaf (node leaf leaf)))
(print "built:" my-tree)
(print "depth:" (tree-depth my-tree))
(print "value:" (eval my-tree))

; ── Tree surgery: swap children of a node ──
(def swap (fn (t)
  (match t
    leaf
    (fn (l r) (node r l)))))

(def original '(E (E 1 1) 1))
(def swapped (swap original))
(print "original:" original "=>" (eval original))
(print "swapped: " swapped "=>" (eval swapped))

; ── Count leaves in a tree ──
(letrec ((count-leaves (fn (t)
  (match t
    1
    (fn (l r) (+ (count-leaves l) (count-leaves r)))))))
  (print "leaves in (E (E 1 1) (E 1 1)):"
    (count-leaves '(E (E 1 1) (E 1 1)))))

; ── The zero tree from our experiment ──
; Recall: E(e, E(e^e, e-1)) ≈ 0
(def zero-tree '(E (E 1 1) (E (E (E 1 1) 1) (E 1 (E 1 1)))))
(print "zero-tree evaluates to:" (eval zero-tree))
