import cv2
import numpy as np
import face_recognition
import face_recognition_models

# Load images first, convert their BGR to RGB
img_elon = face_recognition.load_image_file('DoorBell/Samples/elon_musk1.jpg')
img_elon = cv2.cvtColor(img_elon, cv2.COLOR_BGR2RGB)

img_test_elon = face_recognition.load_image_file('DoorBell/Samples/elon_musk2.jpg')
img_test_elon = cv2.cvtColor(img_test_elon, cv2.COLOR_BGR2RGB)

img_test_2 = face_recognition.load_image_file('DoorBell/Samples/donald_trump1.jpg')
img_test_2 = cv2.cvtColor(img_test_2, cv2.COLOR_BGR2RGB)


# Face location detecting
face_location = face_recognition.face_locations(img_elon)[0]
face_encode_elon = face_recognition.face_encodings(img_elon)[0]
cv2.rectangle(img_elon, (face_location[3], face_location[0]),                             # Draw a Rectangle on the face
                        (face_location[1], face_location[2]), (255, 255, 0), 2)

face_location_test = face_recognition.face_locations(img_test_elon)[0]
face_encode_test_elon = face_recognition.face_encodings(img_test_elon)[0]
cv2.rectangle(img_test_elon, (face_location_test[3], face_location_test[0]),
                             (face_location_test[1], face_location_test[2]), (255, 255, 0), 2)

face_location_test_2 = face_recognition.face_locations(img_test_2)[0]
face_encode_test_2 = face_recognition.face_encodings(img_test_2)[0]
cv2.rectangle(img_test_2, (face_location_test_2[3], face_location_test_2[0]),
                          (face_location_test_2[1], face_location_test_2[2]), (255, 255, 0), 2)


# Best match when face_distance is lower.

results = face_recognition.compare_faces([face_encode_elon], face_encode_test_elon)
face_distance = face_recognition.face_distance([face_encode_elon], face_encode_test_elon)
print(results, face_distance)
cv2.putText(img_test_elon, f'{bool(results[0])}, Distance: {round(face_distance[0], 2)}',
            (50,50), cv2.FONT_HERSHEY_PLAIN, 1, (0, 0, 255), 2)

results = face_recognition.compare_faces([face_encode_elon], face_encode_test_2)
face_distance = face_recognition.face_distance([face_encode_elon], face_encode_test_2)
print(results, face_distance)
cv2.putText(img_test_2, f'{bool(results[0])}, Distance: {round(face_distance[0], 2)}',
            (50,50), cv2.FONT_HERSHEY_PLAIN, 1, (0, 0, 255), 2)


cv2.imshow('Elon Musk', img_elon)
cv2.imshow('Elon Musk Test', img_test_elon)
cv2.imshow('Donald Trump for comparison', img_test_2)
cv2.waitKey(0)