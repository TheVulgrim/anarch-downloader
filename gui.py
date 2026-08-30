import customtkinter as ctk
import threading
from tkinter import messagebox, filedialog
import queue
import os
from PIL import Image, ImageEnhance

import logic

# --- UI Setup ---
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")
root = ctk.CTk()
root.title("Anarch Downloader")
root.geometry("600x780")
root.resizable(False, False)

current_dir = os.path.dirname(os.path.abspath(__file__))
image_path = os.path.join(current_dir, "Fallen.jpeg")

if os.path.exists(image_path):
    try:
        original_bg = Image.open(image_path)
        enhancer = ImageEnhance.Brightness(original_bg)
        darkened_bg = enhancer.enhance(0.25)
        bg_ctk_image = ctk.CTkImage(light_image=darkened_bg, dark_image=darkened_bg, size=(600, 780))
        bg_label = ctk.CTkLabel(root, text="", image=bg_ctk_image)
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        bg_label.image = bg_ctk_image
    except Exception as e:
        print(f"Background image found but failed to load: {e}")
else:
    print("No background image found — running with plain background. See README for details.")

cancel_event = threading.Event()
heading_font = ctk.CTkFont(family="Road Rage", size=32, weight="bold")
title = ctk.CTkLabel(root, text="Anarch Downloader", font=heading_font, fg_color="transparent")
title.pack(pady=(25, 20))

save_folder = os.path.expanduser("~/Downloads")
gui_queue = queue.Queue()
download_finished = False

QUALITY_OPTIONS = {
    "Best": "bestvideo+bestaudio/best",
    "1080p": "bestvideo[height<=1080]+bestaudio/best[height<=1080]",
    "720p": "bestvideo[height<=720]+bestaudio/best[height<=720]",
    "480p": "bestvideo[height<=480]+bestaudio/best[height<=480]",
    "Audio Only": "bestaudio/best"
}
quality_var = ctk.StringVar(value="Best")


# --- Logic ---

def choose_folder():
    global save_folder
    folder = filedialog.askdirectory()
    if folder:
        save_folder = folder
        folder_label.configure(text=f"{folder}")


def progress_hook(d):
    if cancel_event.is_set():
        raise Exception("Download cancelled by user.")
    if d["status"] == "downloading":
        downloaded = d.get("downloaded_bytes") or 0
        total = d.get("total_bytes") or d.get("total_bytes_estimate")
        speed = d.get("speed")
        eta = d.get("eta")
        speed_down = speed / (1024 * 1024) if speed else 0
        eta_str = f"{eta:.2f}s" if eta else "Unknown"
        if total:
            percentage = (downloaded / total) * 100
            gui_queue.put(("progress", (percentage, f"{percentage:.1f}% | Speed: {speed_down:.2f} MB/s | ETA: {eta_str}")))
    elif d["status"] == "finished":
        print("\ndownload finished")


def cancel_download():
    cancel_event.set()


def postprocessor_hooks(d):
    if d["status"] == "finished":
        print("Post Processing is Done - file is now Ready")
        gui_queue.put(("done", None))


def download_video_thread():
    try:
        selected_format = QUALITY_OPTIONS[quality_var.get()]
        logic.download_video(url.get(), save_folder, progress_hook, postprocessor_hooks, selected_format)
    except Exception as e:
        if cancel_event.is_set():
            gui_queue.put(("cancelled", None))
        else:
            gui_queue.put(("error", str(e)))


def fetch_thumbnail_thread():
    try:
        pil_image = logic.fetch_thumbnail(url.get())
        gui_queue.put(("thumbnail", pil_image))
    except Exception as e:
        gui_queue.put(("error", str(e)))


def start_preview():
    thumbnail_label.configure(text="Loading thumbnail...", image=None)
    thread = threading.Thread(target=fetch_thumbnail_thread)
    thread.start()


def start_download():
    global download_finished
    if not save_folder:
        messagebox.showerror("Error", "Please choose a save folder before downloading.")
        return
    download_finished = False
    cancel_event.clear()
    thread = threading.Thread(target=download_video_thread)
    thread.start()
    Ui_Button.configure(state="disabled")


