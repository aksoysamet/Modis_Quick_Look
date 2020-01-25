from PIL import Image
import os
import numpy as np


def buildImgArr(r, g=None, b=None):
    if g is not None and b is not None:
        img_Arr = np.zeros((r.shape[0], r.shape[1], 3), dtype=np.uint8)
        img_Arr[:, :, 0] = r.clip(0, 255).astype('uint8')
        img_Arr[:, :, 1] = g.clip(0, 255).astype('uint8')
        img_Arr[:, :, 2] = b.clip(0, 255).astype('uint8')
    else:
        img_Arr = r.clip(0, 255).astype('uint8')
    return img_Arr


def saveArrayToImg(arr, filename, mode="RGB"):
    if len(arr.shape) < 3:
        mode = "L"
    img = Image.fromarray(arr, mode)  # L
    if os.path.exists(filename):
        os.remove(filename)
    img_io = open(filename, "wb")
    img.save(img_io, "PNG")
    img_io.close()


def reSampleArray(r, g, b):
    if g is None or b is None:
        return (r, g, b)
    maxRes = max(r.shape[0], g.shape[0], b.shape[0])
    img = [r, g, b]
    for i in range(3):
        ratio = maxRes//img[i].shape[0]
        if ratio > 1:
            img[i] = np.repeat(np.repeat(img[i], ratio, axis=1), ratio, axis=0)
    return tuple(img)


def rotateImageSave(input, output, rotation):
    colorImage = Image.open(input)  # noqa
    rotated = colorImage.rotate(rotation, expand=1)
    img_io = open(output, "wb")  # noqa
    rotated.save(img_io, "JPEG")
    img_io.close()
