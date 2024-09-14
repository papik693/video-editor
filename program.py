import os
import sys
import tkinter as tk
from tkinter import filedialog, Toplevel, Label
from tkinter import ttk  # Import ttk for Notebook
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
        self.root.geometry("700x500")

        # Create a Notebook
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True)

        # Create frames for tabs
        self.tab1 = tk.Frame(self.notebook)
        self.tab2 = tk.Frame(self.notebook)
        self.tab3 = tk.Frame(self.notebook)
        self.tab4 = tk.Frame(self.notebook)  

        # Add tabs to the notebook
        self.notebook.add(self.tab1, text='Wyciągnij Audio')
        self.notebook.add(self.tab2, text='Przytnij Materiał')
        self.notebook.add(self.tab3, text='Zapętlij Materiał')
        self.notebook.add(self.tab4, text='Połącz Pliki') 

        # Initialize variables
        self.filepath_tab1 = ""
        self.filepath_tab2 = ""
        self.filepath_tab3 = ""
        self.filepath_tab4_1 = ""  
        self.filepath_tab4_2 = ""  

        # Build the tabs
        self.extract_tab()
        self.cut_tab()
        self.loop_tab()
        self.concat_tab()  

    def extract_tab(self):
        # Widgets for the first tab (Extract Audio)
        self.label1 = tk.Label(self.tab1, text="Wybierz plik")
        self.label1.pack(pady=10)

        self.select_button1 = tk.Button(self.tab1, text="Wybierz plik", command=self.select_file_tab1)
        self.select_button1.pack(pady=10)

        self.extract_audio_button = tk.Button(self.tab1, text="Wyciągnij audio z video", command=self.extract_audio)
        self.extract_audio_button.pack(pady=10)

    def cut_tab(self):
        # Widgets for the second tab (Cut Media)
        self.label2 = tk.Label(self.tab2, text="Wybierz plik")
        self.label2.pack(pady=10)

        self.select_button2 = tk.Button(self.tab2, text="Wybierz plik", command=self.select_file_tab2)
        self.select_button2.pack(pady=10)

        self.start_time_label = tk.Label(self.tab2, text="Początek materiału w formacie HH:MM:SS")
        self.start_time_label.pack(pady=10)
        self.start_time_entry = tk.Entry(self.tab2)
        self.start_time_entry.pack(pady=5)

        self.end_time_label = tk.Label(self.tab2, text="Koniec materiału w formacie HH:MM:SS")
        self.end_time_label.pack(pady=10)
        self.end_time_entry = tk.Entry(self.tab2)
        self.end_time_entry.pack(pady=5)

        self.cut_button = tk.Button(self.tab2, text="Przytnij materiał", command=self.cut_media)
        self.cut_button.pack(pady=10)

    def loop_tab(self):
        # Widgets for the third tab (Loop Media)
        self.label3 = tk.Label(self.tab3, text="Wybierz plik")
        self.label3.pack(pady=10)

        self.select_button3 = tk.Button(self.tab3, text="Wybierz plik", command=self.select_file_tab3)
        self.select_button3.pack(pady=10)

        self.duration_label = tk.Label(self.tab3, text="Docelowy czas trwania materiału w formacie HH:MM:SS")
        self.duration_label.pack(pady=10)
        self.duration_entry = tk.Entry(self.tab3)
        self.duration_entry.pack(pady=5)

        self.loop_button = tk.Button(self.tab3, text="Zapętlij Materiał", command=self.loop_media)
        self.loop_button.pack(pady=10)

    def concat_tab(self):
        # Widgets for the fourth tab (Concatenate Files)
        self.label4 = tk.Label(self.tab4, text="Wybierz pierwszy plik")
        self.label4.pack(pady=10)

        self.select_button4_1 = tk.Button(self.tab4, text="Wybierz pierwszy plik", command=self.select_file_tab4_1)
        self.select_button4_1.pack(pady=10)

        self.label4_2 = tk.Label(self.tab4, text="Wybierz drugi plik")
        self.label4_2.pack(pady=10)

        self.select_button4_2 = tk.Button(self.tab4, text="Wybierz drugi plik", command=self.select_file_tab4_2)
        self.select_button4_2.pack(pady=10)

        self.concat_button = tk.Button(self.tab4, text="Połącz pliki", command=self.concat_media)
        self.concat_button.pack(pady=20)

    def select_file_tab1(self):
        self.filepath_tab1 = filedialog.askopenfilename(filetypes=[("All files", "*.*")])
        self.label1.config(text=self.filepath_tab1)

    def select_file_tab2(self):
        self.filepath_tab2 = filedialog.askopenfilename(filetypes=[("All files", "*.*")])
        self.label2.config(text=self.filepath_tab2)

    def select_file_tab3(self):
        self.filepath_tab3 = filedialog.askopenfilename(filetypes=[("All files", "*.*")])
        self.label3.config(text=self.filepath_tab3)

    def select_file_tab4_1(self):
        self.filepath_tab4_1 = filedialog.askopenfilename(filetypes=[("All files", "*.*")])
        self.label4.config(text=f"Pierwszy plik: {self.filepath_tab4_1}")

    def select_file_tab4_2(self):
        self.filepath_tab4_2 = filedialog.askopenfilename(filetypes=[("All files", "*.*")])
        self.label4_2.config(text=f"Drugi plik: {self.filepath_tab4_2}")

    def cut_media(self):
        if self.filepath_tab2:
            start_time = self.start_time_entry.get()
            end_time = self.end_time_entry.get()
            file_extension = os.path.splitext(self.filepath_tab2)[1]
            output_file = filedialog.asksaveasfilename(defaultextension=file_extension,
                                                       filetypes=[("All files", "*.*")])
            if output_file:
                self.show_processing_popup("Przetwarzam...")
                threading.Thread(target=self.process_cut_media, args=(self.filepath_tab2, start_time, end_time, output_file)).start()

    def extract_audio(self):
        if self.filepath_tab1:
            output_file = filedialog.asksaveasfilename(defaultextension=".mp3",
                                                       filetypes=[("All files", "*.*")])
            if output_file:
                self.show_processing_popup("Wyciągam audio...")
                threading.Thread(target=self.process_extract_audio, args=(self.filepath_tab1, output_file)).start()

    def loop_media(self):
        if self.filepath_tab3:
            total_duration_str = self.duration_entry.get()
            if not total_duration_str:
                self.label3.config(text="Proszę podać docelowy czas trwania.")
                return

            # Validate the total_duration_str
            if not self.validate_time_format(total_duration_str):
                self.label3.config(text="Nieprawidłowy format czasu. Użyj HH:MM:SS.")
                return

            file_extension = os.path.splitext(self.filepath_tab3)[1]
            output_file = filedialog.asksaveasfilename(defaultextension=file_extension,
                                                       filetypes=[("All files", "*.*")])
            if output_file:
                self.show_processing_popup("Przetwarzam...")
                threading.Thread(target=self.process_loop_media, args=(self.filepath_tab3, total_duration_str, output_file)).start()

    def concat_media(self):
        if self.filepath_tab4_1 and self.filepath_tab4_2:
            file_extension = os.path.splitext(self.filepath_tab4_1)[1]
            output_file = filedialog.asksaveasfilename(defaultextension=file_extension,
                                                       filetypes=[("All files", "*.*")])
            if output_file:
                self.show_processing_popup("Łączenie plików...")
                threading.Thread(target=self.process_concat_media, args=(self.filepath_tab4_1, self.filepath_tab4_2, output_file)).start()
        else:
            self.label4.config(text="Proszę wybrać oba pliki do połączenia.")

    def validate_time_format(self, time_str):
        # Simple validation for HH:MM:SS format
        parts = time_str.strip().split(':')
        if len(parts) != 3:
            return False
        try:
            h, m, s = parts
            int(h)
            int(m)
            float(s)
            return True
        except ValueError:
            return False

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

    def process_cut_media(self, filepath, start_time, end_time, output_file):
        try:
            cut_media(filepath, start_time, end_time, output_file)
            self.label2.config(text=f"Materiał przycięty!: {output_file}")
        except Exception as e:
            self.label2.config(text=f"Wystąpił błąd: {e}")
        finally:
            self.processing_popup.destroy()

    def process_extract_audio(self, filepath, output_file):
        try:
            extract_audio(filepath, output_file)
            self.label1.config(text=f"Wyciągnięcie audio zakończone pomyślnie: {output_file}")
        except Exception as e:
            self.label1.config(text=f"Wystąpił błąd: {e}")
        finally:
            self.processing_popup.destroy()

    def process_loop_media(self, filepath, total_duration_str, output_file):
        try:
            loop_media(filepath, total_duration_str, output_file)
            self.label3.config(text=f"Zapętlanie zakończone pomyślnie: {output_file}")
        except Exception as e:
            self.label3.config(text=f"Wystąpił błąd: {e}")
        finally:
            self.processing_popup.destroy()

    def process_concat_media(self, filepath1, filepath2, output_file):
        try:
            concat_media(filepath1, filepath2, output_file)
            self.label4.config(text=f"Połączenie zakończone pomyślnie: {output_file}")
        except Exception as e:
            self.label4.config(text=f"Wystąpił błąd: {e}")
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
        .run()
    )

