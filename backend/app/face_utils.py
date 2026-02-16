import face_recognition
import numpy as np


def encode_face(image_path: str):
    image = face_recognition.load_image_file(image_path)

    encodings = face_recognition.face_encodings(image)

    if len(encodings) == 0:
        return None

    return encodings[0].tolist()


def compare_faces(known_encoding, unknown_encoding):

    known = np.array(known_encoding)
    unknown = np.array(unknown_encoding)

    results = face_recognition.compare_faces([known], unknown)

    return results[0]