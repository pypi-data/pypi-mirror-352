from skimage.transform import resize
def resize_image(image, target_shape):
    assert 0 <= target_shape <= 1, "Target shape must be between 0 and 1"
    height = round(image.shape[0] * target_shape)
    width = round(image.shape[1] * target_shape)
    resized_image = resize(image, (height, width), anti_aliasing=True)
    return resized_image