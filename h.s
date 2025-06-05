.global _start

_start:

ldr X0, =h
mov X8, #93
svc 0

.data
h: .ascii "f"
