from skimage.io import imread, imsave

def read_image(image_path, is_gray=False):
    image = imread(image_path, as_gray=is_gray)
    return image

def save_image(image, output_path):
    imsave(output_path, image)
    print(f"Image saved to {output_path}")