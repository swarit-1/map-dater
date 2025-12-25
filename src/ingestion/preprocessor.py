"""
Image preprocessing for historical maps.

Handles: loading, deskewing, denoising, contrast enhancement.
"""

import numpy as np
from typing import Optional
from pathlib import Path
import sys
from dataclasses import dataclass

try:
    import cv2
except ImportError:
    cv2 = None

sys.path.append(str(Path(__file__).parent.parent))
from models import ProcessedImage


class ImagePreprocessor:
    """
    Preprocesses map images for optimal OCR and visual analysis.

    Applies transformations to normalize image quality while preserving
    historical features.
    """

    def __init__(
        self,
        target_dpi: int = 300,
        apply_deskew: bool = True,
        apply_denoise: bool = True,
        enhance_contrast: bool = True,
        apply_binarization: bool = False,
        upscale_factor: float = 1.0
    ):
        """
        Initialize the preprocessor.

        Args:
            target_dpi: Target resolution for processing
            apply_deskew: Whether to correct image rotation
            apply_denoise: Whether to reduce noise
            enhance_contrast: Whether to enhance contrast
            apply_binarization: Whether to apply adaptive thresholding
            upscale_factor: Factor to upscale image for better OCR (1.0 = no scaling)
        """
        if cv2 is None:
            raise ImportError("OpenCV (cv2) is required for image preprocessing")

        self.target_dpi = target_dpi
        self.apply_deskew = apply_deskew
        self.apply_denoise = apply_denoise
        self.enhance_contrast = enhance_contrast
        self.apply_binarization = apply_binarization
        self.upscale_factor = upscale_factor

    def load_image(self, image_path: str) -> np.ndarray:
        """
        Load an image from disk.

        Args:
            image_path: Path to the image file

        Returns:
            Image as numpy array

        Raises:
            FileNotFoundError: If image doesn't exist
            ValueError: If image cannot be loaded
        """
        if not Path(image_path).exists():
            raise FileNotFoundError(f"Image not found: {image_path}")

        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Failed to load image: {image_path}")

        return image

    def _deskew(self, image: np.ndarray) -> np.ndarray:
        """
        Correct skew/rotation in scanned maps.

        Uses Hough line detection to find dominant angles.
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)
        lines = cv2.HoughLines(edges, 1, np.pi / 180, 200)

        if lines is None:
            return image

        # Find the dominant angle
        angles = []
        for line in lines:
            rho, theta = line[0]
            angle = theta * 180 / np.pi
            # Normalize to -45 to 45 range
            if angle > 90:
                angle = angle - 180
            elif angle > 45:
                angle = angle - 90
            angles.append(angle)

        if not angles:
            return image

        median_angle = np.median(angles)

        # Only deskew if angle is significant (> 0.5 degrees)
        if abs(median_angle) > 0.5:
            (h, w) = image.shape[:2]
            center = (w // 2, h // 2)
            M = cv2.getRotationMatrix2D(center, median_angle, 1.0)
            rotated = cv2.warpAffine(
                image, M, (w, h),
                flags=cv2.INTER_CUBIC,
                borderMode=cv2.BORDER_REPLICATE
            )
            return rotated

        return image

    def _denoise(self, image: np.ndarray) -> np.ndarray:
        """
        Apply gentle denoising while preserving text.

        Uses Non-local Means Denoising which is effective for scanned documents.
        """
        # Use color denoising for RGB images
        denoised = cv2.fastNlMeansDenoisingColored(
            image,
            None,
            h=10,  # Filter strength for luminance
            hColor=10,  # Filter strength for color
            templateWindowSize=7,
            searchWindowSize=21
        )
        return denoised

    def _enhance_contrast(self, image: np.ndarray) -> np.ndarray:
        """
        Enhance contrast using CLAHE (Contrast Limited Adaptive Histogram Equalization).

        This improves text readability without over-saturating.
        """
        # Convert to LAB color space
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)

        # Apply CLAHE to L channel
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        l = clahe.apply(l)

        # Merge channels and convert back to BGR
        lab = cv2.merge([l, a, b])
        enhanced = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)

        return enhanced

    def _binarize(self, image: np.ndarray) -> np.ndarray:
        """
        Apply adaptive binarization to create high-contrast text.

        Uses Otsu's method combined with morphological operations
        to create clean black-and-white text suitable for OCR.
        """
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Apply bilateral filter to reduce noise while preserving edges
        filtered = cv2.bilateralFilter(gray, 9, 75, 75)

        # Apply adaptive thresholding
        binary = cv2.adaptiveThreshold(
            filtered,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            11,
            2
        )

        # Morphological operations to clean up
        kernel = np.ones((1, 1), np.uint8)
        binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
        binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)

        # Convert back to BGR for consistency
        return cv2.cvtColor(binary, cv2.COLOR_GRAY2BGR)

    def _upscale(self, image: np.ndarray, factor: float) -> np.ndarray:
        """
        Upscale image for better OCR accuracy.

        Uses high-quality interpolation to preserve text quality.

        Args:
            image: Input image
            factor: Scaling factor (e.g., 2.0 = double size)

        Returns:
            Upscaled image
        """
        if factor == 1.0:
            return image

        height, width = image.shape[:2]
        new_width = int(width * factor)
        new_height = int(height * factor)

        # Use INTER_CUBIC for upscaling (better quality)
        upscaled = cv2.resize(
            image,
            (new_width, new_height),
            interpolation=cv2.INTER_CUBIC
        )

        return upscaled

    def process(self, image_path: str) -> ProcessedImage:
        """
        Apply full preprocessing pipeline to an image.

        Args:
            image_path: Path to the input image

        Returns:
            ProcessedImage with applied transformations

        Raises:
            FileNotFoundError: If image doesn't exist
            ValueError: If image cannot be processed
        """
        image = self.load_image(image_path)
        applied_steps = []

        # Upscale first if requested (before other operations)
        if self.upscale_factor != 1.0:
            image = self._upscale(image, self.upscale_factor)
            applied_steps.append(f"upscale_{self.upscale_factor}x")

        if self.apply_deskew:
            image = self._deskew(image)
            applied_steps.append("deskew")

        if self.apply_denoise:
            image = self._denoise(image)
            applied_steps.append("denoise")

        if self.enhance_contrast:
            image = self._enhance_contrast(image)
            applied_steps.append("contrast_enhancement")

        # Binarization should be last (if enabled)
        if self.apply_binarization:
            image = self._binarize(image)
            applied_steps.append("binarization")

        height, width = image.shape[:2]

        return ProcessedImage(
            image_data=image,
            original_path=image_path,
            width=width,
            height=height,
            preprocessing_applied=applied_steps
        )

    def save_processed_image(self, processed: ProcessedImage, output_path: str) -> None:
        """
        Save a processed image to disk.

        Args:
            processed: ProcessedImage to save
            output_path: Where to save the image
        """
        cv2.imwrite(output_path, processed.image_data)
