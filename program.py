import os
import sys
import tkinter as tk
from tkinter import filedialog, Toplevel, Label
import ffmpeg
import threading

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

class VideoEditorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Simple Video Editor")
        self.root.geometry("700x400")

        self.filepath = ""

        self.label = tk.Label(root, text="Wybierz plik")
        self.label.pack(pady=10)

        self.select_button = tk.Button(root, text="Wybierz plik", command=self.select_file)
        self.select_button.pack(pady=10)

        self.extract_audio_button = tk.Button(root, text="Wyciągnij audio z video", command=self.extract_audio)
        self.extract_audio_button.pack(pady=10)

        self.start_time_label = tk.Label(root, text="Początek materiału w formacie HH:MM:SS")
        self.start_time_label.pack(pady=10)
        self.start_time_entry = tk.Entry(root)
        self.start_time_entry.pack(pady=5)

        self.end_time_label = tk.Label(root, text="Koniec materiału w formacie HH:MM:SS")
        self.end_time_label.pack(pady=10)
        self.end_time_entry = tk.Entry(root)
        self.end_time_entry.pack(pady=5)

        self.cut_button = tk.Button(root, text="Przytnij materiał", command=self.cut_media)
        self.cut_button.pack(pady=10)


    def select_file(self):
        self.filepath = filedialog.askopenfilename(filetypes=[("All files", "*.*")])
        self.label.config(text=self.filepath)

    def cut_media(self):
        if self.filepath:
            start_time = self.start_time_entry.get()
            end_time = self.end_time_entry.get()
            file_extension = os.path.splitext(self.filepath)[1]
            output_file = filedialog.asksaveasfilename(defaultextension=file_extension,
                                                       filetypes=[("All files", "*.*")])
            if output_file:
                self.show_processing_popup("Przetwarzam...")
                threading.Thread(target=self.process_cut_media, args=(start_time, end_time, output_file)).start()

    def extract_audio(self):
        if self.filepath:
            output_file = filedialog.asksaveasfilename(defaultextension=".mp3",
                                                       filetypes=[("All files", "*.*")])
            if output_file:
                self.show_processing_popup("Wyciagam audio...")
                threading.Thread(target=self.process_extract_audio, args=(output_file,)).start()

    def show_processing_popup(self, message):
        self.processing_popup = Toplevel(self.root)
        self.processing_popup.title("Przetwarzam...")
        Label(self.processing_popup, text=message).pack(pady=20, padx=20)

        # Center the popup relative to the main window
        self.processing_popup.update_idletasks()
        popup_width = self.processing_popup.winfo_width()
        popup_height = self.processing_popup.winfo_height()
        main_width = self.root.winfo_width()
        main_height = self.root.winfo_height()
        main_x = self.root.winfo_x()
        main_y = self.root.winfo_y()

        popup_x = main_x + (main_width // 2) - (popup_width // 2)
        popup_y = main_y + (main_height // 2) - (popup_height // 2)

        self.processing_popup.geometry(f"{popup_width}x{popup_height}+{popup_x}+{popup_y}")

    def process_cut_media(self, start_time, end_time, output_file):
        try:
            cut_media(self.filepath, start_time, end_time, output_file)
            self.label.config(text=f"Materiał przycięty!: {output_file}")
        except Exception as e:
            self.label.config(text=f"Wystapil blad: {e}")
        finally:
            self.processing_popup.destroy()

    def process_extract_audio(self, output_file):
        try:
            extract_audio(self.filepath, output_file)
            self.label.config(text=f"Wyciągnięcie audio zakończone pomyślnie: {output_file}")
        except Exception as e:
            self.label.config(text=f"Wystapil blad: {e}")
        finally:
            self.processing_popup.destroy()

def cut_media(input_file, start_time, end_time, output_file):
    file_extension = os.path.splitext(input_file)[1].lower()
    if file_extension in ['.mp4', '.mkv', '.avi']:
        codec = 'copy'  # Copy both audio and video streams
    elif file_extension in ['.mp3', '.wav', '.aac']:
        codec = 'copy'  # Copy the audio stream
    else:
        raise ValueError(f"Unsupported file format: {file_extension}")

    (
        ffmpeg
        .input(input_file, ss=start_time, to=end_time)
        .output(output_file, c=codec, y=None)
        .run()  # Suppress the output
    )

def extract_audio(input_file, output_file):
    (
        ffmpeg
        .input(input_file)
        .output(output_file, acodec='libmp3lame', y=None)
        .run()  # Suppress the output
    )

if __name__ == "__main__":
    ffmpeg_path = resource_path("ffmpeg.exe")
    root = tk.Tk()
    app = VideoEditorApp(root)
    root.mainloop()
