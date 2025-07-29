# python native
from typing import Any


# constants
DEVELOPING = False


def handle_error(
    error: Exception, 
    function: str, 
    default_error: str
) -> None:
    """
    Displays error message and what function the error occurred in.
    Either displays the full error message or just the error text,
    depending on whether the script is being developed or not.

    Parameters
    ----------
    error : Exception
        the exception that was raised
    function : str
        the name of the function that the expection was raised in
    default_error : str
        the error message to be displayed to the user, non-technical
        such that the user can more obviously know what to do
    """

    if DEVELOPING:
        print_internal('Error in function: ' + function, True)
        print_internal(type(error), True)
        print_internal(error, True)
    else:
        print_internal(default_error)

    etc()
    return


def etc() -> None:
    """
    Displays prompt to user to press Enter to continue.
    """

    input('Press Enter to continue\n')
    return


def print_internal(
    text: Any, 
    display_error_notice: bool=False
) -> None:
    """
    Prints a message with an indent indicating an internal message,
    a message that appears during setup of the script.

    Parameters
    ----------
    text : Any
        the data to display
    display_error_notice : bool, default=False
        true if "[ERROR]" prefix is desired
        false if "]" prefix is desired
    """

    if display_error_notice:
        print(f'[ERROR] {text}')
    else:
        print(f'] {text}')
    return


def print_script_message(text : str) -> None:
    """
    Prints a message with a >, indicating a message from the script.

    Parameters
    ----------
    text : str
        the data to display
    """

    print(f'> {text}')
    return


def save_log(filename: str, data: Any) -> None:
    with open(filename, 'a+', encoding="utf-8") as f:
        f.write(str(data))


def prompt_for_answer(prompt_text : str) -> str:
    answer = input(f'> {prompt_text}: ').strip()

    while not answer:
        print('Please enter a valid string.')
        answer = input(f'> {prompt_text}: ').strip()

    return answer


def select_list_options(options : list[str]) -> int:

    for i, option in enumerate(options):
        print(f'({i + 1}) {option}')

    try:
        choice = int(input('] '))

        if choice < 1 or choice > len(options):
            raise IndexError
        
        print()
        return choice

    except ValueError:
        print('Given choice is not a number.\n')
        return select_list_options(options)
    
    except IndexError:
        print('Given choice is not in the range of options.\n')
        return select_list_options(options)
    

# method used
# https://stackoverflow.com/a/7205107
def merge_dicts(dict1: dict, dict2: dict, path=[]):
    for key in dict2:
        if key in dict1:
            if isinstance(dict1[key], dict) and isinstance(dict2[key], dict):
                merge_dicts(dict1[key], dict2[key], path + [str(key)])
            elif dict1[key] != dict2[key]:
                raise Exception('Conflict at ' + '.'.join(path + [str(key)]))
        else:
            dict1[key] = dict2[key]
    return dict1
