import cv2
import numpy as np
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk

class SteganographyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CyberSteg - Image Steganography Suite")
        self.root.geometry("1000x600")  # Smaller initial window size
        self.root.configure(bg="#0a0a0a")
        
        # Initialize image paths
        self.cover_path = ""
        self.secret_path = ""
        self.hidden_image_path = "hidden_image.png"
        self.extracted_image_path = "extracted_image.png"
        
        self.setup_styles()
        self.create_scrollable_container()
        self.create_widgets()
        self.setup_layout()
        self.bind_mouse_scroll()

    def setup_styles(self):
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Color scheme
        self.bg_color = "#0a0a0a"
        self.accent_color = "#00f3ff"
        self.secondary_color = "#1a1a1a"
        self.text_color = "#ffffff"
        
        # Configure styles
        self.style.configure("TFrame", background=self.bg_color)
        self.style.configure("TLabel", background=self.bg_color, foreground=self.text_color)
        self.style.configure("TButton", 
                           background=self.secondary_color, 
                           foreground=self.text_color,
                           borderwidth=1,
                           relief="flat",
                           font=("Roboto", 10),
                           padding=8)
        self.style.map("TButton",
                     background=[("active", self.accent_color), ("disabled", "#404040")],
                     foreground=[("active", self.bg_color)])
        
        self.style.configure("Accent.TButton", 
                           background=self.accent_color, 
                           foreground=self.bg_color,
                           font=("Roboto Medium", 12),
                           padding=10)
        self.style.map("Accent.TButton",
                     background=[("active", "#00c4cc")])
        
        self.style.configure("TLabelframe", 
                           background=self.bg_color, 
                           foreground=self.accent_color,
                           font=("Roboto Medium", 12))
        self.style.configure("TLabelframe.Label", 
                           background=self.bg_color, 
                           foreground=self.accent_color)

    def create_scrollable_container(self):
        # Create main container with scrollbar
        self.canvas = tk.Canvas(self.root, bg=self.bg_color, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

    def bind_mouse_scroll(self):
        # Bind mouse wheel scrolling for all platforms
        self.canvas.bind_all("<MouseWheel>", self._on_mouse_wheel)
        self.canvas.bind_all("<Button-4>", self._on_mouse_wheel)  # Linux scroll up
        self.canvas.bind_all("<Button-5>", self._on_mouse_wheel)  # Linux scroll down

    def _on_mouse_wheel(self, event):
        # Cross-platform mouse wheel scrolling
        if event.num == 4 or event.delta > 0:
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5 or event.delta < 0:
            self.canvas.yview_scroll(1, "units")

    def create_widgets(self):
        # Main content frame inside scrollable container
        self.main_frame = ttk.Frame(self.scrollable_frame, padding=20)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Header
        self.header = ttk.Label(self.main_frame, 
                              text="CYBERSTEG", 
                              font=("Roboto Black", 24),
                              foreground=self.accent_color)
        self.header.grid(row=0, column=0, columnspan=2, pady=(0, 20))

        # Image selection section
        self.selection_frame = ttk.LabelFrame(self.main_frame, 
                                            text=" IMAGE SELECTION ",
                                            padding=20)
        self.selection_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=10)

        # Cover image panel
        self.cover_panel = ttk.Frame(self.selection_frame)
        self.cover_panel.grid(row=0, column=0, padx=15)
        ttk.Label(self.cover_panel, text="Cover Image", font=("Roboto Medium", 11)).pack(pady=5)
        self.cover_img_label = ttk.Label(self.cover_panel, background="#151515")
        self.cover_img_label.pack(pady=5)
        self.cover_btn = ttk.Button(self.cover_panel, 
                                  text="Select Cover Image", 
                                  command=self.select_cover,
                                  style="Accent.TButton")
        self.cover_btn.pack(pady=10, ipadx=20)

        # Secret image panel
        self.secret_panel = ttk.Frame(self.selection_frame)
        self.secret_panel.grid(row=0, column=1, padx=15)
        ttk.Label(self.secret_panel, text="Secret Image", font=("Roboto Medium", 11)).pack(pady=5)
        self.secret_img_label = ttk.Label(self.secret_panel, background="#151515")
        self.secret_img_label.pack(pady=5)
        self.secret_btn = ttk.Button(self.secret_panel, 
                                   text="Select Secret Image", 
                                   command=self.select_secret,
                                   style="Accent.TButton")
        self.secret_btn.pack(pady=10, ipadx=20)

        # Action buttons
        self.action_frame = ttk.Frame(self.main_frame)
        self.action_frame.grid(row=2, column=0, columnspan=2, pady=25)
        self.hide_btn = ttk.Button(self.action_frame, 
                                 text="ENCODE IMAGE", 
                                 command=self.hide_image,
                                 style="Accent.TButton")
        self.hide_btn.grid(row=0, column=0, padx=15)
        self.extract_btn = ttk.Button(self.action_frame, 
                                    text="DECODE IMAGE", 
                                    command=self.extract_image,
                                    style="Accent.TButton")
        self.extract_btn.grid(row=0, column=1, padx=15)

        # Results section
        self.results_frame = ttk.LabelFrame(self.main_frame, 
                                          text=" RESULTS ",
                                          padding=20)
        self.results_frame.grid(row=3, column=0, columnspan=2, sticky="nsew", pady=10)

        # Hidden image
        self.hidden_panel = ttk.Frame(self.results_frame)
        self.hidden_panel.grid(row=0, column=0, padx=15)
        ttk.Label(self.hidden_panel, text="Encoded Image", font=("Roboto Medium", 11)).pack(pady=5)
        self.hidden_img_label = ttk.Label(self.hidden_panel, background="#151515")
        self.hidden_img_label.pack(pady=5)

        # Extracted image
        self.extracted_panel = ttk.Frame(self.results_frame)
        self.extracted_panel.grid(row=0, column=1, padx=15)
        ttk.Label(self.extracted_panel, text="Decoded Image", font=("Roboto Medium", 11)).pack(pady=5)
        self.extracted_img_label = ttk.Label(self.extracted_panel, background="#151515")
        self.extracted_img_label.pack(pady=5)

    def setup_layout(self):
        # Configure grid weights
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=1)
        self.selection_frame.columnconfigure(0, weight=1)
        self.selection_frame.columnconfigure(1, weight=1)
        self.results_frame.columnconfigure(0, weight=1)
        self.results_frame.columnconfigure(1, weight=1)

    def select_cover(self):
        self.cover_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
        if self.cover_path:
            self.display_image(self.cover_path, self.cover_img_label)

    def select_secret(self):
        self.secret_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
        if self.secret_path:
            self.display_image(self.secret_path, self.secret_img_label)

    def display_image(self, image_path, label):
        try:
            img = Image.open(image_path)
            img.thumbnail((300, 300))  # Maintain aspect ratio
            photo = ImageTk.PhotoImage(img)
            label.configure(image=photo)
            label.image = photo  # Keep reference
            label.configure(background="#151515")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load image: {str(e)}")

    def hide_image(self):
        if not self.cover_path or not self.secret_path:
            messagebox.showwarning("Warning", "Please select both images first!")
            return
        
        try:
            cover_img = cv2.imread(self.cover_path)
            secret_img = cv2.imread(self.secret_path)
            
            # Resize secret image to match cover dimensions
            secret_img = cv2.resize(secret_img, (cover_img.shape[1], cover_img.shape[0]))
            
            # Perform steganography
            hidden_img = (cover_img & 0b11110000) | (secret_img >> 4)
            cv2.imwrite(self.hidden_image_path, hidden_img)
            
            self.display_image(self.hidden_image_path, self.hidden_img_label)
            messagebox.showinfo("Success", "Image encoded successfully!\nOutput: hidden_image.png")
        except Exception as e:
            messagebox.showerror("Error", f"Encoding failed: {str(e)}")

    def extract_image(self):
        try:
            hidden_img = cv2.imread(self.hidden_image_path)
            extracted_img = (hidden_img & 0b00001111) << 4
            cv2.imwrite(self.extracted_image_path, extracted_img)
            self.display_image(self.extracted_image_path, self.extracted_img_label)
            messagebox.showinfo("Success", "Image decoded successfully!\nOutput: extracted_image.png")
        except Exception as e:
            messagebox.showerror("Error", f"Decoding failed: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = SteganographyApp(root)
    root.mainloop()