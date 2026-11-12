import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk


class BMPImageViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("BMP Image Viewer")
        self.root.geometry("720x620")

        # Keep a reference to the displayed image
        self.photo = None

        # Create the canvas used to display the image
        self.canvas = tk.Canvas(
            root,
            width=704,
            height=576,
            bg="lightgray"
        )
        self.canvas.pack(padx=5, pady=5)

        # Create the menu bar
        menubar = tk.Menu(root)

        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(
            label="Open File",
            command=self.open_file
        )
        file_menu.add_separator()
        file_menu.add_command(
            label="Exit",
            command=root.destroy
        )

        menubar.add_cascade(label="File", menu=file_menu)
        root.config(menu=menubar)

    def open_file(self):
        # Ask the user to select a BMP file
        filename = filedialog.askopenfilename(
            title="Open BMP Image",
            filetypes=[("BMP files", "*.bmp"), ("All files", "*.*")]
        )

        # Do nothing if the user cancels
        if not filename:
            return

        try:
            # Read and decode the BMP image
            with Image.open(filename) as image:
                if image.format != "BMP":
                    raise ValueError("Please select a BMP image.")

                if image.size[0] > 704 or image.size[1] > 576:
                    raise ValueError(
                        "Image dimensions must not exceed 704 x 576."
                    )

                if image.mode != "RGB":
                    raise ValueError(
                        "Only 24-bit RGB BMP images are supported."
                    )

                if image.info.get("compression", 0) != 0:
                    raise ValueError(
                        "Only uncompressed BMP images are supported."
                    )

                image.load()
                decoded_image = image.copy()

            # Convert the image for display in Tkinter
            new_photo = ImageTk.PhotoImage(decoded_image)

            # Clear the previous image before displaying the new one
            self.canvas.delete("all")
            self.canvas.config(
                width=decoded_image.width,
                height=decoded_image.height
            )

            # Display the new image at its original size
            self.photo = new_photo
            self.canvas.create_image(
                0, 0,
                anchor=tk.NW,
                image=self.photo
            )

            # Update the window title
            self.root.title(f"BMP Image Viewer - {filename}")

        except Exception as error:
            messagebox.showerror(
                "Error Opening Image",
                str(error)
            )


if __name__ == "__main__":
    root = tk.Tk()
    app = BMPImageViewer(root)
    root.mainloop()
