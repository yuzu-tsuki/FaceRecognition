"""Side-by-side face comparison demo.

A developer utility, not part of the installed package: it shows what
``compare_faces`` and ``face_distance`` do on two photos of the same person
versus a photo of somebody else.

Run it from anywhere once the project is installed:

    python tools/compare_faces_demo.py
"""

import cv2
import face_recognition

from face_recognition_doorbell import paths

BOX_COLOR = (255, 255, 0)
TEXT_COLOR = (0, 0, 255)
THICKNESS = 2


def load(path):
    """Loads an image and draws a box around the first face found in it."""
    image = face_recognition.load_image_file(path)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    locations = face_recognition.face_locations(image)
    if not locations:
        raise SystemExit(f"No face found in {path}")

    top, right, bottom, left = locations[0]
    cv2.rectangle(image, (left, top), (right, bottom), BOX_COLOR, THICKNESS)
    return image, face_recognition.face_encodings(image)[0]


def compare(image, known_encoding, candidate_encoding):
    """Annotates *image* with whether it matches, and by what distance."""
    results = face_recognition.compare_faces([known_encoding], candidate_encoding)
    distance = face_recognition.face_distance([known_encoding], candidate_encoding)
    print(results, distance)
    cv2.putText(
        image,
        f"{bool(results[0])}, Distance: {round(distance[0], 2)}",
        (50, 50),
        cv2.FONT_HERSHEY_PLAIN,
        1,
        TEXT_COLOR,
        THICKNESS,
    )


def main() -> None:
    """Shows the reference face beside a match and a non-match."""
    data = paths.data_dir()
    # The reference and the second photo of the same person are deliberately
    # different files; the decoy comes from the whitelist samples.
    reference, reference_encoding = load(data / "demo" / "elon_musk1.jpg")
    same_person, same_encoding = load(data / "samples" / "elon_musk.jpg")
    other_person, other_encoding = load(data / "samples" / "donald_trump.jpg")

    compare(same_person, reference_encoding, same_encoding)
    compare(other_person, reference_encoding, other_encoding)

    cv2.imshow("Elon Musk", reference)
    cv2.imshow("Elon Musk Test", same_person)
    cv2.imshow("Donald Trump for comparison", other_person)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
