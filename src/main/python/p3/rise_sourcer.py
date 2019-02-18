import numpy as np
import cv2
import scipy
import matplotlib.pyplot as plt

class RiseSourcer:
    def __init__(self, files, size, depth):
        self.original_frames = []
        self.files = files
        self.size = size
        self.depth = depth

    def setup(self):
        for i in range(0, len(self.files)):
            raw_image = cv2.imread(self.files[i])
            self.original_frames.append(raw_image)

    def get_state(self):
        frame_buffer = [None] * self.depth
        for i in range(0, len(self.original_frames)):
            frame_buffer[i] = self.to_grayscale(cv2.resize(np.array(self.original_frames[i]), (self.size, self.size), interpolation=cv2.INTER_AREA)).flatten(order='C')

        return np.concatenate(frame_buffer) / 255

    def output_mapped_images(self, heat_values, output_name):
        np_heats = np.array(heat_values)
        heats = np.resize(np_heats, (self.depth, self.size, self.size))

        for i in range(0, 1):#len(self.original_frames)):
            scaled_heat = cv2.resize(np.array(heats[i]), (self.size, self.size), interpolation=cv2.INTER_AREA)
            plt.imshow(self.original_frames[i])
            plt.imshow(scaled_heat, cmap='hot',  alpha=.5)
            plt.suptitle(output_name, fontsize=16)
            plt.show()
            file_name = "heated" + self.files[i]
            scipy.misc.imsave(file_name, self.save_buffer[i])

    def to_grayscale(self, image):
        return np.dot(image[..., :3], [0.114, 0.587, 0.299]) # image is in bgra
