# MIT License

# Copyright (c) 2025 Ahmed Salim

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import pathlib
from typing import Union, Tuple, List, Optional

import cv2
import numpy as np
import tensorflow as tf
import dlib
from face_detection import RetinaFace

from face_analysis.eyes.utils import get_attributes_wrt_local_frame, setup_gpu, get_dlib_points, get_left_key_points, get_right_key_points
from face_analysis.eyes.results import EyeStateResultContainer
from face_analysis.eyes.model import EyeStateClassifierNet
from face_analysis.commons.get_weights import download_weights_if_necessary 

SHAPE_PREDICTOR_URL = "http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2"

class Pipeline:

    def __init__(
        self, 
        weights: pathlib.Path = None, 
        shape_predictor: Optional[pathlib.Path] = None,
        detector: str = "retinaface",
        device: str = 'cpu', 
        confidence_threshold: float = 0.5
        ):

        # Save input parameters
        self.weights = weights
        self.shape_predictor = shape_predictor
        self.detector_type = detector
        self.device = setup_gpu(device)
        self.confidence_threshold = confidence_threshold

        if shape_predictor is None:
            self.shape_predictor = download_weights_if_necessary(
                file_name='shape_predictor_68_face_landmarks.dat',
                source_url=SHAPE_PREDICTOR_URL,
                compress_type='bz2'
            )
            self.predictor = dlib.shape_predictor(str(self.shape_predictor))
        
        if self.weights is None:
            self.weights = download_weights_if_necessary(
                file_name='eye_state_model.h5',
                source_url="https://github.com/ahmedsalim3/eye-analysis/raw/refs/heads/main/weights/eye_state_model.h5",
                compress_type=None
            )
        
        # Create eye state classifier model
        with tf.device(self.device):
            self.model = EyeStateClassifierNet(compile=True).model
            self.model.load_weights(self.weights)
        
        # Set up face detection based on detector_type
        if self.detector_type == "retinaface":
            # RetinaFace for face detection
            if 'CPU' in self.device:
                self.detector = RetinaFace()
            else:
                gpu_id = 0  # Default GPU ID, adjust as needed
                self.detector = RetinaFace(gpu_id=gpu_id)
        elif self.detector_type == "dlib":
            # Use dlib's frontal face detector
            self.detector = dlib.get_frontal_face_detector()
        else:
            raise ValueError("Invalid detector type. Must be 'retinaface' or 'dlib'")

    def step(self, frame: np.ndarray) -> EyeStateResultContainer:
        """
        Process a single frame and return eye state results.
        
        Args:
            frame: Input image frame as numpy array
            
        Returns:
            EyeStateResultContainer with eye state results
        """
        # Creating containers
        face_imgs = []
        bboxes = []
        landmarks = []
        scores = []
        left_states = []
        right_states = []
        left_confidences = []
        right_confidences = []

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        if self.detector_type == "retinaface":
            # Detect faces using RetinaFace
            faces = self.detector(frame)
            
            if faces is not None:
                for box, landmark, score in faces:
                    # Apply threshold
                    if score < self.confidence_threshold:
                        continue
                        
                    # Extract safe min and max of x,y
                    x_min = int(box[0])
                    if x_min < 0:
                        x_min = 0
                    y_min = int(box[1])
                    if y_min < 0:
                        y_min = 0
                    x_max = int(box[2])
                    y_max = int(box[3])
                    
                    # Crop face and resize
                    face_img = gray[y_min:y_max, x_min:x_max]
                    if face_img.size == 0:  # Skip if face region is empty
                        continue
                    face_img = cv2.resize(face_img, (100, 100))
                    
                    # Create dlib rectangle for the face to use with the predictor
                    face_rect = dlib.rectangle(0, 0, 100, 100)
                    
                    # Process the face
                    l_state, l_confidence, r_state, r_confidence = self.process_face(face_img, face_rect)
                    
                    # Save data
                    face_imgs.append(face_img)
                    bboxes.append(box)
                    landmarks.append(landmark)
                    scores.append(score)
                    left_states.append(l_state)
                    right_states.append(r_state)
                    left_confidences.append(l_confidence)
                    right_confidences.append(r_confidence)
            
        elif self.detector_type == "dlib":
            # Process directly using dlib for landmarks
            dlib_faces = self.detector(gray)
            
            for face in dlib_faces:
                # Extract face
                face_left = max(0, face.left())
                face_top = max(0, face.top())
                face_right = min(gray.shape[1], face.right())
                face_bottom = min(gray.shape[0], face.bottom())
                
                face_img = gray[face_top:face_bottom, face_left:face_right]
                if face_img.size == 0:  # Skip if face region is empty
                    continue
                face_img = cv2.resize(face_img, (100, 100))
                
                # Create dlib rectangle for the face to use with the predictor
                face_rect = dlib.rectangle(0, 0, 100, 100)
                
                # Process the face
                l_state, l_confidence, r_state, r_confidence = self.process_face(face_img, face_rect)
                
                # Create bounding box format compatible with RetinaFace for consistency
                box = np.array([face_left, face_top, face_right, face_bottom])
                
                # Save data
                face_imgs.append(face_img)
                bboxes.append(box)
                landmarks.append(np.zeros((5, 2)))  # placeholder for compatibility
                scores.append(1.0)  # placeholder confidence for dlib
                left_states.append(l_state)
                right_states.append(r_state)
                left_confidences.append(l_confidence)
                right_confidences.append(r_confidence)

        # If no faces found or processed, return empty results
        if not face_imgs:
            return EyeStateResultContainer(
                left_states=[],
                right_states=[],
                left_confidences=[],
                right_confidences=[],
                bboxes=np.empty((0, 4)),
                landmarks=np.empty((0, 5, 2)),
                scores=np.empty((0,))
            )

        # Create result container
        results = EyeStateResultContainer(
            left_states=left_states,
            right_states=right_states,
            left_confidences=left_confidences,
            right_confidences=right_confidences,
            bboxes=np.array(bboxes),
            landmarks=np.array(landmarks),
            scores=np.array(scores)
        )

        return results

    def process_face(self, face_img: np.ndarray, face_rect: dlib.rectangle, debug: bool = False) -> Tuple[str, float, str, float]:
        """
        Process a face image and return eye states and confidences.
        
        Args:
            face_img: Grayscale face image
            face_rect: Dlib rectangle representing the face bounds
            
        Returns:
            Tuple of (left_state, left_confidence, right_state, right_confidence)
        """
        # Get eye attributes - pass the face_rect directly instead of extracting it inside the functions
        l_i, lkp, ld, la = self._get_left_eye_attributes(face_img, face_rect)
        r_i, rkp, rd, ra = self._get_right_eye_attributes(face_img, face_rect)
        if debug:
            cv2.imshow(f"Left eye", l_i)
            cv2.imshow(f"Right eye", r_i)
        
        # Prepare eye data
        left_eye_data = self.prepare_eye_data(l_i, lkp, ld, la)
        right_eye_data = self.prepare_eye_data(r_i, rkp, rd, ra)

        # Predict eye states
        left_state, left_confidence = self.predict_eye_state(left_eye_data)
        right_state, right_confidence = self.predict_eye_state(right_eye_data)
        
        return left_state, left_confidence, right_state, right_confidence

    def _get_left_eye_attributes(self, face_image, face_rect):
        """
        Extracts eye image, key points, distance of each key points
        from centroid of the key points and angles between centroid and
        each key points of left eye.
        """
        # Get dlib key points
        dlib_points = get_dlib_points(face_image, self.predictor, face_rect)
        
        # Get key points of the eye and eyebrow
        key_points_11 = get_left_key_points(dlib_points)
        
        # Get attributes with respect to local frame
        eye_image, key_points_11, dists, angles = get_attributes_wrt_local_frame(
            face_image, key_points_11, (24, 24, 1)
        )
        
        return eye_image, key_points_11, dists, angles

    def _get_right_eye_attributes(self, face_image, face_rect):
        """
        Extracts eye image, key points, distance of each key points
        from centroid of the key points and angles between centroid and
        each key points of right eye.
        """
        # Get dlib key points
        dlib_points = get_dlib_points(face_image, self.predictor, face_rect)
        
        # Get key points of the eye and eyebrow
        key_points_11 = get_right_key_points(dlib_points)
        
        # Get attributes with respect to local frame
        eye_image, key_points_11, dists, angles = get_attributes_wrt_local_frame(
            face_image, key_points_11, (24, 24, 1)
        )
        
        return eye_image, key_points_11, dists, angles

    def prepare_eye_data(self, eye_img, keypoints, distances, angles):
        """
        Prepare eye data for the model.
        
        Args:
            eye_img: Eye image
            keypoints: Eye keypoints
            distances: Eye distances
            angles: Eye angles
            
        Returns:
            Tuple of prepared tensors
        """
        img = eye_img.reshape(-1, 24, 24, 1).astype(np.float32) / 255
        kp = np.expand_dims(keypoints, 1).astype(np.float32) / 24
        d = np.expand_dims(distances, 1).astype(np.float32) / 24
        a = np.expand_dims(angles, 1).astype(np.float32) / np.pi

        kp = kp.reshape(-1, 1, 11, 2)
        d = d.reshape(-1, 1, 11, 1)
        a = a.reshape(-1, 1, 11, 1)

        return img, kp, d, a

    def predict_eye_state(self, eye_data):
        """
        Predict eye state from prepared eye data.
        
        Args:
            eye_data: Tuple of prepared eye tensors
            
        Returns:
            Tuple of (state, confidence)
        """
        img, kp, d, a = eye_data
        
        with tf.device(self.device):
            prediction = self.model.predict([img, kp, d, a], verbose=0)[0]
            
        arg_max = np.argmax(prediction)

        state = "open" if arg_max == 1 else "closed"
        confidence = float(prediction[arg_max])

        return state, confidence
