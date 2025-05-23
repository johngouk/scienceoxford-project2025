# Script to display commands and their content
C_shift_L = 0x10
C_shift_R = 0x14
D_shift_L = 0x18
D_shift_R = 0x1A

Display_ON_OFF = 0x08 # OR'd 0b-1-- Display on 0b--1- Cursor on 0b---1 Blink on

Set_DRAM_addr_0 = 0x20 # OR'd with 0x00 - 0x27
Set_DRAM_addr_1 = 0x40 # OR'd with 0x00 - 0x27
l.setcmd(0x10) # Cursor/display shift; moves cursor/display 0b0--- Cursor 0b1--- Display 0b-0-- Left 0b-1-- Right