# Easy TTUI Menus

## About

Write simple UI for your code in seconds in a unified way using Easy TTUI Menus

## Installation

Run `pip install easyttuimenus` from your preferred environment.

## Usage

### List Menu

`list_menu(prompt: str, options: list)`

Use when you have a list of possible valid options.

#### Parameters

`prompt`: Information to give to the user

`opitons`: The list of options to select

#### Returns

An index from `options`

#### Example Usage

```python
import easyttuimenus
prompt = "Pick one of these"
options = ["lorem", "ipsum", "lorem ipsum"]
choice = easyttuimenus.list_menu(prompt, options)
print(options[choice]) # selected item from options
```

### Int Menu

Use when you want to take an integer value as input.

#### Parameters

`prompt`: Information to give to the user


`opitons`: A list containing a minimum and maximum value

#### Returns

An integer value

#### Example Usage

```python
import easyttuimenus
min_and_max = [0, 10]
prompt = "Pick a value between 0 and 10"
user_input = easyttuimenus.int_menu(prompt, min_and_max)
print(user_input) # user selected number
```


