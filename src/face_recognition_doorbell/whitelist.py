import os
import cv2
import face_recognition


class WhiteList:

    path: str

    white_list_names: list[str]
    white_list: list[tuple]

    _encoded_faces: list

    def __init__(self, images_path: str) -> None:
        self.path = images_path
        self.white_list_names = os.listdir(images_path)

        self.white_list = []
        for person in self.white_list_names:
            img = cv2.imread(f'{self.path}/{person}')
            # Convert BGR to RGB
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            self.white_list.append((img, os.path.splitext(person)[0]))

        self._encoded_faces = []
        print(self._encode_faces())
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

    def add_white_list(self, img, person) -> bool:
        """ Adds <person> to the whitelist, which the person's image has been already
        added to the directory, <self.path>.path
        Returns True iff encoded_face is not None i.e. it has been successfully encoded.
        """
        encoded_face = face_recognition.face_encodings(img)

        # Append only when encoding succeeds, so white_list and encoded_faces
        # stay index-aligned.
        if encoded_face:
            self.white_list.append((img, os.path.splitext(person)[0]))
            self._encoded_faces.append(encoded_face[0])
            return True
        return False


if __name__ == '__main__':
    path = 'Samples'
    test = WhiteList(path)