def process_queue():
    try:
        while True:
            msg_type, data = gui_queue.get_nowait()
            if msg_type == "progress":
                percentage, text = data
                progress_bar.set(percentage / 100)
                label.configure(text=text, text_color="gray")
            elif msg_type == "done":
                global download_finished
                if not download_finished:
                    download_finished = True
                    messagebox.showinfo("Successful Operation", "Download Complete")
                    label.configure(text="Download complete", text_color="#4CAF50")
                    Ui_Button.configure(state="normal")
            elif msg_type == "thumbnail":
                pil_image = data
                ctk_img = ctk.CTkImage(light_image=pil_image, dark_image=pil_image, size=(300, 200))
                thumbnail_label.configure(image=ctk_img, text="")
                thumbnail_label.image = ctk_img
            elif msg_type == "error":
                label.configure(text=f"Error: {data}", text_color="red")
                Ui_Button.configure(state="normal")
            elif msg_type == "cancelled":
                messagebox.showinfo("Cancelled", "Download Cancelled")
                label.configure(text="Cancelled by user", text_color="red")
                Ui_Button.configure(state="normal")
                progress_bar.set(0)
    except queue.Empty:
        pass
    root.after(100, process_queue)


# --- Layout ---

card1 = ctk.CTkFrame(root, corner_radius=10, fg_color="transparent")
card1.pack(pady=(0, 15), padx=20, fill="x")

input_frame = ctk.CTkFrame(card1, fg_color="transparent")
input_frame.pack(pady=15, padx=15, fill="x")

url = ctk.CTkEntry(input_frame, placeholder_text="Enter YouTube URL here...", height=40, corner_radius=8)
url.pack(side="left", expand=True, fill="x", padx=(0, 10))

preview_button = ctk.CTkButton(input_frame, text="Load Preview", command=start_preview, width=110, height=40, corner_radius=8)
preview_button.pack(side="right")

thumbnail_frame = ctk.CTkFrame(card1, width=320, height=200, corner_radius=8, fg_color=("gray80", "gray15"))
thumbnail_frame.pack(pady=(0, 15))
thumbnail_frame.pack_propagate(False)

thumbnail_label = ctk.CTkLabel(thumbnail_frame, text="Thumbnail Preview", text_color="gray")
thumbnail_label.place(relx=0.5, rely=0.5, anchor="center")

card2 = ctk.CTkFrame(root, corner_radius=10, fg_color="transparent")
card2.pack(pady=10, padx=20, fill="x")

quality_frame = ctk.CTkFrame(card2, fg_color="transparent")
quality_frame.pack(pady=(15, 10), padx=15, fill="x")
ctk.CTkLabel(quality_frame, text="Format Quality:", font=("Verdana", 12, "bold")).pack(side="left")
quality_menu = ctk.CTkOptionMenu(quality_frame, values=list(QUALITY_OPTIONS.keys()), variable=quality_var, width=150)
quality_menu.pack(side="right")

folder_frame = ctk.CTkFrame(card2, fg_color="transparent")
folder_frame.pack(pady=(0, 15), padx=15, fill="x")
folder_button = ctk.CTkButton(folder_frame, text="Change Folder", command=choose_folder, width=120, fg_color="gray30", hover_color="gray40")
folder_button.pack(side="left", padx=(0, 15))
folder_label = ctk.CTkLabel(folder_frame, text=f"{save_folder}", text_color="gray", justify="left")
folder_label.pack(side="left", fill="x", expand=True)

card3 = ctk.CTkFrame(root, fg_color="transparent")
card3.pack(pady=10, padx=20, fill="x")

button_frame = ctk.CTkFrame(card3, fg_color="transparent")
button_frame.pack(fill="x", pady=(10, 15))

Ui_Button = ctk.CTkButton(button_frame, text="Download Video", command=start_download, height=45, corner_radius=8, font=("Verdana", 14, "bold"))
Ui_Button.pack(side="left", expand=True, fill="x", padx=(0, 10))

cancel_button = ctk.CTkButton(button_frame, text="Cancel", command=cancel_download, fg_color="#c62828", hover_color="#b71c1c", width=120, height=45, corner_radius=8, font=("Verdana", 14, "bold"))
cancel_button.pack(side="right")

progress_bar = ctk.CTkProgressBar(card3, height=10, corner_radius=5)
progress_bar.set(0)
progress_bar.pack(fill="x", pady=(0, 10))

label = ctk.CTkLabel(card3, text="Waiting for URL...", text_color="gray", font=("Verdana", 11))
label.pack()

process_queue()
root.mainloop()
