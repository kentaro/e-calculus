; ── E-Calculus: Hello, World! ──────────────────────────────
;
; Every character is born from E(x, y) = exp(x) - ln(y).
; The only constant is 1. Everything else derives from e = E(1, 1).

; ── The seed ──
(def e (E 1 1))                  ; e ≈ 2.718

; ── Building blocks: all derived from e ──
(def r3  (round e))              ; 3  = round(e)
(def r7  (round (* e e)))        ; 7  = round(e²)
(def r15 (round (E (E 1 1) 1)))  ; 15 = round(e^e)
(def r20 (round (* e (* e e))))  ; 20 = round(e³)

; ── Small numbers: derived from r3 and the constant 1 ──
(def two  (- r3 1))              ; 2 = 3 - 1
(def four (+ r3 1))              ; 4 = 3 + 1
(def five (+ r3 two))            ; 5 = 3 + 2
(def six  (* r3 two))            ; 6 = 3 * 2
(def nine (* r3 r3))             ; 9 = 3 * 3

; ── Hello, World! ──
;
;   H  =  72 = 3 * (20 + 4)      = 3 * 24
;   e  = 101 = 15 * 7 - 4
;   l  = 108 = 15 * 7 + 3
;   o  = 111 = 15 * 7 + 6
;   ,  =  44 = 7 * 7 - 5
;   SP =  32 = 4 * 4 * 2
;   W  =  87 = 3 * (20 + 7 + 2)  = 3 * 29
;   r  = 114 = 15 * 7 + 9
;   d  = 100 = 15 * 7 - 5
;   !  =  33 = 20 + 7 + 6

(def E-char (fn (n) (chr (round n))))

(display
  (E-char (* r3 (+ r20 four)))          ; H  = 3 * 24     = 72
  (E-char (- (* r15 r7) four))          ; e  = 105 - 4    = 101
  (E-char (+ (* r15 r7) r3))            ; l  = 105 + 3    = 108
  (E-char (+ (* r15 r7) r3))            ; l  = 108
  (E-char (+ (* r15 r7) six))           ; o  = 105 + 6    = 111
  (E-char (- (* r7 r7) five))           ; ,  = 49 - 5     = 44
  (E-char (* (* four four) two))         ; SP = 16 * 2     = 32
  (E-char (* r3 (+ r20 (+ r7 two))))    ; W  = 3 * 29     = 87
  (E-char (+ (* r15 r7) six))           ; o  = 111
  (E-char (+ (* r15 r7) nine))          ; r  = 105 + 9    = 114
  (E-char (+ (* r15 r7) r3))            ; l  = 108
  (E-char (- (* r15 r7) five))          ; d  = 105 - 5    = 100
  (E-char (+ r20 (+ r7 six)))           ; !  = 20 + 13    = 33
)
