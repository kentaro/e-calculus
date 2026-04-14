; ── E-Calculus: Hello, World! ──────────────────────────────
;
; Every character is born from E(x, y) = exp(x) - ln(y).
; e = E(1,1) ≈ 2.718...  — the only seed we need.

(def e (E 1 1))

; ── Express ASCII codes through e ──
;
;   e   = 2.718...
;   e*e = 7.389...   (shorthand for (E (E 1 1) 1) would give e^e ≈ 15.15,
;                      but * is bootstrapped from E for convenience)
;
; The game: reach each character code using e and arithmetic.

; H = 72  ≈ round(e * e * e * e * e * e * e * e / 100)
;        ... nah, let's be more direct about it.

; Helper: build a char from an E-based expression
(def E-char (fn (n) (chr (round n))))

; ── Each character, expressed through e ──

; H  =  72 = round(e^(e+1) + e*e + e)
;   e^(e+1) = e^3.718 ≈ 41.19, e*e ≈ 7.39, total ≈ 51... nope.
; Let's use: E(E(1,1), 1) = e^e ≈ 15.154
; and build from there with arithmetic.

(def ee   (E (E 1 1) 1))       ; e^e       ≈ 15.154
(def eee  (E (E (E 1 1) 1) 1)) ; e^(e^e)   ≈ 3814279.105

; ASCII codes as E-arithmetic:
; H  =  72 = round(ee * ee / pi... ) — let's just be honest and use e.
(def H  (E-char (* ee (+ e (E 1 (E 1 1))))))   ; ee * (e + (e-1)) = 15.15 * 4.718 ≈ 71.5 → 72
(def e_ (E-char (* e (- ee (* e e)))))           ; e * (ee - e²) = 2.718 * (15.154 - 7.389) ≈ 21.1... no

; OK. Let's be pragmatic and beautiful at the same time.
; Express each code as a polynomial in e. The beauty is that
; every number traces back to E(1,1).

(def c-H (E-char (round (- (* e (* e e)) (+ e e)))))      ; e³ - 2e = 20.09 - 5.44 ≈ 14.6... no

; Fine — the HONEST approach: e to integer arithmetic.
; The point is every number starts from (E 1 1).

(def c-H (E-char (* (round (* e e)) (round (* e (+ e e)))))) ; 7 * ... nope

; Let's just build it cleanly.
; round(e) = 3, round(e*e) = 7, round(e*e*e) = 20, round(e^e) = 15

(def r3  (round e))              ; 3
(def r7  (round (* e e)))        ; 7
(def r15 (round ee))             ; 15
(def r20 (round (* e (* e e))))  ; 20

; Now spell out Hello, World! from these building blocks:
;   H  =  72 = 3 * (20 + 4)  = 3 * 24 = 72     ✓  (24 = 20 + 4 = 20 + 3 + 1)
;   e  = 101 = 15 * 7 - 4    = 105 - 4 = 101    ✓
;   l  = 108 = 15 * 7 + 3    = 105 + 3 = 108    ✓
;   o  = 111 = 15 * 7 + 3*2  = 111               ✓
;   ,  =  44 = 7 * 7 - 3 - 2 = 49 - 5 = 44      ✓  (but 2 = 3-1)
;   SP =  32 = 3 * 7 + 7 + 4 ... = nah. 32 = 20 + 7 + 3 + 2 ... no.
;              = (3 + 1) * (3 + 1) * (3 - 1) = 4*4*2 = 32  ✓
;   W  =  87 = 3 * (20 + 7 + 2) = 3 * 29 = 87   ✓
;   r  = 114 = 15 * 7 + 3*3  = 105 + 9 = 114    ✓
;   d  = 100 = 15 * 7 - 3 - (3-1) = 105 - 5 = 100  ✓
;   !  =  33 = 20 + 7 + 3 + 3 = 33               ✓

(def one 1)
(def two  (- r3 one))       ; 2
(def four (+ r3 one))       ; 4
(def nine (* r3 r3))        ; 9

(display
  (E-char (* r3 (+ r20 four)))            ; H  = 3*(20+4)       = 72
  (E-char (- (* r15 r7) four))            ; e  = 15*7 - 4       = 101
  (E-char (+ (* r15 r7) r3))              ; l  = 15*7 + 3       = 108
  (E-char (+ (* r15 r7) r3))              ; l  = 15*7 + 3       = 108
  (E-char (+ (* r15 r7) (* r3 two)))      ; o  = 15*7 + 6       = 111
  (E-char (- (* r7 r7) (+ r3 two)))       ; ,  = 7*7 - 5        = 44
  (E-char (* (* four four) two))           ; SP = 4*4*2          = 32
  (E-char (* r3 (+ r20 (+ r7 two))))      ; W  = 3*(20+7+2)     = 87
  (E-char (+ (* r15 r7) (* r3 two)))      ; o  = 15*7 + 6       = 111
  (E-char (+ (* r15 r7) nine))            ; r  = 15*7 + 9       = 114
  (E-char (+ (* r15 r7) r3))              ; l  = 15*7 + 3       = 108
  (E-char (- (* r15 r7) (+ r3 two)))      ; d  = 15*7 - 5       = 100
  (E-char (+ r20 (+ r7 (+ r3 r3))))       ; !  = 20+7+3+3       = 33
)
