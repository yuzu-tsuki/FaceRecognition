import cv2
import numpy as np
import face_recognition
import os
from white_list import WhiteList
from datetime import datetime


class DoorBell:
    # TODO: Allow parameters such as a path to WL.
    #  Add a method for adding a whitelist.
    def __init__(self) -> None:
        self.w_list = WhiteList('Samples')
        self.encoded_faces = self.w_list.get_encoded_faces()
        self.w_list_images = self.w_list.get_white_lists()

    def view_white_list(self) -> list[tuple]:
        return self.w_list.get_white_lists()

    def add_sample(self) -> None:
        path = 'Samples'
        w_list_image = os.listdir(path)

        for person in w_list_image:
            img = cv2.imread(f'{path}/{person}')
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            self.w_list.add_white_list(img, person)
            print(f"Added {person} to white list.")
        
        self.encoded_faces = self.w_list.get_encoded_faces()
        self.w_list_images = self.w_list.get_white_lists()
        self.view_white_list()

    def mark_attendance(self, name: str) -> bool:
        """Just a Test method for now"""
        # TODO: Allow writing duplicate only after 5 minutes of the last one written.
        path = 'Attendance/Attendance.csv'
        with open(path, 'r+') as f:
            attended_list = f.readlines()

            # This avoids duplicates within 1 minute
            for i in range(len(attended_list) - 1, -1, -1):
                entry = attended_list[i].split(',')
                existing_name = entry[0]
                if existing_name.lower() == name.lower():
                    # Every line except the last keeps its trailing '\n' after
                    # readlines(), which strptime rejects.
                    written_date_time = datetime.strptime(entry[1].strip(), '%d/%m/%Y %H:%M:%S')
                    print('written date: ' + written_date_time.strftime('%d/%m/%Y %H:%M:%S'))
                    now = datetime.now()
                    print('difference: ' + str((now - written_date_time).total_seconds()))
                    if (now - written_date_time).total_seconds() >= 60: # 60 sec (1 min)
                        now = now.strftime('%d/%m/%Y %H:%M:%S')
                        f.writelines(f'\n{name},{now}')
                        return True
                    return False

            now = datetime.now()
            date_string = now.strftime("%d/%m/%Y %H:%M:%S")
            f.writelines(f'\n{name},{date_string}')
            return True


    def run_door_bell(self) -> None:
        # TODO: Make sub-function / helper functions for easier management
        cam = cv2.VideoCapture(0)

        if not cam.isOpened():
            print("Error: Could not open camera.")
            return

        while True:
            succ, frame = cam.read()

            if not succ:
                print("Error: Could not read frame.")
                break

            # resizing the image for faster processing
            frame_small = cv2.resize(frame, (0, 0), None, 0.25, 0.25)
            frame_small = cv2.cvtColor(frame_small, cv2.COLOR_BGR2RGB)

            face_loc = face_recognition.face_locations(frame_small)
            encode_frame = face_recognition.face_encodings(frame_small, face_loc)

            for encode_face, face_location in zip(encode_frame, face_loc):
                matches = face_recognition.compare_faces(self.encoded_faces, encode_face)
                face_distance = face_recognition.face_distance(self.encoded_faces, encode_face)

                # print(f"Face distance: {face_distance}")

                match_index = np.argmin(face_distance)

                if matches[match_index]:
                    name = self.w_list_images[match_index][1]
                    print(f"Recognized: {name}")

                    y1, x2, y2, x1 = face_location
                    y1 *= 4
                    x2 *= 4
                    y2 *= 4
                    x1 *= 4

                    cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 255, 0), 2)
                    cv2.putText(frame, name, (x1 + 6, y1 - 6), cv2.FONT_HERSHEY_PLAIN,
                                1.5, (255, 255, 255), 2)
                    print('Marking Attentance: ' + str(self.mark_attendance(name)))
                else:
                    y1, x2, y2, x1 = face_location
                    y1 *= 4
                    x2 *= 4
                    y2 *= 4
                    x1 *= 4

                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
                    cv2.putText(frame, "Unknown", (x1 + 6, y1 - 6), cv2.FONT_HERSHEY_PLAIN,
                                1.5, (255, 255, 255), 2)

            cv2.imshow('Door Bell', frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q') or cv2.getWindowProperty('Door Bell', cv2.WND_PROP_VISIBLE) < 1:
                break  

        cam.release()
        cv2.destroyAllWindows()

