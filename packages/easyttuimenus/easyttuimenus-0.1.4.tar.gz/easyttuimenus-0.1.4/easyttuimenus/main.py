from os import system, name

def _display(prompt, options = None, mode = ""):
    '''
    Forgive me.

    `options` is either a dictionary containing `int: value` pairs or a list containing a "min" and "max" value.
    '''
    break_hard = "=============================="
    break_soft = "------------------------------"
    input_prompt = ":: "
    clear_screen = system("cls") if name == "nt" else system("clear")

    clear_screen
    print(f"{break_hard}\n{prompt}\n{break_soft}")
    if mode == "list_mode":
        for i in range(len(options)):
            print(f"{i}: {options[i]}")
    elif mode == "int_mode":
        print(f"Enter a number between {options[0]} and {options[1]}")
    else:
        pass
    print(break_hard)
    try:
        return int(input(input_prompt))
    except Exception as e:
        return e

def list_menu(prompt: str, options: list):
    '''
    :param prompt: Text to display to the user
    :param options: List of every possible option, in a text format
    :return: An index within `options`
    '''
    while True:
        response = _display(prompt, options, mode = "list_mode")
        if isinstance(response, ValueError):
            prompt = prompt + "\nPlease only enter number values."
        elif response > len(options) or response < 0:
            prompt = prompt + f"\nResponse {response} is not in the available options. Please try another."
        else:
            return response
            
def int_menu(prompt: str, options: list):
    while True:
        response = _display(prompt, options, mode = "int_mode")
        if isinstance(response, ValueError):
            prompt = prompt + "\nPlease only enter number values."
        elif response < options[0] or response > options[1]:
            prompt = prompt + f"\nResponse {response} was out of range. Please try another."
        else:
            return response
    
options = ["dingus", "dongus"]
list_menu("", options)
