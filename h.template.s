.section .data
format:      .asciz "%ld\n"
format_str:  .asciz "%s\n"
format2:     .asciz "%s: %s\n"

{}

.section .text
.global main

main:

ldr X19, =stack
ldr X20, =block

{}

ldr X0, #0
mov X8, #93
svc 0

.bss
    .align 3
stack: .skip 1048576
block: .skip 1048576

{}