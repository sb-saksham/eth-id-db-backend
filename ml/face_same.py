import cv2 as cv
from django.conf import settings
from pathlib import Path
import numpy
from PIL import Image


def recognize_face(id_image, image_waddr):
    final_verdict = False
    detector = cv.FaceDetectorYN.create(
        str(Path.joinpath(settings.BASE_DIR, "ml/face_detection_yunet_2023mar.onnx")),
        "",
        (320, 320),
        0.9,
        0.3,
        500,
    )
    if id_image is not None:
        pil_image = Image.open(id_image)
        img1 = cv.cvtColor(numpy.array(pil_image), cv.COLOR_RGB2BGR)
        img1Width = int(img1.shape[1]*1.0)
        img1Height = int(img1.shape[0]*1.0)
        img1 = cv.resize(img1, (img1Width, img1Height))

        detector.setInputSize((img1Width, img1Height))
        faces1 = detector.detect(img1)

        assert faces1[1] is not None, 'Cannot find a face in {}'.format(id_image)

        if image_waddr is not None:
            pil_image = Image.open(image_waddr)
            img2 = cv.cvtColor(numpy.array(pil_image), cv.COLOR_RGB2BGR)
            detector.setInputSize((img2.shape[1], img2.shape[0]))
            faces2 = detector.detect(img2)

            assert faces2[1] is not None, 'Cannot find a face in {}'.format(image_waddr)

            recognizer = cv.FaceRecognizerSF.create(str(Path.joinpath(settings.BASE_DIR, "ml/face_recognition_sface_2021dec_int8.onnx")), "")
            face1_align = recognizer.alignCrop(img1, faces1[1][0])
            face2_align = recognizer.alignCrop(img2, faces2[1][0])

            face1_feature = recognizer.feature(face1_align)
            face2_feature = recognizer.feature(face2_align)

            cosine_similarity_threshold = 0.363
            l2_similarity_threshold = 1.128

            cosine_score = recognizer.match(face1_feature, face2_feature, cv.FaceRecognizerSF_FR_COSINE)
            l2_score = recognizer.match(face1_feature, face2_feature, cv.FaceRecognizerSF_FR_NORM_L2)

            cosine_verdict = False
            msg = 'different identities'
            if cosine_score >= cosine_similarity_threshold:
                msg = 'the same identity'
                cosine_verdict = True
            print('They have {}. Cosine Similarity: {}, threshold: {} (higher value means higher similarity, max 1.0).'.format(msg, cosine_score, cosine_similarity_threshold))

            verdict_12 = False
            msg = 'different identities'
            if l2_score <= l2_similarity_threshold:
                msg = 'the same identity'
                verdict_12 = True
            print('They have {}. NormL2 Distance: {}, threshold: {} (lower value means higher similarity, min 0.0).'.format(msg, l2_score, l2_similarity_threshold))
            print("verdict_12", verdict_12)
            print("cosine_verdict", cosine_verdict)
            final_verdict = verdict_12 and cosine_verdict

    return final_verdict