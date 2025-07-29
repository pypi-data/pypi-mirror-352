from customtkinter import CTkToplevel, CTkButton, CTkLabel, CTk
from os import path
from winsound import MessageBeep, MB_ICONHAND, MB_OK

class MessageBox(object):
    def showError(title, message):
        MessageBeep(MB_ICONHAND)
        container = CTkToplevel()
        container.title(title)
        container.geometry("330x95")
        container.resizable(False, False)

        dirPath = path.dirname(__file__)
        errorIconPath = path.join(dirPath, "MessageboxIcons", "ErrorIcon.ico")

        container.after(250, lambda: container.iconbitmap(errorIconPath))
        container.attributes('-topmost', 'true')

        containerTitle = CTkLabel(container, text=message)
        containerTitle.place(relx=0.5, rely=0.28, anchor="center")

        containerButton = CTkButton(container, text="Weiter", cursor="hand2", command=lambda: container.destroy())
        containerButton.place(relx=0.5, rely=0.75, anchor="center")
        
    def showInfo(title, message):
        MessageBeep(MB_OK)
        container = CTkToplevel()
        container.title(title)
        container.geometry("330x95")
        container.resizable(False, False)

        dirPath = path.dirname(__file__)
        infoIconPath = path.join(dirPath, "MessageboxIcons", "InfoIcon.ico")

        container.after(250, lambda: container.iconbitmap(infoIconPath))
        container.attributes('-topmost', 'true')

        containerTitle = CTkLabel(container, text=message)
        containerTitle.place(relx=0.5, rely=0.28, anchor="center")

        containerButton = CTkButton(container, text="Weiter", cursor="hand2", command=lambda: container.destroy())
        containerButton.place(relx=0.5, rely=0.75, anchor="center")

    def askWindow(title, message, yesText, noText, yesCommand):
        MessageBeep(MB_OK)
        container = CTkToplevel()
        container.title(title)
        container.geometry("330x95")
        container.resizable(False, False)

        dirPath = path.dirname(__file__)
        infoIconPath = path.join(dirPath, "MessageboxIcons", "InfoIcon.ico")

        container.after(250, lambda: container.iconbitmap(infoIconPath))
        container.attributes('-topmost', 'true')

        containerTitle = CTkLabel(container, text=message)
        containerTitle.place(relx=0.5, rely=0.28, anchor="center")
        
        # Bestätigen Eingabe
        containerButton = CTkButton(container, text=yesText, cursor="hand2", command=yesCommand)
        containerButton.place(relx=0.25, rely=0.75, anchor="center")

        # Abbrechen Eingabe
        containerButton = CTkButton(container, text=noText, cursor="hand2", command=lambda: container.destroy(), fg_color="grey")
        containerButton.place(relx=0.75, rely=0.75, anchor="center")