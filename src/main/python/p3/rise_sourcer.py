import numpy as np
import cv2

class RiseSourcer:
    def __init__(self, files, size):
        self.converted_frames = []
        self.original_frames = []
        self.files = files
        self.size = size

    def setup(self):
        for i in range(0, len(self.files)):
            raw_image = cv2.imread(self.files[i])
            self.original_frames.append(raw_image)
            converted_image = self.convert_image(raw_image, self.size)
            self.converted_frames.append(converted_image)

    def get_flat_original_images(self):
        return self.get_flat_images(self.original_frames)

    def get_flat_converted_images(self):
        return self.get_flat_images(self.converted_frames)

    def get_flat_images(self, images):
        flat_frames = []
        for i in range(0, len(images)):
            flat_frames.extend(images[i])
        return flat_frames

    def convert_image(self, im, size):
        arr = self.to_grayscale(cv2.resize(im, (size, size), interpolation=cv2.INTER_AREA)[:,:,:3])
        return arr / 255.0

    def to_grayscale(self, im):
        mean = np.mean(im, axis=2)
        return mean
