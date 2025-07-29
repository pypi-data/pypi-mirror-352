from customtkinter import *
from Messageboxclass import MessageBox

app = CTk()
MessageBox.askWindow("Ask", "Möchten Sie testen?", "Ja", "Nein", yesCommand=lambda: print("Ja gedrückt!"))
app.mainloop()