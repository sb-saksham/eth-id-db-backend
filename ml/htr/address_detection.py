from typing import Tuple, List
from collections import namedtuple
from pathlib import Path

from PIL import Image
import numpy as np
import cv2
from django.conf import settings

from .model import Model, DecoderType
from .preprocessor import Preprocessor

Batch = namedtuple('Batch', 'imgs, gt_texts, batch_size')


def char_list_from_file() -> List[str]:
    with open(str(Path.joinpath(settings.BASE_DIR, 'ml/htr/model_data/charList.txt'))) as f:
        return list(f.read())


def get_img_size(line_mode: bool = False) -> Tuple[int, int]:
    """Height is fixed for NN, width is set according to training mode (single words or text lines)."""
    if line_mode:
        return 256, get_img_height()
    return 128, get_img_height()


def get_img_height() -> int:
    """Fixed height for NN."""
    return 32


def recognize_addr(waddr, waddr_image):
    model = Model(char_list_from_file(), DecoderType.WordBeamSearch, must_restore=True)
    pil_image = Image.open(waddr_image)
    img = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2GRAY)
    # img1Width = int(img1.shape[1]*1.0)
    # img1Height = int(img1.shape[0]*1.0)
    # img = cv2.resize(img1, (img1Width, img1Height))
    assert img is not None
    preprocessor = Preprocessor(get_img_size(), dynamic_width=True, padding=16)
    img = preprocessor.process_img(img)

    batch = Batch([img], None, 1)
    recognized, probability = model.infer_batch(batch, True)
    print(f'Recognized: "{recognized[0]}"')
    print(f'Probability: {probability[0]}')
    return waddr == recognized
