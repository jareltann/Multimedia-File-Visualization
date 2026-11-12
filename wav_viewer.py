import sys
import wave
import struct
import tkinter as tk
from tkinter import filedialog, messagebox


class WAVViewer:
    """stereo PCM WAV viewer that draws waveforms using Tkinter Canvas"""

    BG = "#ffffff"
    AXIS = "#8a8a8a"
    LEFT_COLOR = "#2563eb"
    RIGHT_COLOR = "#16a34a"

    def __init__(self, root):
        self.root = root
        self.root.title("Stereo WAV File Viewer")
        self.root.geometry("1000x700")
        self.root.minsize(650, 450)

        self.file_path = None
        self.left_samples = []
        self.right_samples = []
        self.sample_rate = 0
        self.total_samples = 0

        toolbar = tk.Frame(root, padx=10, pady=8)
        toolbar.pack(fill="x")

        tk.Button(
            toolbar, text="Open WAV File...", command=self.open_file
        ).pack(side="left")

        self.file_label = tk.Label(
            toolbar, text="No file selected", anchor="w"
        )
        self.file_label.pack(side="left", padx=12, fill="x", expand=True)

        self.info_label = tk.Label(
            root,
            text="Select a PCM stereo WAV file to view its waveforms.",
            anchor="w",
            justify="left",
            padx=10,
            pady=5,
        )
        self.info_label.pack(fill="x")

        self.canvas = tk.Canvas(root, bg=self.BG, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.canvas.bind("<Configure>", self.redraw)

        # Show the file dialog immediately when the GUI starts.
        self.root.after(150, self.open_file)

    def open_file(self):
        path = filedialog.askopenfilename(
            parent=self.root,
            title="Select a PCM stereo WAV file",
            filetypes=[("WAV audio files", "*.wav"), ("All files", "*.*")],
        )
        if not path:
            # If the user cancels the first dialog, keep the GUI open so they
            # can click "Open WAV File..." later.
            return

        try:
            left, right, sample_rate, total_samples = self.read_wav(path)
        except (wave.Error, OSError, ValueError, struct.error) as exc:
            messagebox.showerror(
                "Could not load WAV file",
                f"The selected file could not be read:\n\n{exc}",
                parent=self.root,
            )
            return

        self.file_path = path
        self.left_samples = left
        self.right_samples = right
        self.sample_rate = sample_rate
        self.total_samples = total_samples

        self.file_label.config(text=path)
        self.info_label.config(
            text=(
                f"Total samples (both channels combined): {total_samples:,}    "
                f"Sampling frequency: {sample_rate:,} Hz    "
                f"Frames per channel: {len(left):,}"
            )
        )
        self.root.title(f"Stereo WAV File Viewer — {path.split('/')[-1]}")
        self.redraw()

    @staticmethod
    def read_wav(path):
        """Read PCM samples and return separate left/right channel lists."""
        with wave.open(path, "rb") as wav:
            channels = wav.getnchannels()
            sample_rate = wav.getframerate()
            frame_count = wav.getnframes()
            sample_width = wav.getsampwidth()
            compression = wav.getcomptype()

            if compression != "NONE":
                raise ValueError("The file must use uncompressed PCM audio.")
            if channels != 2:
                raise ValueError(
                    f"Expected a stereo file with 2 channels; found {channels}."
                )
            if sample_width not in (1, 2, 3, 4):
                raise ValueError(
                    f"Unsupported PCM sample width: {sample_width * 8} bits."
                )

            raw = wav.readframes(frame_count)

        bytes_per_frame = channels * sample_width
        if len(raw) % bytes_per_frame != 0:
            raise ValueError("The WAV file contains incomplete audio frames.")

        # PCM WAV stores 8-bit samples as unsigned values; larger common
        # integer PCM widths are signed little-endian values.
        if sample_width == 1:
            all_samples = [byte - 128 for byte in raw]
        elif sample_width == 2:
            count = len(raw) // 2
            all_samples = struct.unpack("<" + "h" * count, raw)
        elif sample_width == 3:
            all_samples = []
            for i in range(0, len(raw), 3):
                value = raw[i] | (raw[i + 1] << 8) | (raw[i + 2] << 16)
                if value & 0x800000:
                    value -= 1 << 24
                all_samples.append(value)
        else:  # 32-bit integer PCM
            count = len(raw) // 4
            all_samples = struct.unpack("<" + "i" * count, raw)

        left = list(all_samples[0::2])
        right = list(all_samples[1::2])

        if len(left) != frame_count or len(right) != frame_count:
            raise ValueError("Could not separate the stereo channels correctly.")

        # Also, report individual sample values across both channels.
        total_samples = len(left) + len(right)
        return left, right, sample_rate, total_samples

    def redraw(self, _event=None):
        """Draw both channels with basic Canvas line operations."""
        self.canvas.delete("all")
        if not self.left_samples or not self.right_samples:
            return

        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        if width < 100 or height < 160:
            return

        margin_left = 55
        margin_right = 18
        margin_top = 28
        margin_bottom = 25
        gap = 36
        plot_height = (height - margin_top - margin_bottom - gap) / 2
        plot_width = max(1, width - margin_left - margin_right)

        self._draw_channel(
            self.left_samples,
            x0=margin_left,
            y0=margin_top,
            plot_width=plot_width,
            plot_height=plot_height,
            label="Left Channel",
            color=self.LEFT_COLOR,
        )

        lower_y = margin_top + plot_height + gap
        self._draw_channel(
            self.right_samples,
            x0=margin_left,
            y0=lower_y,
            plot_width=plot_width,
            plot_height=plot_height,
            label="Right Channel",
            color=self.RIGHT_COLOR,
        )

    def _draw_channel(self, samples, x0, y0, plot_width, plot_height, label, color):
        """Map sample indices/amplitudes to canvas coordinates and connect them."""
        y_mid = y0 + plot_height / 2
        amplitude = max(abs(value) for value in samples) if samples else 1
        if amplitude == 0:
            amplitude = 1

        # Axes and labels.
        self.canvas.create_text(
            x0, y0 - 5,
            text=label,
            anchor="sw",
            fill=color,
            font=("TkDefaultFont", 10, "bold")
        )
        self.canvas.create_line(
            x0, y_mid, x0 + plot_width, y_mid, fill=self.AXIS, dash=(3, 3)
        )
        self.canvas.create_line(
            x0, y0 + 15, x0, y0 + plot_height, fill=self.AXIS
        )
        self.canvas.create_line(
            x0, y0 + plot_height, x0 + plot_width, y0 + plot_height,
            fill=self.AXIS
        )
        self.canvas.create_text(
            x0 - 8, y0 + 15, text=f"+{amplitude}", anchor="e",
            fill="#555555", font=("TkDefaultFont", 8)
        )
        self.canvas.create_text(
            x0 - 8, y0 + plot_height, text=f"-{amplitude}", anchor="e",
            fill="#555555", font=("TkDefaultFont", 8)
        )
        self.canvas.create_text(
            x0 + plot_width, y0 + plot_height + 4,
            text=f"{len(samples) - 1:,} (sample index)",
            anchor="ne", fill="#555555", font=("TkDefaultFont", 8)
        )

        count = len(samples)
        if count == 1:
            x = x0 + plot_width / 2
            y = y_mid - (samples[0] / amplitude) * (plot_height * 0.42)
            self.canvas.create_oval(x - 2, y - 2, x + 2, y + 2, fill=color, outline=color)
            return

        # direct pixel/line drawing
        # draw each sample and connect adjacent points
        usable_half_height = plot_height * 0.42
        previous = None
        for i, sample in enumerate(samples):
            x = x0 + (i / (count - 1)) * plot_width
            y = y_mid - (sample / amplitude) * usable_half_height
            point = (x, y)
            if previous is not None:
                self.canvas.create_line(
                    previous[0], previous[1], point[0], point[1],
                    fill=color, width=1
                )
            previous = point


def main():
    root = tk.Tk()
    WAVViewer(root)
    root.mainloop()


if __name__ == "__main__":
    main()
