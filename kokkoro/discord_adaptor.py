from PIL import Image

class DiscordImage:
    LOCAL_IMAGE = 1
    REMOTE_IMAGE = 2
    PIL_IMAGE = 3

    def __init__(self, img_type, img, filename="image.png"):
        self.type = img_type
        self.img = img # path or url or pil image
        self.filename = filename

def local_image(path:str) -> DiscordImage:
    return DiscordImage(DiscordImage.LOCAL_IMAGE, path)

def remote_image(url:str, filename="image.png") -> DiscordImage:
    return DiscordImage(DiscordImage.REMOTE_IMAGE, url, filename=filename)

def pil_image(img: Image, filename="image.png") -> DiscordImage:
    return DiscordImage(DiscordImage.PIL_IMAGE, img, filename=filename)