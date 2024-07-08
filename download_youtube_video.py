import tkinter as tk
from tkinter import ttk, messagebox
import yt_dlp
import threading
import queue
import re

# File d'attente pour les téléchargements
download_queue = queue.Queue()
current_download = None

def clean_ansi(text):
    ansi_escape = re.compile(r'\x1B[@-_][0-?]*[ -/]*[@-~]')
    return ansi_escape.sub('', text)

def progress_hook(d):
    if d['status'] == 'downloading':
        p = clean_ansi(d['_percent_str'].strip())
        progress_var.set(p)
        progress_bar['value'] = float(p.strip('%'))
        step_var.set(f"Téléchargement: {d['filename']} à {p}")
    elif d['status'] == 'finished':
        step_var.set("Fusion des fichiers...")

def download_video():
    global current_download
    while not download_queue.empty():
        current_download = download_queue.get()
        url, resolution, is_playlist = current_download

        ydl_opts = {
            'format': f'bestvideo[height<={resolution[:-1]}]+bestaudio/best[height<={resolution[:-1]}]',
            'merge_output_format': 'mp4',
            'progress_hooks': [progress_hook]
        }

        if is_playlist:
            ydl_opts['noplaylist'] = False
        else:
            ydl_opts['noplaylist'] = True

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            messagebox.showinfo("Succès", f"Téléchargement terminé: {url}")
        except Exception as e:
            messagebox.showerror("Erreur", f"Une erreur s'est produite: {e}")

        download_queue.task_done()
        current_download = None
        update_queue_list()
        progress_bar['value'] = 0
        progress_var.set("0%")
        step_var.set("Prêt")

def add_to_queue():
    url = url_entry.get()
    resolution = resolution_var.get()
    is_playlist = playlist_var.get()

    if not url:
        messagebox.showerror("Erreur", "Veuillez entrer une URL valide.")
        return

    download_queue.put((url, resolution, is_playlist))
    update_queue_list()

def start_download():
    if current_download is None and not download_queue.empty():
        threading.Thread(target=download_video, daemon=True).start()

def update_queue_list():
    queue_list.delete(0, tk.END)
    for i, item in enumerate(list(download_queue.queue)):
        url, resolution, is_playlist = item
        status = "En attente"
        if i == 0 and current_download:
            status = "En cours"
        queue_list.insert(tk.END, f"{url} - {resolution} - {'Playlist' if is_playlist else 'Vidéo'} - {status}")

# Création de la fenêtre principale
root = tk.Tk()
root.title("Téléchargeur de vidéos YouTube")

# URL de la vidéo
tk.Label(root, text="URL de la vidéo YouTube:").grid(row=0, column=0, padx=10, pady=10)
url_entry = tk.Entry(root, width=50)
url_entry.grid(row=0, column=1, padx=10, pady=10)

# Sélection de la résolution
tk.Label(root, text="Sélectionnez la résolution:").grid(row=1, column=0, padx=10, pady=10)
resolution_var = tk.StringVar(value="1080p")
resolution_menu = ttk.Combobox(root, textvariable=resolution_var, values=["1080p", "720p", "4k"], state="readonly")
resolution_menu.grid(row=1, column=1, padx=10, pady=10)

# Option pour télécharger une playlist
playlist_var = tk.BooleanVar()
playlist_check = tk.Checkbutton(root, text="Télécharger comme playlist", variable=playlist_var)
playlist_check.grid(row=2, column=0, columnspan=2, padx=10, pady=10)

# Barre de progression
progress_var = tk.StringVar(value="0%")
progress_bar = ttk.Progressbar(root, orient="horizontal", length=400, mode="determinate", maximum=100)
progress_bar.grid(row=3, column=0, columnspan=2, padx=10, pady=10)
progress_label = tk.Label(root, textvariable=progress_var)
progress_label.grid(row=4, column=0, columnspan=2)

# État de l'étape en cours
step_var = tk.StringVar(value="Prêt")
step_label = tk.Label(root, textvariable=step_var)
step_label.grid(row=5, column=0, columnspan=2)

# Liste d'attente des téléchargements
queue_list = tk.Listbox(root, height=10, width=80)
queue_list.grid(row=6, column=0, columnspan=2, padx=10, pady=10)

# Bouton pour ajouter à la file d'attente
add_button = tk.Button(root, text="Ajouter à la liste", command=add_to_queue)
add_button.grid(row=7, column=0, padx=10, pady=10)

# Bouton pour démarrer les téléchargements
download_button = tk.Button(root, text="Télécharger", command=start_download)
download_button.grid(row=7, column=1, padx=10, pady=10)

# Lancer la boucle principale de l'interface
root.mainloop()
