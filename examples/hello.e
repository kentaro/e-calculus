; ── E-Calculus: Hello, World! ──────────────────────────────
;
; The message is a linked list of quoted E-trees.
; Each character is a pure E-expression — only E and 1.
; No numeric literals. No arithmetic. No built-in functions.
;
; match walks the list. eval collapses each E-tree to a number.
; chr(round(number)) gives the character.
;
; This is homoiconicity: the data IS E-expressions,
; and eval gives them back their meaning.

; ── The message: a tree of quoted E-trees ──
;
; node = cons (left = character tree, right = rest of string)
; leaf = nil  (end of string)
;
; Each character tree is a quoted E-expression that evaluates
; to (approximately) the ASCII code of that character.
; Found by exhaustive search over E-trees up to depth 6.

(def msg
  (node
    ; H = 72 ≈ 72.038
    '(E (E (E (E 1 (E (E 1 1) 1)) (E 1 (E 1 1))) (E 1 (E (E 1 1) (E 1 1)))) (E (E 1 (E (E 1 1) 1)) (E 1 (E 1 1))))
  (node
    ; e = 101 ≈ 100.886
    '(E (E (E 1 (E 1 1)) (E 1 1)) (E (E 1 (E (E 1 1) (E 1 1))) (E (E 1 (E 1 1)) (E (E 1 1) 1))))
  (node
    ; l = 108 ≈ 107.684
    '(E (E (E (E 1 (E (E 1 1) (E 1 1))) (E 1 (E 1 (E 1 1)))) (E 1 (E (E 1 1) (E 1 (E 1 1))))) (E 1 (E (E 1 1) (E 1 1))))
  (node
    ; l = 108 ≈ 107.684
    '(E (E (E (E 1 (E (E 1 1) (E 1 1))) (E 1 (E 1 (E 1 1)))) (E 1 (E (E 1 1) (E 1 (E 1 1))))) (E 1 (E (E 1 1) (E 1 1))))
  (node
    ; o = 111 ≈ 111.051
    '(E (E (E 1 (E (E 1 (E 1 1)) (E (E 1 1) (E 1 1)))) (E 1 (E (E 1 (E 1 1)) (E (E 1 1) 1)))) (E (E (E 1 (E (E 1 1) 1)) (E (E 1 1) (E 1 1))) (E 1 (E (E 1 (E 1 1)) (E 1 1)))))
  (node
    ; , = 44 ≈ 43.682
    '(E (E (E 1 (E (E 1 1) 1)) (E 1 (E (E 1 1) (E 1 1)))) (E (E 1 (E (E 1 1) (E 1 1))) (E (E 1 (E 1 1)) (E (E 1 1) 1))))
  (node
    ; SP = 32 ≈ 31.893
    '(E (E (E (E 1 (E (E 1 1) 1)) (E (E 1 1) 1)) (E 1 (E (E 1 1) (E 1 (E 1 1))))) (E 1 1))
  (node
    ; W = 87 ≈ 87.289
    '(E (E (E 1 (E 1 1)) (E (E 1 (E 1 1)) (E (E 1 1) 1))) (E (E (E 1 (E 1 1)) (E 1 (E 1 1))) 1))
  (node
    ; o = 111 ≈ 111.051
    '(E (E (E 1 (E (E 1 (E 1 1)) (E (E 1 1) (E 1 1)))) (E 1 (E (E 1 (E 1 1)) (E (E 1 1) 1)))) (E (E (E 1 (E (E 1 1) 1)) (E (E 1 1) (E 1 1))) (E 1 (E (E 1 (E 1 1)) (E 1 1)))))
  (node
    ; r = 114 ≈ 114.444
    '(E (E (E 1 (E (E 1 (E 1 1)) (E (E 1 1) 1))) (E 1 (E 1 1))) (E (E 1 1) 1))
  (node
    ; l = 108 ≈ 107.684
    '(E (E (E (E 1 (E (E 1 1) (E 1 1))) (E 1 (E 1 (E 1 1)))) (E 1 (E (E 1 1) (E 1 (E 1 1))))) (E 1 (E (E 1 1) (E 1 1))))
  (node
    ; d = 100 ≈ 99.707
    '(E (E (E 1 (E 1 1)) (E 1 1)) (E 1 (E (E 1 1) (E 1 1))))
  (node
    ; ! = 33 ≈ 32.893
    '(E (E (E (E 1 (E (E 1 1) 1)) (E (E 1 1) 1)) (E 1 (E (E 1 1) (E 1 (E 1 1))))) 1)
  leaf))))))))))))))

; ── Decode: match walks the tree, eval recovers each character ──

(letrec ((decode (fn (tree)
  (match tree
    ""                                              ; leaf → end
    (fn (char-tree rest)                            ; node → decode char
      (str-join (chr (round (eval char-tree)))      ; eval the E-tree → number → char
                (decode rest)))))))                  ; recurse

  (display (decode msg)))