def extract_audio(input_file, output_file):
    (
        ffmpeg
        .input(input_file)
        .output(output_file, acodec='libmp3lame', y=None)
        .run()
    )

def loop_media(input_file, total_duration_str, output_file):
    # Use ffmpeg with -stream_loop -1 and -t total_duration_str
    file_extension = os.path.splitext(input_file)[1].lower()
    if file_extension in ['.mp4', '.mkv', '.avi', '.mp3', '.wav', '.aac']:
        codec = 'copy'  # Copy streams
    else:
        raise ValueError(f"Unsupported file format: {file_extension}")

    (
        ffmpeg
        .input(input_file, stream_loop=-1)
        .output(output_file, c=codec, t=total_duration_str, y=None)
        .run()
    )
def concat_media(input_file1, input_file2, output_file):
    file_extension1 = os.path.splitext(input_file1)[1].lower()
    file_extension2 = os.path.splitext(input_file2)[1].lower()

    if file_extension1 != file_extension2:
        raise ValueError("Pliki muszą być tego samego formatu.")

    # Check if the file format is supported
    if file_extension1 not in ['.mp4', '.mkv', '.ts', '.mp3', '.wav', '.aac']:
        raise ValueError(f"Unsupported file format: {file_extension1}")

    # Create a temporary file list for the concat demuxer
    with open('file_list.txt', 'w', encoding='utf-8') as f:
        f.write(f"file '{input_file1}'\n")
        f.write(f"file '{input_file2}'\n")

    try:
        # Use FFmpeg concat demuxer
        (
            ffmpeg
            .input('file_list.txt', format='concat', safe=0)
            .output(output_file, c='copy', y=None)
            .run()
        )
    finally:
        # Remove the temporary file list
        os.remove('file_list.txt')

if __name__ == "__main__":
    ffmpeg_path = resource_path("ffmpeg.exe")
    root = tk.Tk()
    app = VideoEditorApp(root)
    root.mainloop()
