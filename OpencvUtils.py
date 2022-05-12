import math
import cv2
import numpy as np


def resize(frame, scale_percent):
    """
    Resize the image maintaining the aspect ratio
    :param frame: opencv image/frame
    :param scale_percent: int
        scale factor for resizing the image
    :return:
    resized: rescaled opencv image/frame
    """
    width = int(frame.shape[1] * scale_percent / 100)
    height = int(frame.shape[0] * scale_percent / 100)
    dim = (width, height)

    resized = cv2.resize(frame, dim, interpolation=cv2.INTER_LINEAR)
    return resized


def get_face_area(face):
    """
    Computes the area of the bounding box ROI of the face detected by the dlib face detector
    It's used to sort the detected faces by the box area
    :param face: dlib bounding box of a detected face in faces
    :return: area of the face bounding box
    """
    return (face.left() - face.right()) * (face.bottom() - face.top())


def show_keypoints(keypoints, frame):
    """
    Draw circles on the opencv frame over the face keypoints predicted by the dlib predictor
    :param keypoints: dlib iterable 68 keypoints object
    :param frame: opencv frame
    :return: frame
        Returns the frame with all the 68 dlib face keypoints drawn
    """
    for n in range(0, 68):  # per tutti i 68 keypoints stampa su frame la loro posizione
        x = keypoints.part(n).x
        y = keypoints.part(n).y
        cv2.circle(frame, (x, y), 1, (0, 0, 255), -1)
        return frame


def midpoint(p1, p2):
    """
    Compute the midpoint between two dlib keypoints
    :param p1: dlib single keypoint
    :param p2: dlib single keypoint
    :return: array of x,y coordinated of the midpoint between p1 and p2
    """
    return np.array([int((p1.x + p2.x) / 2), int((p1.y + p2.y) / 2)])


def get_array_keypoints(landmarks, dtype="int", verbose: bool = False):
    """
    Converts all the iterable dlib 68 face keypoint in a numpy array of shape 68,2
    :param landmarks: dlib iterable 68 keypoints object
    :param dtype: dtype desired in output
    :param verbose: if set to True, prints array of keypoints (default is False)
    :return: points_array
        Numpy array containing all the 68 keypoints (x,y) coordinates
        The shape is 68,2
    """
    points_array = np.zeros((68, 2), dtype=dtype)
    for i in range(0, 68):
        points_array[i] = (landmarks.part(i).x, landmarks.part(i).y)

    if verbose:
        print(points_array)

    return points_array


def isRotationMatrix(R, precision=1e-4):
    """
    Checks if a matrix is a rotation matrix
    :param R: np.array matrix of 3 by 3
    :param precision: float
        precision to respect to accept a zero value in identity matrix check (default is 1e-4)
    :return: True or False
        Return True if a matrix is a rotation matrix, False if not
    """
    Rt = np.transpose(R)
    shouldBeIdentity = np.dot(Rt, R)
    I = np.identity(3, dtype=R.dtype)
    n = np.linalg.norm(I - shouldBeIdentity)
    return n < precision

# Calculates Rotation Matrix given euler angles in the order of YAW(psi), PITCH(theta), ROLL(phi)


def eulerAnglesToRotationMatrix(theta):
    '''
    :param: theta: np array 
        array of angles (radians) in the order of YAW(psi), PITCH(theta), ROLL(phi)

    YAW = rotation around the x axis
    PITCH = rotation around the y axis
    ROLL = rotation around the z axis

    :return: 3 by 3 np array
        Return 3x3 rotation matrix
    '''
    #yaw rotation
    R_x = np.array([[1,         0,                  0],
                    [0,         math.cos(theta[0]), -math.sin(theta[0])],
                    [0,         math.sin(theta[0]), math.cos(theta[0])]
                    ])
    #pitch rotation
    R_y = np.array([[math.cos(theta[1]),    0,      math.sin(theta[1])],
                    [0,                     1,      0],
                    [-math.sin(theta[1]),   0,      math.cos(theta[1])]
                    ])
    #roll rotation
    R_z = np.array([[math.cos(theta[2]),    -math.sin(theta[2]),    0],
                    [math.sin(theta[2]),    math.cos(theta[2]),     0],
                    [0,                     0,                      1]
                    ])

    R = np.dot(R_z, np.dot(R_y, R_x))

    return R


def rotationMatrixToEulerAngles(R, precision=1e-4):
    """
    Computes the Tait–Bryan Euler () angles from a Rotation Matrix.
    Also checks if there is a gymbal lock and eventually use an alternative formula
    :param R: np.array
        3 x 3 Rotation matrix
    :param precision: float
        precision to respect to accept a zero value in identity matrix check (default is 1e-4)
    :return: (yaw, pitch, roll) tuple of float numbers
        Euler angles in radians in the order of YAW, PITCH, ROLL
    """
    # Calculates Tait–Bryan Euler angles from a Rotation Matrix
    assert (isRotationMatrix(R, precision))  # check if it's a Rmat

    # assert that sqrt(R11^2 + R21^2) != 0
    sy = np.sqrt(R[0, 0] * R[0, 0] + R[1, 0] * R[1, 0])
    singular = sy < precision

    if not singular:  # if not in a singularity, use the standard formula
        x = math.atan2(R[2, 1], R[2, 2])  # atan2(R31, R33) -> YAW, angle PSI

        # atan2(-R31, sqrt(R11^2 + R21^2)) -> PITCH, angle delta
        y = math.atan2(-R[2, 0], sy)

        z = math.atan2(R[1, 0], R[0, 0])  # atan2(R21,R11) -> ROLL, angle phi

    else:  # if in gymbal lock, use different formula for yaw, pitch roll
        x = math.atan2(-R[1, 2], R[1, 1])
        y = math.atan2(-R[2, 0], sy)
        z = 0

    return np.array([x, y, z])  # returns YAW, PITCH, ROLL in radians

