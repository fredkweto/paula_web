from PIL import Image
import os, secrets

size = (300,300)


def save_picture(form_picture):
    random_hex = secrets.token_hex(4)
    _ , f_ext = os.path.splitext(form_picture)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join('paula\static\web_images', picture_fn)
    # picture_resized = Image.open(picture_path)
    # picture_resized.thumbnail(size)
    form_picture.save(picture_path)
    return picture_fn

save_picture('stacked-coins-with-dirt-plant.jpg')