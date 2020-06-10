class EmulatedDisplay:
    def __init__(self, file_path):
        self.file_path = file_path

    def draw(self, image):
        image.save(self.file_path)
