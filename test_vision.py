from pathlib import Path
from vision import recognize_product_from_image


class FakeUploadedFile:
    def __init__(self, path):
        self.path = path
        self.type = "image/jpeg"

    def getvalue(self):
        return Path(self.path).read_bytes()


img = FakeUploadedFile("test.jpg")

result = recognize_product_from_image(img)

print("识别结果：", result)