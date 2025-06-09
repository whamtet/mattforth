.global _start

_start:

ldr X4, =stack

{}

ldr X0, #0
mov X8, #93
svc 0

.bss
    .align 3
stack: .skip 1048576
pointer: .skip 8
print_buffer: .skip 32
