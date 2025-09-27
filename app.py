import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import time
import threading
import os
from cryptography.fernet import Fernet
import base64
import hashlib

languages = {
    "DE": {
        "title": "Verschlüsselungs-App",
        "info": "Diese Anwendung kann Texte und Dateien verschlüsseln und entschlüsseln.",
        "btn_info": "Info",
        "label_lang": "Sprache auswählen:",
        "tab_text": "Text",
        "tab_file": "Datei",
        "encrypt": "Verschlüsseln",
        "decrypt": "Entschlüsseln",
        "password": "Passwort:",
        "input_text": "Text eingeben:",
        "output_text": "Ergebnis:",
        "select_file": "Datei auswählen",
        "status_done": "Fertig!",
    },
    "EN": {
        "title": "Encryption App",
        "info": "This application can encrypt and decrypt text and files.",
        "btn_info": "Info",
        "label_lang": "Select language:",
        "tab_text": "Text",
        "tab_file": "File",
        "encrypt": "Encrypt",
        "decrypt": "Decrypt",
        "password": "Password:",
        "input_text": "Enter text:",
        "output_text": "Result:",
        "select_file": "Select file",
        "status_done": "Done!",
    }
}

current_lang = "DE"


def generate_key(password: str) -> bytes:
    key = hashlib.sha256(password.encode()).digest()
    return base64.urlsafe_b64encode(key)


def encrypt_text(text: str, password: str) -> str:
    f = Fernet(generate_key(password))
    return f.encrypt(text.encode()).decode()


def decrypt_text(token: str, password: str) -> str:
    f = Fernet(generate_key(password))
    return f.decrypt(token.encode()).decode()


def encrypt_file(filepath: str, password: str):
    f = Fernet(generate_key(password))
    with open(filepath, "rb") as file:
        data = file.read()
    encrypted = f.encrypt(data)
    with open(filepath + ".enc", "wb") as file:
        file.write(encrypted)


def decrypt_file(filepath: str, password: str):
    f = Fernet(generate_key(password))
    with open(filepath, "rb") as file:
        data = file.read()
    decrypted = f.decrypt(data)
    original_path = filepath.replace(".enc", "")
    with open(original_path, "wb") as file:
        file.write(decrypted)


class SplashScreen(tk.Toplevel):
    def __init__(self, parent, on_finish):
        super().__init__(parent)
        self.parent = parent
        self.on_finish = on_finish
        self.progress = 0

        self.title("Loading...")
        self.geometry("1200x300")
        self.configure(bg="black")

        ascii_art = r"""
 ______     __  __     __         __     ______     __  __     __     __         ______     ______     ______    
/\  == \   /\ \_\ \   /\ \       /\ \   /\  ___\   /\ \/ /    /\ \   /\ \       /\  __ \   /\  == \   /\  ___\   
\ \  __<   \ \____ \  \ \ \____  \ \ \  \ \ \____  \ \  _"-.  \ \ \  \ \ \____  \ \  __ \  \ \  __<   \ \___  \  
 \ \_____\  \/\_____\  \ \_____\  \ \_\  \ \_____\  \ \_\ \_\  \ \_\  \ \_____\  \ \_\ \_\  \ \_____\  \/\_____\ 
  \/_____/   \/_____/   \/_____/   \/_/   \/_____/   \/_/\/_/   \/_/   \/_____/   \/_/\/_/   \/_____/   \/_____/ 
                                                                                                                 

"""
        self.label_ascii = tk.Label(self, text=ascii_art, fg="lime", bg="black", font=("Courier", 12))
        self.label_ascii.pack(pady=20)

        self.progress_label = tk.Label(self, text="Loading... 0%", fg="white", bg="black")
        self.progress_label.pack(pady=10)

        self.progressbar = ttk.Progressbar(self, length=400, mode="determinate")
        self.progressbar.pack(pady=10)

        threading.Thread(target=self.load).start()

    def load(self):
        for i in range(101):
            time.sleep(0.03)
            self.progress = i
            self.progressbar["value"] = i
            self.progress_label.config(text=f"Loading... {i}%")
            self.update_idletasks()
        self.after(500, self.finish)

    def finish(self):
        self.destroy()
        self.on_finish()


class MyApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.lang = current_lang
        self.title(languages[self.lang]["title"])
        self.geometry("600x400")

        self.label_lang = tk.Label(self, text=languages[self.lang]["label_lang"])
        self.label_lang.pack(pady=5)

        self.lang_var = tk.StringVar(value=self.lang)
        self.combo = ttk.Combobox(self, textvariable=self.lang_var, values=["DE", "EN"], state="readonly")
        self.combo.pack(pady=5)
        self.combo.bind("<<ComboboxSelected>>", self.change_language)

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(expand=True, fill="both")

        self.tab_text = tk.Frame(self.notebook)
        self.notebook.add(self.tab_text, text=languages[self.lang]["tab_text"])

        self.label_pw1 = tk.Label(self.tab_text, text=languages[self.lang]["password"])
        self.label_pw1.pack()
        self.entry_pw1 = tk.Entry(self.tab_text, show="*")
        self.entry_pw1.pack(pady=5)

        self.label_input = tk.Label(self.tab_text, text=languages[self.lang]["input_text"])
        self.label_input.pack()
        self.entry_text = tk.Text(self.tab_text, height=5)
        self.entry_text.pack(pady=5)

        self.btn_encrypt_text = tk.Button(self.tab_text, text=languages[self.lang]["encrypt"], command=self.do_encrypt_text)
        self.btn_encrypt_text.pack(pady=5)
        self.btn_decrypt_text = tk.Button(self.tab_text, text=languages[self.lang]["decrypt"], command=self.do_decrypt_text)
        self.btn_decrypt_text.pack(pady=5)

        self.label_output = tk.Label(self.tab_text, text=languages[self.lang]["output_text"])
        self.label_output.pack()
        self.output_text = tk.Text(self.tab_text, height=5, state="normal")
        self.output_text.pack(pady=5)

        self.tab_file = tk.Frame(self.notebook)
        self.notebook.add(self.tab_file, text=languages[self.lang]["tab_file"])

        self.label_pw2 = tk.Label(self.tab_file, text=languages[self.lang]["password"])
        self.label_pw2.pack()
        self.entry_pw2 = tk.Entry(self.tab_file, show="*")
        self.entry_pw2.pack(pady=5)

        self.btn_select_file = tk.Button(self.tab_file, text=languages[self.lang]["select_file"], command=self.select_file)
        self.btn_select_file.pack(pady=10)

        self.btn_encrypt_file = tk.Button(self.tab_file, text=languages[self.lang]["encrypt"], command=self.do_encrypt_file)
        self.btn_encrypt_file.pack(pady=5)
        self.btn_decrypt_file = tk.Button(self.tab_file, text=languages[self.lang]["decrypt"], command=self.do_decrypt_file)
        self.btn_decrypt_file.pack(pady=5)

        self.selected_file = None

        self.btn_info = tk.Button(self, text=languages[self.lang]["btn_info"], command=self.show_info)
        self.btn_info.pack(pady=10)

    def change_language(self, event=None):
        self.lang = self.lang_var.get()
        self.title(languages[self.lang]["title"])
        self.label_lang.config(text=languages[self.lang]["label_lang"])
        self.btn_info.config(text=languages[self.lang]["btn_info"])
        self.notebook.tab(0, text=languages[self.lang]["tab_text"])
        self.notebook.tab(1, text=languages[self.lang]["tab_file"])
        self.label_pw1.config(text=languages[self.lang]["password"])
        self.label_input.config(text=languages[self.lang]["input_text"])
        self.btn_encrypt_text.config(text=languages[self.lang]["encrypt"])
        self.btn_decrypt_text.config(text=languages[self.lang]["decrypt"])
        self.label_output.config(text=languages[self.lang]["output_text"])
        self.label_pw2.config(text=languages[self.lang]["password"])
        self.btn_select_file.config(text=languages[self.lang]["select_file"])
        self.btn_encrypt_file.config(text=languages[self.lang]["encrypt"])
        self.btn_decrypt_file.config(text=languages[self.lang]["decrypt"])

    def show_info(self):
        messagebox.showinfo("Info", languages[self.lang]["info"])

    def do_encrypt_text(self):
        pw = self.entry_pw1.get()
        txt = self.entry_text.get("1.0", "end").strip()
        if not pw or not txt:
            messagebox.showerror("Error", "Bitte Passwort und Text eingeben.")
            return
        try:
            encrypted = encrypt_text(txt, pw)
            self.output_text.delete("1.0", "end")
            self.output_text.insert("end", encrypted)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def do_decrypt_text(self):
        pw = self.entry_pw1.get()
        txt = self.entry_text.get("1.0", "end").strip()
        if not pw or not txt:
            messagebox.showerror("Error", "Bitte Passwort und Text eingeben.")
            return
        try:
            decrypted = decrypt_text(txt, pw)
            self.output_text.delete("1.0", "end")
            self.output_text.insert("end", decrypted)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def select_file(self):
        self.selected_file = filedialog.askopenfilename()
        if self.selected_file:
            messagebox.showinfo("File", f"Ausgewählt: {self.selected_file}")

    def do_encrypt_file(self):
        if not self.selected_file or not self.entry_pw2.get():
            messagebox.showerror("Error", "Bitte Datei auswählen und Passwort eingeben.")
            return
        try:
            encrypt_file(self.selected_file, self.entry_pw2.get())
            messagebox.showinfo("OK", languages[self.lang]["status_done"])
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def do_decrypt_file(self):
        if not self.selected_file or not self.entry_pw2.get():
            messagebox.showerror("Error", "Bitte Datei auswählen und Passwort eingeben.")
            return
        try:
            decrypt_file(self.selected_file, self.entry_pw2.get())
            messagebox.showinfo("OK", languages[self.lang]["status_done"])
        except Exception as e:
            messagebox.showerror("Error", str(e))


def main():
    root = MyApp()
    root.withdraw()

    def start_app():
        root.deiconify()

    splash = SplashScreen(root, on_finish=start_app)
    root.mainloop()


if __name__ == "__main__":
    main()
