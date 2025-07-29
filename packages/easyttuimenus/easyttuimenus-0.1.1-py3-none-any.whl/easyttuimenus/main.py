#!../venv/bin/python3
# A unified input system
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
    if mode == "dict_mode":
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
    options_with_keys = {i: options[i] for i in range(len(options))}
    while True:
        response = _display(prompt, options_with_keys, mode = "dict_mode")
        if isinstance(response, ValueError):
            prompt = prompt + "\nPlease only enter number values."
        elif not response in options_with_keys:
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



def main():
    test_options = ["yes", "no", "heck naw"]
    print(test_options[list_menu("Pick one of these", test_options)])


if __name__ == "__main__":
    main()