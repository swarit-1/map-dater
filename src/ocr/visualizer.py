"""
OCR visualization tools for debugging and analysis.

Creates visual representations of text detection results.
"""

import numpy as np
from typing import List, Optional, Tuple
from pathlib import Path
import sys

try:
    import cv2
except ImportError:
    cv2 = None

sys.path.append(str(Path(__file__).parent.parent))
from models import TextBlock, ProcessedImage


class OCRVisualizer:
    """
    Visualizes OCR results by drawing bounding boxes and text on images.

    Useful for debugging OCR quality and understanding what text was extracted.
    """

    def __init__(
        self,
        box_color: Tuple[int, int, int] = (0, 255, 0),  # Green
        text_color: Tuple[int, int, int] = (255, 0, 0),  # Blue
        box_thickness: int = 2,
        font_scale: float = 0.5,
        show_confidence: bool = True
    ):
        """
        Initialize the visualizer.

        Args:
            box_color: BGR color for bounding boxes
            text_color: BGR color for text labels
            box_thickness: Thickness of bounding box lines
            font_scale: Scale of text labels
            show_confidence: Whether to show confidence scores
        """
        if cv2 is None:
            raise ImportError("OpenCV (cv2) is required for visualization")

        self.box_color = box_color
        self.text_color = text_color
        self.box_thickness = box_thickness
        self.font_scale = font_scale
        self.show_confidence = show_confidence

    def visualize_text_blocks(
        self,
        processed_image: ProcessedImage,
        text_blocks: List[TextBlock],
        output_path: Optional[str] = None
    ) -> np.ndarray:
        """
        Draw bounding boxes around detected text.

        Args:
            processed_image: The processed image
            text_blocks: List of detected text blocks
            output_path: Optional path to save the visualization

        Returns:
            Image with bounding boxes drawn
        """
        # Create a copy to draw on
        image = processed_image.image_data.copy()

        for block in text_blocks:
            # Draw bounding box
            x, y, w, h = block.bbox.x, block.bbox.y, block.bbox.width, block.bbox.height
            cv2.rectangle(
                image,
                (x, y),
                (x + w, y + h),
                self.box_color,
                self.box_thickness
            )

            # Prepare label
            if self.show_confidence:
                label = f"{block.text} ({block.confidence:.2f})"
            else:
                label = block.text

            # Draw label background
            (label_width, label_height), _ = cv2.getTextSize(
                label,
                cv2.FONT_HERSHEY_SIMPLEX,
                self.font_scale,
                1
            )

            # Draw filled rectangle for text background
            cv2.rectangle(
                image,
                (x, y - label_height - 5),
                (x + label_width, y),
                self.box_color,
                -1  # Filled
            )

            # Draw text
            cv2.putText(
                image,
                label,
                (x, y - 5),
                cv2.FONT_HERSHEY_SIMPLEX,
                self.font_scale,
                self.text_color,
                1,
                cv2.LINE_AA
            )

        if output_path:
            cv2.imwrite(output_path, image)

        return image

    def create_word_map(
        self,
        processed_image: ProcessedImage,
        text_blocks: List[TextBlock],
        output_path: Optional[str] = None,
        background_color: Tuple[int, int, int] = (255, 255, 255)
    ) -> np.ndarray:
        """
        Create a "word map" showing only the detected text in their original positions.

        This helps visualize the spatial layout of detected text without the map image.

        Args:
            processed_image: The processed image
            text_blocks: List of detected text blocks
            output_path: Optional path to save the word map
            background_color: Background color for the word map

        Returns:
            Word map image
        """
        # Create blank canvas
        height, width = processed_image.height, processed_image.width
        word_map = np.full((height, width, 3), background_color, dtype=np.uint8)

        for block in text_blocks:
            x, y, w, h = block.bbox.x, block.bbox.y, block.bbox.width, block.bbox.height

            # Calculate font size based on bounding box height
            font_scale = h / 30.0  # Approximate scaling

            # Draw text at original position
            cv2.putText(
                word_map,
                block.text,
                (x, y + h - 5),  # Align to bottom of bbox
                cv2.FONT_HERSHEY_SIMPLEX,
                font_scale,
                (0, 0, 0),  # Black text
                max(1, int(font_scale * 2)),
                cv2.LINE_AA
            )

        if output_path:
            cv2.imwrite(output_path, word_map)

        return word_map

    def create_heatmap(
        self,
        processed_image: ProcessedImage,
        text_blocks: List[TextBlock],
        output_path: Optional[str] = None
    ) -> np.ndarray:
        """
        Create a confidence heatmap showing OCR quality across the image.

        Args:
            processed_image: The processed image
            text_blocks: List of detected text blocks
            output_path: Optional path to save the heatmap

        Returns:
            Heatmap image
        """
        # Create grayscale heatmap
        height, width = processed_image.height, processed_image.width
        heatmap = np.zeros((height, width), dtype=np.float32)

        for block in text_blocks:
            x, y, w, h = block.bbox.x, block.bbox.y, block.bbox.width, block.bbox.height
            # Ensure coordinates are within bounds
            x1, y1 = max(0, x), max(0, y)
            x2, y2 = min(width, x + w), min(height, y + h)

            heatmap[y1:y2, x1:x2] = block.confidence

        # Convert to color heatmap
        heatmap_normalized = (heatmap * 255).astype(np.uint8)
        heatmap_color = cv2.applyColorMap(heatmap_normalized, cv2.COLORMAP_JET)

        # Overlay on original image
        overlay = cv2.addWeighted(
            processed_image.image_data,
            0.7,
            heatmap_color,
            0.3,
            0
        )

        if output_path:
            cv2.imwrite(output_path, overlay)

        return overlay

    def create_summary_visualization(
        self,
        processed_image: ProcessedImage,
        text_blocks: List[TextBlock],
        output_path: Optional[str] = None
    ) -> np.ndarray:
        """
        Create a comprehensive summary visualization with multiple views.

        Args:
            processed_image: The processed image
            text_blocks: List of detected text blocks
            output_path: Optional path to save the summary

        Returns:
            Summary visualization image
        """
        # Create all visualizations
        bbox_vis = self.visualize_text_blocks(processed_image, text_blocks)
        word_map = self.create_word_map(processed_image, text_blocks)
        heatmap = self.create_heatmap(processed_image, text_blocks)

        # Resize to same height for horizontal stacking
        target_height = 600

        def resize_maintaining_aspect(img, height):
            h, w = img.shape[:2]
            aspect = w / h
            new_width = int(height * aspect)
            return cv2.resize(img, (new_width, height))

        bbox_resized = resize_maintaining_aspect(bbox_vis, target_height)
        word_map_resized = resize_maintaining_aspect(word_map, target_height)
        heatmap_resized = resize_maintaining_aspect(heatmap, target_height)

        # Add labels
        def add_title(img, title):
            img_copy = img.copy()
            cv2.putText(
                img_copy,
                title,
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.0,
                (255, 255, 255),
                3,
                cv2.LINE_AA
            )
            cv2.putText(
                img_copy,
                title,
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.0,
                (0, 0, 0),
                2,
                cv2.LINE_AA
            )
            return img_copy

        bbox_titled = add_title(bbox_resized, "Detected Text")
        word_map_titled = add_title(word_map_resized, "Word Map")
        heatmap_titled = add_title(heatmap_resized, "Confidence Heatmap")

        # Stack horizontally
        summary = np.hstack([bbox_titled, word_map_titled, heatmap_titled])

        if output_path:
            cv2.imwrite(output_path, summary)

        return summary
