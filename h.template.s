.section .data
format:     .asciz "%d\n"

.section .text
.global main

main:

ldr X19, =stack

{}

ldr X0, #0
mov X8, #93
svc 0

.bss
    .align 3
stack: .skip 1048576
