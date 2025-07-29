## About

This is a simple Python Messagebox to display current Infos or Errors when using Customtkinter.
<br>

## Installation
```
  pip install ctksimplemessagebox
```
<br>

## How to call the Object
1. First you have to import the Messagecontainer 
```python
  from CTkSimpleMessagebox import MessageContainer
```

 Note: you should also import [customtkinter](https://pypi.org/project/customtkinter/). <br><br>

2. Now you can call the functions
```python
  MessageContainer.showError("title", "message")
```
<br>

## Example 1 - Calling the Error Messagebox
```python
  from CTkSimpleMessagebox import MessageContainer
  from customtkinter import CTk

  app = CTk()
  MessageContainer.showError("Error", "This is a Testerror.")
  app.mainloop()
```

## Example 2 - Calling the Info Messagebox
```python
  ...

  MessageContainer.showInfo("Info", "This is a Testinfo.")
  app.mainloop()
```