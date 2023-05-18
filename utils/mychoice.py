def create_choice_list(file_name, ):
    choice_list = []
    with open(f'txt_static_list/{file_name}') as f:
        file_lines = [l.strip() for l in f.readlines()]
    file_lines.pop(0)
    for i in file_lines:
        choice_list.append((i, i))
    return choice_list


OS_CHOICES = create_choice_list('os.txt')

PROCESSOR_CHOICES = create_choice_list('processor.txt')

GRAPHICS_CHOICES = create_choice_list('graphics.txt')

DIRECTX_CHOICES = create_choice_list('directx.txt')
