# word

Help memorizing words.

A GUI, compact and practical tool.

## Features

- Determine the most valuable word according to user's feedback and ebbinghaus's curve

- Portable, easy to extend

## Structure

- app.py

Main program.

- model.json 

It records user's feedback info and helps to determine the weights of words shown

- settings.json 

It records the latest course, make sure you go back to last course after you closed the program

- tools.py

It helps checking duplicate words in different words and remove the words in the model when you delete it from Excel data

- word.xlsx

It is the vocabulary notebook

- word.bat

It can be added to desktop or quick start as a shortcut to access the program