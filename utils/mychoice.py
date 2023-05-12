with open('txt_static_list/os.txt') as f:
    os_lines = [l.strip() for l in f.readlines()]

with open('txt_static_list/processor.txt') as f:
    processor_lines = [l.strip() for l in f.readlines()]

with open('txt_static_list/graphics.txt') as f:
    graphics_lines = [l.strip() for l in f.readlines()]

with open('txt_static_list/directx.txt') as f:
    directx_lines = [l.strip() for l in f.readlines()]

OS_CHOICES = []
for i in os_lines:
    OS_CHOICES.append((i, i))

PROCESSOR_CHOICES = []
for i in processor_lines:
    PROCESSOR_CHOICES.append((i, i))

GRAPHICS_CHOICES = []
for i in graphics_lines:
    GRAPHICS_CHOICES.append((i, i))

DIRECTX_CHOICES = []
for i in directx_lines:
    DIRECTX_CHOICES.append((i, i))

