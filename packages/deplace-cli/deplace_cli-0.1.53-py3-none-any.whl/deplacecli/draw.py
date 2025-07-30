import cv2
import numpy as np

from typing import Dict, List, Tuple
from pycocotools import mask as mask_utils

class Annotation:

    pass


class Text(Annotation):

    @staticmethod
    def draw(
        frame: np.ndarray, 
        text: str, 
        draw: Dict = {}
    ) -> np.ndarray:

        # Drawing parameters
        color = draw.get("text_color", "#FF0000")
        text_size = draw.get("text_size", 1.0)
        text_thickness = draw.get("text_thickness", 2)
        text_margin = draw.get("text_margin", 10)

        # Color conversion
        color = tuple(int(color[i:i + 2], 16) for i in (1, 3, 5))
        color = (color[2], color[1], color[0])

        # Get text size
        text_size_tuple = cv2.getTextSize(
            text, 
            cv2.FONT_HERSHEY_SIMPLEX, 
            text_size, 
            text_thickness
        )[0]

        # Calculate text position
        text_x = text_margin
        text_y = text_margin + text_size_tuple[1]
        cv2.putText(
            frame, text,
            (text_x, text_y),
            cv2.FONT_HERSHEY_SIMPLEX,
            text_size,
            color, text_thickness,
        )

        return frame

class BBox(Annotation):

    """
    Class to annotate bounding boxes on video frames
    """

    @staticmethod
    def draw(
        frame: np.ndarray, 
        x_min: int,
        y_min: int,
        x_max: int,
        y_max: int,
        draw: Dict = {}
    ) -> np.ndarray:
        
        # Drawing parameters
        color = draw.get("frame_color", "#FF0000")
        frame_thickness = draw.get("frame_thickness", 3)

        # Color conversion
        color = tuple(int(color[i:i + 2], 16) for i in (1, 3, 5))
        color = (color[2], color[1], color[0])

        cv2.rectangle(
            frame, 
            (x_min, y_min), 
            (x_max, y_max), 
            color, 
            frame_thickness
        )

        return frame
    
    @staticmethod
    def draw_with_label(
        frame: np.ndarray, 
        x_min: int,
        y_min: int,
        x_max: int,
        y_max: int,
        label: str,
        draw: Dict = {}
    ) -> np.ndarray:
        
        # Draw the bounding box
        frame = BBox.draw(frame, x_min, y_min, x_max, y_max, draw)

        # Drawing parameters for label
        text_color = draw.get("text_color", "#FFFFFF")
        text_size = draw.get("text_size", 0.5)
        text_thickness = draw.get("text_thickness", 1)
        text_margin = draw.get("text_margin", 5)

        # Color conversion
        text_color = tuple(int(text_color[i:i + 2], 16) for i in (1, 3, 5))
        text_color = (text_color[2], text_color[1], text_color[0])

        # Put the label above the bounding box
        cv2.putText(
            frame, label,
            (x_min + text_margin, y_min - text_margin),
            cv2.FONT_HERSHEY_SIMPLEX,
            text_size,
            text_color, text_thickness,
        )

        return frame
    

class Mask(Annotation):

    @staticmethod
    def draw(
        frame: np.ndarray, 
        mask_coco_rle: Dict,
        draw: Dict = {}
    ):
        
        # Get draw parameters
        mask_color = draw.get("mask_color", "#FFFFFF")
        
        # Use pycocotools to decode the mask
        mask_decoded = mask_utils.decode(mask_coco_rle)
        mask = np.array(mask_decoded, dtype=np.uint8)

        # Mask Color
        mask_color = tuple(int(mask_color[i:i + 2], 16) for i in (1, 3, 5))
        mask_color = (mask_color[2], mask_color[1], mask_color[0])
        
        # Create a colored mask
        colored_mask = np.zeros_like(frame, dtype=np.uint8)
        colored_mask[mask > 0] = mask_color

        # Overlay the mask on the frame
        cv2.addWeighted(colored_mask, 0.5, frame, 0.5, 0, frame)

        if draw.get("border_draw", True): 

            # Border Color
            border_color = draw.get("border_color", "#FF00E1")
            border_color = tuple(int(border_color[i:i + 2], 16) for i in (1, 3, 5))
            border_color = (border_color[2], border_color[1], border_color[0])

            # Border Width
            border_width = draw.get("border_width", 2)

            # Draw border
            contours, _ = cv2.findContours(mask.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            for contour in contours:
                frame = cv2.drawContours(frame, [contour], -1, border_color, border_width)

        return frame
    

class Landmarks(Annotation):

    @staticmethod
    def draw(
        frame: np.ndarray, 
        landmarks: List[Tuple[float, float, float]],
        draw: Dict = {}
    ) -> np.ndarray:
        
        # Radius 
        radius = draw.get("points_radius", 4)
        thickness = draw.get("lines_thickness", 2)
        
        # Color 
        color = draw.get("line_color", "#0000FF")
        color = tuple(int(color[i:i + 2], 16) for i in (1, 3, 5))
        color = (color[2], color[1], color[0]) 

        # Color For Points
        point_color = draw.get("points_color", "#00EEFF")
        point_color = tuple(int(point_color[i:i + 2], 16) for i in (1, 3, 5))
        point_color = (point_color[2], point_color[1], point_color[0])

        HAND_CONNECTIONS = [
            # Palm
            (0, 1), (1, 2), (2, 3), (3, 4),         # Thumb
            (0, 5), (5, 6), (6, 7), (7, 8),         # Index
            (5, 9), (9, 10), (10, 11), (11, 12),    # Middle
            (9, 13), (13, 14), (14, 15), (15, 16),  # Ring
            (13, 17), (17, 18), (18, 19), (19, 20), # Pinky
            (0, 17)                                 # Wrist to pinky base
        ]

        h, w = frame.shape[:2]
    
        # Convert normalized landmarks to pixel coordinates
        points = [(int(x * w), int(y * h)) for x, y, z in landmarks]

        # Draw connections
        for start_idx, end_idx in HAND_CONNECTIONS:
            cv2.line(frame, points[start_idx], points[end_idx], color, thickness)

        # Draw landmark points
        for point in points:
            cv2.circle(frame, point, radius, point_color, -1)

        return frame








