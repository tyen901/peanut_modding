import tkinter as tk
from PIL import Image, ImageTk, ImageOps
import os
import json
from functools import partial

class ImageViewer:

    render_mode = "RGB"

    def __init__(self, tkRoot, image_folder):
        self.tkRoot = tkRoot
        self.image_folder = image_folder
        self.all_image_files = []
        
        path = os.path.dirname(os.path.abspath(__file__))
        image_folder = os.path.join(path, image_folder)

        self.all_image_files = []
        for root, dirs, files in os.walk(image_folder):
            for name in files:
                if name.lower().endswith(('png', 'jpg', 'jpeg')):
                    self.all_image_files.append(os.path.relpath(os.path.join(root, name), image_folder))
        
        self.display_mode = "grid"  # Possible values: "grid" or "single"
        self.skip_tagged_images = True  # By default, skip images tagged with 'skip'
        self.tag_history = []

        self.current_index = 0
        self.tags = {}
        self.tag_panel = tk.Frame(self.tkRoot, bg='lightgray')
        self.tag_panel.pack(side=tk.BOTTOM, fill=tk.X)

        # Add a frame for the image information
        self.info_panel = tk.Frame(self.tkRoot, bg='white')
        self.info_panel.pack(side=tk.TOP, fill=tk.X)
        self.info_label = tk.Label(self.info_panel, bg='white')
        self.info_label.pack(pady=5)

        # Use a canvas instead of a label for displaying the image
        self.canvas = tk.Canvas(tkRoot)
        self.canvas.pack(fill=tk.BOTH, expand=tk.YES)

        # Key bindings for various functionalities
        self.tkRoot.bind("<Right>", self.next_image)
        self.tkRoot.bind("<Left>", self.prev_image)
        self.tkRoot.bind("r", partial(self.show_channel, 'R'))
        self.tkRoot.bind("g", partial(self.show_channel, 'G'))
        self.tkRoot.bind("b", partial(self.show_channel, 'B'))
        self.tkRoot.bind("a", partial(self.show_channel, 'A'))
        self.tkRoot.bind("1", partial(self.toggle_tag, tag='copy'))
        self.tkRoot.bind("2", partial(self.toggle_tag, tag='skip'))
        self.tkRoot.bind("m", self.toggle_display_mode)
        self.tkRoot.bind("s", self.toggle_skip_behavior)
        self.tkRoot.bind("z", self.undo_tag)
        
        self.tkRoot.bind("q", self.quit_viewer)

        # Bind window resize event to reload the image
        self.tkRoot.bind("<Configure>", lambda event: self.load_image())
        
        self.load_tags()
        self.load_image()

    def load_image(self):
        image_path = os.path.join(self.image_folder, self.all_image_files[self.current_index])
        original_image = Image.open(image_path)
        
        title_text = f"{self.current_index + 1} / {len(self.all_image_files)} - {image_path}"

        self.tkRoot.title(title_text)

        self.update_tag_panel()

        # Current dimensions of the window
        window_width = self.tkRoot.winfo_width()
        window_height = self.tkRoot.winfo_height()

        if window_width == 0 or window_height == 0:
            # Window is minimized, don't render the image
            return

        # Aspect ratio of the image
        image_aspect = original_image.width / original_image.height

        # Aspect ratio of the window
        window_aspect = window_width / window_height

        if image_aspect > window_aspect:
            # Image is wider than the window
            scaled_width = window_width
            scaled_height = int(scaled_width / image_aspect)
        else:
            # Image is taller than the window
            scaled_height = window_height
            scaled_width = int(scaled_height * image_aspect)

        if scaled_width <= 1 or scaled_height <= 1:
            # Window is too small to render the image
            return

        scaled_image = original_image.resize((scaled_width, scaled_height))

        # Clear the canvas
        self.canvas.delete("all")

        if self.display_mode == "grid":
            # Render the 2x2 grid
            channels = scaled_image.split()

            quadrant_width = scaled_width // 2
            quadrant_height = scaled_height // 2

            for idx, channel in enumerate(channels):
                img = Image.new("RGB", (quadrant_width, quadrant_height))
                resized_channel = channel.resize((quadrant_width, quadrant_height))
                img.paste(resized_channel, (0, 0))
                quadrant = ImageTk.PhotoImage(img)
                self.canvas.create_image((idx % 2) * quadrant_width, (idx // 2) * quadrant_height, anchor=tk.NW, image=quadrant)
                setattr(self, f"quadrant_{idx}_img", quadrant)  # To prevent the image from being garbage collected
        else:
            channels = {"R": 0, "G": 1, "B": 2, "A": 3}
            channel_img = scaled_image.split()[channels[self.render_mode]]
            img = Image.merge("RGB", (channel_img, channel_img, channel_img))
            self.tk_image = ImageTk.PhotoImage(img)
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image)

    def is_image_valid(self, image_path):
        filter_array = [
            'nohq.png',
            'co.png',
            'smdi.png',
            'ao.png',
            'as.png',
            '\\UI\\',
            '\\ui\\',
            '\\icons\\',
            '_body_',
            'reticle',
        ]
        return not any(filter in image_path for filter in filter_array)

    def next_image(self, event):
        initial_index = self.current_index
        while True:
            self.current_index = (self.current_index + 1) % len(self.all_image_files)
            image_path = self.all_image_files[self.current_index]
            if (self.is_image_valid(image_path) and
                not (self.skip_tagged_images and image_path in self.tags and len(self.tags[image_path]) > 0)):
                break
            if self.current_index == initial_index:
                self.canvas.delete("all")
                self.canvas.create_text(self.tkRoot.winfo_width() // 2, self.tkRoot.winfo_height() // 2, text="Done", font=("Arial", 24), fill="red")
                return
        self.load_image()

    def prev_image(self, event):
        initial_index = self.current_index
        while True:
            self.current_index = (self.current_index - 1) % len(self.all_image_files)
            image_path = self.all_image_files[self.current_index]
            if (self.is_image_valid(image_path) and
                not (self.skip_tagged_images and image_path in self.tags and len(self.tags[image_path]) > 0)):
                break
            if self.current_index == initial_index:
                self.canvas.delete("all")
                self.canvas.create_text(self.tkRoot.winfo_width() // 2, self.tkRoot.winfo_height() // 2, text="Done", font=("Arial", 24), fill="red")
                return
        self.load_image()

    def toggle_skip_behavior(self, event):
        self.skip_tagged_images = not self.skip_tagged_images

    def show_channel(self, channel, event):

        if self.render_mode == channel:
            self.render_mode = "RGB"
        else:
            self.render_mode = channel  
        self.load_image()

    def toggle_display_mode(self, event):
        self.display_mode = "grid" if self.display_mode == "single" else "single"
        self.load_image()

    def quit_viewer(self, event):
        self.save_tags()
        self.tkRoot.quit()

    def tag_image(self, event):
        image_path = os.path.join(self.image_folder, self.all_image_files[self.current_index])
        if image_path in self.tags:
            self.tags.pop(image_path)
        else:
            self.tags[image_path] = True

    def load_tags(self):
        try:
            with open("tags.json", "r") as file:
                self.tags = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            self.tags = {}

    def save_tags(self):
        if os.path.exists("tags.json"):
            os.remove("tags.json")

        with open("tags.json", "w") as file:
            # pretty print the json so it's easier to read
            json.dump(self.tags, file, indent=4)

    def toggle_tag(self, event, tag):
        current_image = self.all_image_files[self.current_index]
        if current_image not in self.tags:
            self.tags[current_image] = []

        action = "added"
        if tag in self.tags[current_image]:
            self.tags[current_image].remove(tag)
            action = "removed"
        else:
            self.tags[current_image].append(tag)

        self.tag_history.append({
            "image": current_image,
            "tag": tag,
            "action": action
        })

        self.save_tags()
        self.update_tag_panel()

        # move to next image
        self.next_image(event)

    def undo_tag(self, event):
        if not self.tag_history:
            return

        last_action = self.tag_history.pop()
        if last_action["action"] == "added":
            self.tags[last_action["image"]].remove(last_action["tag"])
        else:
            self.tags[last_action["image"]].append(last_action["tag"])

        self.save_tags()
        self.update_tag_panel()

    def update_tag_panel(self):
        current_image = self.all_image_files[self.current_index]
        current_tags = self.tags.get(current_image, [])

        # Remove all labels if the current image doesn't have any tags
        if not current_tags:
            for widget in self.tag_panel.winfo_children():
                widget.destroy()
            return

        # Remove excess labels if there are more labels than current tags
        for i in range(len(self.tag_panel.winfo_children()), len(current_tags), -1):
            self.tag_panel.winfo_children()[-1].destroy()

        # Update existing labels or create new ones as needed
        for i, tag in enumerate(current_tags):
            if i < len(self.tag_panel.winfo_children()):
                # Update existing label
                self.tag_panel.winfo_children()[i].config(text=tag)
            else:
                # Create new label
                label = tk.Label(self.tag_panel, text=tag, bg='lightgray')
                label.pack(side=tk.LEFT, padx=5)

if __name__ == "__main__":
    try:
        image_folder = "extracted"  # Replace with the path to your image folder
        tkRoot = tk.Tk()
        tkRoot.attributes('-fullscreen', False)
        viewer = ImageViewer(tkRoot, image_folder)
        tkRoot.mainloop()
    except Exception as e:
        print(f"An error occurred: {e}")
