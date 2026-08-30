from pathlib import Path

import cv2
import face_recognition

from . import config, paths


class WhiteList:

    path: str

    white_list_names: list[str]
    white_list: list[tuple]

    _encoded_faces: list

    def __init__(self, images_path: Path | str | None = None) -> None:
        """Loads and encodes every image in *images_path*.

        Defaults to the samples directory resolved by :mod:`paths` when no path
        is given, so the whitelist no longer depends on the working directory.
        """
        directory = Path(images_path) if images_path is not None else paths.default_samples_dir()
        self.path = str(directory)

        # Anything that is not a recognised image is skipped. cv2.imread returns
        # None for a README or a subdirectory, and the cvtColor below would then
        # raise. Sorting keeps the load order deterministic.
        image_files = sorted(
            entry for entry in directory.iterdir()
            if entry.is_file() and entry.suffix.lower() in config.IMAGE_SUFFIXES
        )
        self.white_list_names = [entry.name for entry in image_files]

        self.white_list = []
        for entry in image_files:
            img = cv2.imread(str(entry))
            # Convert BGR to RGB
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            self.white_list.append((img, entry.stem))

        self._encoded_faces = []
        self._encode_faces()
        # Encode every face for future use.

    def _encode_faces(self) -> bool:
        """Encodes each white listed person's face and stores them in a list, encoded_faces.
        A person whose face cannot be encoded is dropped from the whitelist, so
        white_list and encoded_faces always stay index-aligned.
        Returns True iff every face has been successfully encoded.
        """
        all_encoded = True
        encodable = []
        kept_file_names = []
        # white_list and white_list_names are built in the same order in
        # __init__, so they can be walked together per file.
        for person, file_name in zip(self.white_list, self.white_list_names):
            image = person[0]
            encoded_face = face_recognition.face_encodings(image)
            if encoded_face:
                self._encoded_faces.append(encoded_face[0])
                encodable.append(person)
                kept_file_names.append(file_name)
            else:
                print(f"Warning: no face found for '{person[1]}', removed from white list.")
                all_encoded = False
        self.white_list = encodable
        self.white_list_names = kept_file_names
        return all_encoded

    def get_white_lists(self) -> list[tuple]:
        """ Returns list of white listed person's faces as a cv2 image format."""
        return self.white_list

    def get_encoded_faces(self) -> list:
        """ Returns list of encoded faces."""
        return self._encoded_faces

    def get_path(self) -> str:
        return self.path

    def get_white_list_names(self) -> list[str]:
        return self.white_list_names

    def add_white_list(self, img, person: str) -> bool:
        """Adds *person* to the whitelist, whose image is already in ``self.path``.

        *person* is the image's file name; the display name is its stem.
        Returns True iff the face was successfully encoded.
        """
        encoded_face = face_recognition.face_encodings(img)

        # Append only when encoding succeeds, and append to all three lists, so
        # white_list, white_list_names and encoded_faces stay index-aligned.
        if encoded_face:
            self.white_list.append((img, Path(person).stem))
            self.white_list_names.append(person)
            self._encoded_faces.append(encoded_face[0])
            return True
        return False