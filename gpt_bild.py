'''
KI-Bild-Generator im Vollbildmodus (Kiosk)
https://github.com/wolli112/ki-bild-generator

MIT License

Copyright (c) 2024 wolli112

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''
__version__ = '0.1'
__author__ = 'wolli112'

import tkinter as tk
from PIL import ImageTk, Image
from openai import OpenAI
import requests
import io
from tkinter import filedialog
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import os
import shutil
from datetime import datetime
from openaiapikey import OPENAI_API_KEY
from emaildata import *

# Globale Variable für das QR-Code-Bild
img = None

# Funktion zum generieren des Bild anhand des eingegebenen Prompt
def gpt():
    global img  # Deklariere img als eine globale Variable
    
    prompt = input_field.get()
    
    if prompt == "Beende die Anwendung": # Keyword zum Beenden der Anwendung
        beenden()   
    
    openai = OpenAI(api_key=OPENAI_API_KEY)
    model = "dall-e-3"
          
    # Erstelle ein Bild anhand des Prompte
    response = openai.images.generate(prompt=prompt, model=model)

    # URL aus der Antwort extrahieren
    url = response.data[0].url
    
    # Bild aus der Klasse extrahieren
    antwort = requests.get(url)
    bild_bytes = io.BytesIO(antwort.content)
    img = Image.open(bild_bytes)
    img.save("generiert.png") # Speichert das Bild als generiert
    verschieben()
    img.save("bild.png") # Speichert das Bild welches per Mail versendet werden kann
    
    # Größe des Bild für Anzeige anpassen
    breite = 600
    hoehe = 600
    new_img = img.resize((breite, hoehe), Image.Resampling.LANCZOS)
    
    # Konvertieren des PIL-Bild in ein tkinter-Bild
    img_tk = ImageTk.PhotoImage(new_img)

    # Zeigt das Bild in einem Label im Hauptfenster an
    bild_label.config(image=img_tk)
    bild_label.image = img_tk
    input_field.delete(0, "end") # Leert das Prompt Eingabefeld
    
# Bild per E-Mail an eingegebene E-Mail Adresse senden
def sendmail(receiver_email):
    
    # Bild einlesen (angenommen, das Bild ist als "bild.png" im aktuellen Verzeichnis)
    with open('bild.png', 'rb') as f:
        img_data = f.read()
    
    # E-Mail-Nachricht erstellen
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = 'Bild per E-Mail gesendet'
    
    # Textteil der E-Mail hinzufügen
    text = MIMEText('Hallo,\n\nHier ist das Bild, dass Sie vom KI-Bild-Generator angefordert haben:')
    msg.attach(text)
    
    # Bildteil der E-Mail hinzufügen
    image = MIMEImage(img_data, name='bild.png')
    msg.attach(image)
    
    # Verbindung zum SMTP-Server herstellen und E-Mail senden
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
        print('E-Mail erfolgreich gesendet!')
        input_send.delete(0, "end") # Leert das E-Mail Eingabefeld - Datenschutz
        os.remove("bild.png")
    except Exception as e:
        print(f'Fehler beim Senden der E-Mail: {str(e)}')
    finally:
        server.quit()

# Funktion zum Beenden des Anwendung
def beenden():
    root.quit()
    root.destroy()

# Funktion zum verschieben der generierten Bilder - Sicherung
def verschieben():
    
    # Dateiname der vorhandenen Datei
    existing_file = 'generiert.png'
    
    # Zielordner, in dem die Datei gespeichert werden soll
    target_folder = 'save'
    
    # Das aktuelle Datum und Uhrzeit erhalten
    current_datetime = datetime.now()
    formatted_datetime = current_datetime.strftime("%Y-%m-%d_%H-%M-%S")
    
    # Neuer Dateiname mit Datum und Uhrzeit
    new_filename = f"{formatted_datetime}_{existing_file}"
    
    # Ziel-Pfad erstellen
    target_path = os.path.join(target_folder, new_filename)
    
    # Datei kopieren
    shutil.copy(existing_file, target_path)

# HAUPTPROGRAMM

# Erstellen des Hauptfenster
root = tk.Tk()
root.configure(bg="white")
root.title("KI-Bild-Generator mit DALL-E-3 von wolli112")
w, h = root.winfo_screenwidth(), root.winfo_screenheight() # Fenster mit Menü und groß
root.geometry("%dx%d+0+0" % (w, h)) # Fenster mit Menü und groß
root.wm_attributes('-fullscreen','true') # Fenster im Vollbild
#root.overrideredirect(1) # Entfernen der Menüleiste bei Bedarf
root.update()

# Testfeld mit Programmbeschriftung
program_text = tk.Label(root, font=("Arial", 40, "bold"), text="KI-Bild-Generator mit DALL-E-3 von wolli112", bg="white")
program_text.grid(row=1, column=2, columnspan=5, pady=10)

# Erstellen des Eingabefeldes
input_text = tk.Label(root, font=("Arial", 40), text="Prompt eingeben:", bg="white")
input_text.grid(row=2, column=2, columnspan=2, pady=10)
input_field = tk.Entry(root, font=("Arial", 40))
input_field.grid(row=2, column=5, columnspan=2, pady=10)

# Erstellen des "Generieren" Button
submit_button = tk.Button(root, text="Generieren", font=("Arial", 35), command=gpt)
submit_button.grid(row=4, column=2, columnspan=1, pady=10)
    
# Erstellen eines Leerfeld
input_api = tk.Label(root, font=("Arial", 14), text="                                                                              ", bg="white")
input_api.grid(row=1, column=0, columnspan=2, rowspan=5, pady=10)

# Erstellen des "Senden" Button
input_send = tk.Entry(root, font=("Arial", 35))
input_send.grid(row=4, column=6, columnspan=1, pady=10)
send_button = tk.Button(root, text="E-Mail senden", font=("Arial", 35), command=lambda: sendmail(input_send.get()))
send_button.grid(row=4, column=5, columnspan=1, pady=10)

# Feld zum Anzeigen des Bild
bild_label = tk.Label(root)
bild_label.grid(row=5, column=2, columnspan=5, pady=5)

# Aktualisieren das Hauptfenster, um die Größe an den Inhalt anzupassen
root.update_idletasks()

# Hauptschleife fürs Fenster
root.mainloop()
