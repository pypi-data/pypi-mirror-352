from tableviz import TableData, Table
import os
import json
import io
import requests
import base64
from PIL import Image
import cv2
import numpy as np


def read_base64_image(base64_image: str) -> Image.Image:
    return Image.open(io.BytesIO(base64.b64decode(base64_image)))


def encode_base64_image(image: Image.Image) -> str:
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode("utf-8")


def is_same_image(image1: Image.Image, image2: Image.Image, threshold: int = 0.1) -> bool:
    image1 = cv2.cvtColor(np.array(image1), cv2.COLOR_RGB2BGR)
    image2 = cv2.cvtColor(np.array(image2), cv2.COLOR_RGB2BGR)
    # return cv2.compare(image1, image2, cv2.CMP_EQ).all()
    print(cv2.norm(image1, image2, cv2.NORM_L2))
    return cv2.norm(image1, image2, cv2.NORM_L2) < threshold


if __name__ == '__main__':


    data = [
        {'name': 'John Doe', 'age': 25, 'score': 95.5, 'avatar': Image.new('RGB', (256, 256))},
        {'name': 'Jane Smith', 'age': 30, 'score': 87.2, 'avatar': Image.new('RGB', (256, 256))},
        {'name': 'Bob Johnson', 'age': 35, 'score': 90.1, 'avatar': Image.new('RGB', (256, 256))},
        {'name': 'Alice Brown', 'age': 40, 'score': 92.3, 'avatar': Image.new('RGB', (256, 256))},
        {'name': 'David Lee', 'age': 45, 'score': 88.9, 'avatar': Image.new('RGB', (256, 256))},
        {'name': 'Eve Wilson', 'age': 50, 'score': 91.7, 'avatar': Image.new('RGB', (256, 256))},
        {'name': 'Frank Davis', 'age': 55, 'score': 93.5, 'avatar': Image.new('RGB', (256, 256))},
        {'name': 'Grace Taylor', 'age': 60, 'score': 89.8, 'avatar': Image.new('RGB', (256, 256))},
    ]

    table_data = TableData(data)
    table = Table(table_data, save_dir='./test')
    table.save()
