# -*- coding: utf-8 -*-

from runflare.inquirer.render.console import ConsoleRender
from runflare.inquirer import themes

def do_backspace(s):
    if not isinstance(s,str):
        return s
    chars = []
    for c in s:
        if c == '\b' and chars:
            chars.pop()
        else:
            chars.append(c)

    return ''.join(chars)

def prompt(questions, render=None, answers=None,
           theme=themes.Default(), raise_keyboard_interrupt=False):
    render = render or ConsoleRender(theme=theme)
    answers = answers or {}

    try:
        for question in questions:
            answers[question.name] = do_backspace(render.render(question, answers))
        return answers
    except KeyboardInterrupt:
        if raise_keyboard_interrupt:
            raise
        print('')
        print('Cancelled by user')
        print('')
