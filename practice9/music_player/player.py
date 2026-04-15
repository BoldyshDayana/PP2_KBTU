import pygame
import os
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk  # pip install Pillow

class MusicPlayer:
    def __init__(self):
        # Initialize pygame
        pygame.init()
        pygame.mixer.init()
        
        # Player variables
        self.playlist = []
        self.current_index = 0
        self.is_playing = False
        self.volume = 0.5
        self.music_folder = os.path.join(os.path.dirname(__file__), "music")
        
        # Create music folder if it doesn't exist
        if not os.path.exists(self.music_folder):
            os.makedirs(self.music_folder)
        
        # Create window
        self.root = tk.Tk()
        self.root.title("Music Player")
        self.root.geometry("600x500")
        self.root.configure(bg='#f0f0f0')
        
        # Create UI
        self.setup_ui()
        
        # Bind keyboard
        self.bind_keys()
        
        # Auto-load music
        self.load_music()
    
    def setup_ui(self):
        """Create all UI elements"""
        
        # Title
        title = tk.Label(self.root, text="Music Player", 
                        font=("Arial", 18, "bold"),
                        bg='#f0f0f0', fg='#333')
        title.pack(pady=10)
        
        # Main frame
        main_frame = tk.Frame(self.root, bg='#f0f0f0')
        main_frame.pack(pady=10, padx=20, fill='both', expand=True)
        
        # LEFT SIDE - Music Image
        left_frame = tk.Frame(main_frame, bg='#f0f0f0')
        left_frame.pack(side=tk.LEFT, padx=20)
        
        # Image display
        self.image_label = tk.Label(left_frame, bg='#2c3e50', 
                                   width=200, height=200)
        self.image_label.pack(pady=10)
        self.show_default_image()
        
        # Current song name
        self.song_label = tk.Label(left_frame, text="No song", 
                                  font=("Arial", 10, "bold"),
                                  bg='#f0f0f0', fg='#333', width=30)
        self.song_label.pack(pady=5)
        
        # Control buttons
        btn_frame = tk.Frame(left_frame, bg='#f0f0f0')
        btn_frame.pack(pady=10)
        
        # Button style
        btn_style = {"width": 8, "height": 1, "font": ("Arial", 9, "bold")}
        
        tk.Button(btn_frame, text="⏮", bg='#607D8B', fg='white',
                 command=self.previous, **btn_style).pack(side=tk.LEFT, padx=2)
        tk.Button(btn_frame, text="▶", bg='#4CAF50', fg='white',
                 command=self.play, **btn_style).pack(side=tk.LEFT, padx=2)
        tk.Button(btn_frame, text="⏸", bg='#FF9800', fg='white',
                 command=self.pause, **btn_style).pack(side=tk.LEFT, padx=2)
        tk.Button(btn_frame, text="⏹", bg='#f44336', fg='white',
                 command=self.stop, **btn_style).pack(side=tk.LEFT, padx=2)
        tk.Button(btn_frame, text="⏭", bg='#607D8B', fg='white',
                 command=self.next, **btn_style).pack(side=tk.LEFT, padx=2)
        
        # RIGHT SIDE - Playlist
        right_frame = tk.Frame(main_frame, bg='white', bd=2, relief=tk.SUNKEN)
        right_frame.pack(side=tk.RIGHT, fill='both', expand=True)
        
        # Playlist header
        tk.Label(right_frame, text="Playlist", font=("Arial", 10, "bold"),
                bg='white').pack(pady=5)
        
        # Listbox with scrollbar
        scroll = tk.Scrollbar(right_frame)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.listbox = tk.Listbox(right_frame, yscrollcommand=scroll.set,
                                 font=("Arial", 9), height=12)
        self.listbox.pack(fill='both', expand=True, padx=5, pady=5)
        scroll.config(command=self.listbox.yview)
        
        # Double click to play
        self.listbox.bind('<Double-Button-1>', lambda e: self.play_selected())
        
        # BOTTOM - Volume
        bottom_frame = tk.Frame(self.root, bg='#f0f0f0')
        bottom_frame.pack(pady=10, padx=20, fill='x')
        
        tk.Label(bottom_frame, text="Volume:", bg='#f0f0f0').pack(side=tk.LEFT)
        
        self.volume_slider = tk.Scale(bottom_frame, from_=0, to=100,
                                     orient=tk.HORIZONTAL, length=200,
                                     command=self.change_volume)
        self.volume_slider.set(50)
        self.volume_slider.pack(side=tk.LEFT, padx=10)
        
        # Status bar
        self.status = tk.Label(self.root, text="Ready", bd=1, relief=tk.SUNKEN,
                              anchor='w', bg='#e0e0e0')
        self.status.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Keyboard shortcuts
        shortcuts = "P=Play  S=Stop  Space=Pause  N=Next  B=Previous  Q=Quit"
        tk.Label(self.root, text=shortcuts, font=("Arial", 8),
                bg='#f0f0f0', fg='#999').pack(pady=5)
    
    def show_default_image(self):
        """Show default music image"""
        # Clear old image
        for widget in self.image_label.winfo_children():
            widget.destroy()
        
        # Create canvas with music note
        canvas = tk.Canvas(self.image_label, width=200, height=200,
                          bg='#2c3e50', highlightthickness=0)
        canvas.pack()
        canvas.create_text(100, 100, text="🎵", font=("Arial", 70), fill='#4CAF50')
        canvas.create_text(100, 160, text="Music", font=("Arial", 12), fill='white')
    
    def update_image(self, song_name):
        """Update image for current song"""
        # Clear old
        for widget in self.image_label.winfo_children():
            widget.destroy()
        
        canvas = tk.Canvas(self.image_label, width=200, height=200,
                          bg='#3498db', highlightthickness=0)
        canvas.pack()
        
        # Try to load custom image from images folder
        img_path = os.path.join(os.path.dirname(__file__), "images", f"{song_name}.png")
        
        try:
            if os.path.exists(img_path):
                img = Image.open(img_path)
                img = img.resize((190, 190))
                photo = ImageTk.PhotoImage(img)
                canvas.create_image(100, 100, image=photo)
                canvas.image = photo
            else:
                # Show music note and first letter
                canvas.create_text(100, 80, text="🎵", font=("Arial", 60), fill='white')
                canvas.create_text(100, 140, text=song_name[0].upper() if song_name else "?",
                                  font=("Arial", 30, "bold"), fill='white')
                canvas.create_oval(30, 30, 170, 170, outline='white', width=2)
        except:
            canvas.create_text(100, 100, text="🎵", font=("Arial", 70), fill='white')
    
    def load_music(self):
        """Auto-load music from music folder"""
        self.playlist = []
        self.listbox.delete(0, tk.END)
        
        # Check if music folder exists
        if not os.path.exists(self.music_folder):
            self.status.config(text="Music folder not found!")
            return
        
        # Load MP3 and WAV files
        for file in os.listdir(self.music_folder):
            if file.endswith(('.mp3', '.wav', '.MP3', '.WAV')):
                self.playlist.append(file)
        
        if not self.playlist:
            self.status.config(text="No music found! Add MP3 files to 'music' folder")
            return
        
        self.playlist.sort()
        
        # Add to listbox with numbers
        for i, song in enumerate(self.playlist, 1):
            name = os.path.splitext(song)[0]
            if len(name) > 25:
                name = name[:22] + "..."
            self.listbox.insert(tk.END, f"{i}. {name}")
        
        self.status.config(text=f"Loaded {len(self.playlist)} songs")
        
        # Select first song
        if self.playlist:
            self.current_index = 0
            self.listbox.selection_set(0)
            name = os.path.splitext(self.playlist[0])[0]
            self.song_label.config(text=name)
            self.update_image(name)
    
    def play_selected(self):
        """Play selected song"""
        if self.listbox.curselection():
            self.current_index = self.listbox.curselection()[0]
            self.play()
    
    def play(self):
        """Play current song"""
        if not self.playlist:
            messagebox.showwarning("Warning", "No music files found in 'music' folder!")
            return
        
        song_file = self.playlist[self.current_index]
        song_path = os.path.join(self.music_folder, song_file)
        song_name = os.path.splitext(song_file)[0]
        
        try:
            pygame.mixer.music.load(song_path)
            pygame.mixer.music.play()
            self.is_playing = True
            self.song_label.config(text=song_name)
            self.update_image(song_name)
            self.status.config(text=f"▶ Playing: {song_name}")
        except Exception as e:
            self.status.config(text=f"Error: {e}")
    
    def stop(self):
        """Stop music"""
        pygame.mixer.music.stop()
        self.is_playing = False
        self.status.config(text="⏹ Stopped")
    
    def pause(self):
        """Pause music"""
        pygame.mixer.music.pause()
        self.status.config(text="⏸ Paused")
    
    def unpause(self):
        """Unpause music"""
        pygame.mixer.music.unpause()
        self.status.config(text="▶ Playing")
    
    def next(self):
        """Next song"""
        if self.current_index < len(self.playlist) - 1:
            self.current_index += 1
            self.listbox.selection_clear(0, tk.END)
            self.listbox.selection_set(self.current_index)
            self.listbox.see(self.current_index)
            self.play()
    
    def previous(self):
        """Previous song"""
        if self.current_index > 0:
            self.current_index -= 1
            self.listbox.selection_clear(0, tk.END)
            self.listbox.selection_set(self.current_index)
            self.listbox.see(self.current_index)
            self.play()
    
    def change_volume(self, val):
        """Change volume"""
        volume = float(val) / 100
        pygame.mixer.music.set_volume(volume)
    
    def bind_keys(self):
        """Bind keyboard shortcuts"""
        self.root.bind('<p>', lambda e: self.play())
        self.root.bind('<P>', lambda e: self.play())
        self.root.bind('<s>', lambda e: self.stop())
        self.root.bind('<S>', lambda e: self.stop())
        self.root.bind('<space>', lambda e: self.pause())
        self.root.bind('<n>', lambda e: self.next())
        self.root.bind('<N>', lambda e: self.next())
        self.root.bind('<b>', lambda e: self.previous())
        self.root.bind('<B>', lambda e: self.previous())
        self.root.bind('<q>', lambda e: self.quit())
    
    def quit(self):
        """Quit application"""
        pygame.mixer.music.stop()
        pygame.quit()
        self.root.quit()
        self.root.destroy()
    
    def run(self):
        """Run the player"""
        self.root.protocol("WM_DELETE_WINDOW", self.quit)
        self.root.mainloop()