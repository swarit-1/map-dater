"""
Map Renderer for Historical Map Generation.

Renders historical map images in an old-world cartographic style.
Outputs PNG images with muted colors and serif-style labels.
"""

from dataclasses import dataclass, field
from typing import List, Tuple, Optional, Dict, Any
from pathlib import Path
import io
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from models import YearRange
from .boundary_engine import BoundarySet, Polygon, Point, UncertaintyRegion


@dataclass
class RenderConfig:
    """
    Configuration for map rendering.

    Attributes:
        width: Output image width in pixels
        height: Output image height in pixels
        background_color: Background/ocean color
        land_default_color: Default land color
        border_color: Color for borders
        border_width: Width of borders in pixels
        show_labels: Whether to show country/city labels
        show_uncertainty: Whether to show uncertainty regions
        title: Optional title for the map
        style: Rendering style ('antique', 'modern', 'simple')
    """
    width: int = 1200
    height: int = 800
    background_color: str = '#B8D4E8'  # Light blue for oceans
    land_default_color: str = '#E8D4B8'  # Beige for land
    border_color: str = '#4A3728'  # Dark brown for borders
    border_width: int = 2
    show_labels: bool = True
    show_uncertainty: bool = True
    title: Optional[str] = None
    style: str = 'antique'
    font_size: int = 12
    title_font_size: int = 24


class MapRenderer:
    """
    Renders historical maps from boundary data.

    Creates old-world cartographic style images using:
    - Muted, earth-tone color palettes
    - Serif-style labeling
    - Optional uncertainty visualization
    """

    # Projection bounds (simple equirectangular projection)
    # Longitude: -180 to 180
    # Latitude: -60 to 85 (excluding extreme polar regions)
    MIN_LON = -180
    MAX_LON = 180
    MIN_LAT = -60
    MAX_LAT = 85

    # Antique style color palette
    ANTIQUE_PALETTE = {
        'ocean': '#B8C9D4',
        'land': '#E8D4B8',
        'border': '#4A3728',
        'text': '#2F1810',
        'title': '#1A0F0A',
        'grid': '#A09080',
        'uncertainty': '#FFE4B5',
    }

    # Modern style color palette
    MODERN_PALETTE = {
        'ocean': '#4A90C2',
        'land': '#E5E5E0',
        'border': '#333333',
        'text': '#000000',
        'title': '#000000',
        'grid': '#CCCCCC',
        'uncertainty': '#FFFF99',
    }

    def __init__(self, config: Optional[RenderConfig] = None):
        """
        Initialize the renderer.

        Args:
            config: Optional render configuration. Uses defaults if not provided.
        """
        self.config = config or RenderConfig()
        self._palette = (
            self.ANTIQUE_PALETTE if self.config.style == 'antique'
            else self.MODERN_PALETTE
        )

    def render(
        self,
        boundaries: BoundarySet,
        output_path: Optional[str] = None
    ) -> bytes:
        """
        Render a map from boundary data.

        Args:
            boundaries: BoundarySet containing all polygons and uncertainty
            output_path: Optional path to save the image

        Returns:
            PNG image as bytes
        """
        try:
            # Try to use Pillow for rendering
            return self._render_with_pillow(boundaries, output_path)
        except ImportError:
            # Fall back to SVG if Pillow not available
            svg_data = self._render_as_svg(boundaries)
            if output_path:
                svg_path = output_path.replace('.png', '.svg')
                with open(svg_path, 'w', encoding='utf-8') as f:
                    f.write(svg_data)
            return svg_data.encode('utf-8')

    def _render_with_pillow(
        self,
        boundaries: BoundarySet,
        output_path: Optional[str]
    ) -> bytes:
        """Render using Pillow (PIL)."""
        from PIL import Image, ImageDraw, ImageFont

        # Create image
        img = Image.new(
            'RGB',
            (self.config.width, self.config.height),
            self._hex_to_rgb(self._palette['ocean'])
        )
        draw = ImageDraw.Draw(img)

        # Try to load a serif font, fall back to default
        try:
            font = ImageFont.truetype("times.ttf", self.config.font_size)
            title_font = ImageFont.truetype("times.ttf", self.config.title_font_size)
        except (IOError, OSError):
            font = ImageFont.load_default()
            title_font = font

        # Draw grid lines (optional, for antique style)
        if self.config.style == 'antique':
            self._draw_grid(draw)

        # Draw uncertainty regions first (background)
        if self.config.show_uncertainty:
            for region in boundaries.uncertainty_regions:
                self._draw_polygon_pillow(
                    draw,
                    region.polygon,
                    fill_opacity=0.3
                )

        # Draw country polygons
        for polygon in boundaries.country_polygons:
            self._draw_polygon_pillow(draw, polygon)

        # Draw city markers
        for marker in boundaries.city_markers:
            self._draw_city_marker_pillow(draw, marker)

        # Draw labels
        if self.config.show_labels:
            for polygon in boundaries.polygons:
                if polygon.entity_type != 'uncertainty':
                    self._draw_label_pillow(draw, polygon, font)

        # Draw title
        if self.config.title:
            self._draw_title_pillow(draw, self.config.title, title_font)
        elif boundaries.date_range:
            title = f"World Map: {boundaries.date_range}"
            self._draw_title_pillow(draw, title, title_font)

        # Save to bytes
        output = io.BytesIO()
        img.save(output, format='PNG')
        image_bytes = output.getvalue()

        # Optionally save to file
        if output_path:
            img.save(output_path, format='PNG')

        return image_bytes

    def _draw_grid(self, draw):
        """Draw latitude/longitude grid lines."""
        grid_color = self._hex_to_rgb(self._palette['grid'])

        # Longitude lines every 30 degrees
        for lon in range(-180, 181, 30):
            x = self._lon_to_x(lon)
            draw.line([(x, 0), (x, self.config.height)], fill=grid_color, width=1)

        # Latitude lines every 30 degrees
        for lat in range(-60, 91, 30):
            y = self._lat_to_y(lat)
            draw.line([(0, y), (self.config.width, y)], fill=grid_color, width=1)

    def _draw_polygon_pillow(
        self,
        draw,
        polygon: Polygon,
        fill_opacity: float = 1.0
    ):
        """Draw a polygon using Pillow."""
        # Convert points to pixel coordinates
        pixel_points = [
            (self._lon_to_x(p.x), self._lat_to_y(p.y))
            for p in polygon.points
        ]

        if not pixel_points:
            return

        # Parse colors
        fill_color = self._hex_to_rgb(polygon.fill_color)
        border_color = self._hex_to_rgb(polygon.border_color)

        # Draw fill
        if fill_opacity < 1.0:
            # Blend with background for transparency effect
            fill_color = tuple(
                int(c * fill_opacity + 255 * (1 - fill_opacity))
                for c in fill_color
            )

        draw.polygon(pixel_points, fill=fill_color, outline=border_color)

    def _draw_city_marker_pillow(self, draw, marker: Polygon):
        """Draw a city marker (small circle with dot)."""
        if not marker.points:
            return

        # Use centroid for marker position
        center_x = self._lon_to_x(marker.centroid.x)
        center_y = self._lat_to_y(marker.centroid.y)

        # Draw marker
        radius = 4
        fill_color = self._hex_to_rgb('#8B4513')  # Brown
        draw.ellipse(
            [center_x - radius, center_y - radius,
             center_x + radius, center_y + radius],
            fill=fill_color,
            outline=self._hex_to_rgb('#000000')
        )

    def _draw_label_pillow(self, draw, polygon: Polygon, font):
        """Draw a label for a polygon."""
        label_pos = polygon.get_label_position()
        x = self._lon_to_x(label_pos.x)
        y = self._lat_to_y(label_pos.y)

        text_color = self._hex_to_rgb(self._palette['text'])

        # Get text bounds for centering
        text = polygon.entity_name
        try:
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
        except AttributeError:
            # Older Pillow version
            text_width, text_height = draw.textsize(text, font=font)

        # Center the text
        x -= text_width // 2
        y -= text_height // 2

        # Draw text with slight shadow for readability
        shadow_color = self._hex_to_rgb('#FFFFFF')
        draw.text((x + 1, y + 1), text, font=font, fill=shadow_color)
        draw.text((x, y), text, font=font, fill=text_color)

    def _draw_title_pillow(self, draw, title: str, font):
        """Draw the map title."""
        text_color = self._hex_to_rgb(self._palette['title'])

        # Get text bounds
        try:
            bbox = draw.textbbox((0, 0), title, font=font)
            text_width = bbox[2] - bbox[0]
        except AttributeError:
            text_width, _ = draw.textsize(title, font=font)

        # Center at top
        x = (self.config.width - text_width) // 2
        y = 20

        draw.text((x, y), title, font=font, fill=text_color)

    def _render_as_svg(self, boundaries: BoundarySet) -> str:
        """
        Render as SVG for maximum clarity.

        This is the preferred format for historical maps.
        """
        svg_parts = [
            f'<?xml version="1.0" encoding="UTF-8"?>',
            f'<svg xmlns="http://www.w3.org/2000/svg" '
            f'width="{self.config.width}" height="{self.config.height}" '
            f'viewBox="0 0 {self.config.width} {self.config.height}">',
            '',
            '<!-- Historical Map Generated by Map Dater -->',
            f'<!-- Date Range: {boundaries.date_range} -->',
            '',
            '<!-- Styles -->',
            '<defs>',
            '  <style>',
            f'    .ocean {{ fill: {self._palette["ocean"]}; }}',
            f'    .land {{ fill: {self._palette["land"]}; stroke: {self._palette["border"]}; stroke-width: 1; }}',
            f'    .label {{ font-family: "Times New Roman", serif; font-size: {self.config.font_size}px; fill: {self._palette["text"]}; }}',
            f'    .title {{ font-family: "Times New Roman", serif; font-size: {self.config.title_font_size}px; fill: {self._palette["title"]}; font-weight: bold; }}',
            f'    .uncertainty {{ fill: {self._palette["uncertainty"]}; fill-opacity: 0.3; stroke: #FF8C00; stroke-width: 1; stroke-dasharray: 5,3; }}',
            f'    .city {{ fill: #8B4513; stroke: #000000; stroke-width: 1; }}',
            f'    .grid {{ stroke: {self._palette["grid"]}; stroke-width: 0.5; }}',
            '  </style>',
            '</defs>',
            '',
            '<!-- Background (Ocean) -->',
            f'<rect class="ocean" width="100%" height="100%"/>',
            '',
        ]

        # Grid lines
        if self.config.style == 'antique':
            svg_parts.append('<!-- Grid Lines -->')
            for lon in range(-180, 181, 30):
                x = self._lon_to_x(lon)
                svg_parts.append(
                    f'<line class="grid" x1="{x}" y1="0" x2="{x}" y2="{self.config.height}"/>'
                )
            for lat in range(-60, 91, 30):
                y = self._lat_to_y(lat)
                svg_parts.append(
                    f'<line class="grid" x1="0" y1="{y}" x2="{self.config.width}" y2="{y}"/>'
                )
            svg_parts.append('')

        # Uncertainty regions
        if self.config.show_uncertainty and boundaries.uncertainty_regions:
            svg_parts.append('<!-- Uncertainty Regions -->')
            for region in boundaries.uncertainty_regions:
                path_d = self._polygon_to_path(region.polygon)
                svg_parts.append(
                    f'<path class="uncertainty" d="{path_d}"/>'
                )
            svg_parts.append('')

        # Country polygons
        svg_parts.append('<!-- Countries and Territories -->')
        for polygon in boundaries.country_polygons:
            path_d = self._polygon_to_path(polygon)
            svg_parts.append(
                f'<path class="land" style="fill: {polygon.fill_color};" d="{path_d}"/>'
            )
        svg_parts.append('')

        # City markers
        svg_parts.append('<!-- Cities -->')
        for marker in boundaries.city_markers:
            cx = self._lon_to_x(marker.centroid.x)
            cy = self._lat_to_y(marker.centroid.y)
            svg_parts.append(
                f'<circle class="city" cx="{cx}" cy="{cy}" r="4"/>'
            )
        svg_parts.append('')

        # Labels
        if self.config.show_labels:
            svg_parts.append('<!-- Labels -->')
            for polygon in boundaries.polygons:
                if polygon.entity_type != 'uncertainty':
                    label_pos = polygon.get_label_position()
                    x = self._lon_to_x(label_pos.x)
                    y = self._lat_to_y(label_pos.y)
                    svg_parts.append(
                        f'<text class="label" x="{x}" y="{y}" '
                        f'text-anchor="middle" dominant-baseline="middle">'
                        f'{polygon.entity_name}</text>'
                    )
            svg_parts.append('')

        # Title
        title = self.config.title or f"World Map: {boundaries.date_range}"
        svg_parts.append('<!-- Title -->')
        svg_parts.append(
            f'<text class="title" x="{self.config.width // 2}" y="30" '
            f'text-anchor="middle">{title}</text>'
        )

        svg_parts.append('')
        svg_parts.append('</svg>')

        return '\n'.join(svg_parts)

    def _polygon_to_path(self, polygon: Polygon) -> str:
        """Convert a polygon to SVG path data."""
        if not polygon.points:
            return ""

        path_parts = []
        for i, point in enumerate(polygon.points):
            x = self._lon_to_x(point.x)
            y = self._lat_to_y(point.y)
            if i == 0:
                path_parts.append(f"M {x:.1f} {y:.1f}")
            else:
                path_parts.append(f"L {x:.1f} {y:.1f}")
        path_parts.append("Z")

        return " ".join(path_parts)

    def _lon_to_x(self, lon: float) -> float:
        """Convert longitude to x pixel coordinate."""
        return (lon - self.MIN_LON) / (self.MAX_LON - self.MIN_LON) * self.config.width

    def _lat_to_y(self, lat: float) -> float:
        """Convert latitude to y pixel coordinate (inverted for screen coords)."""
        return (self.MAX_LAT - lat) / (self.MAX_LAT - self.MIN_LAT) * self.config.height

    def _hex_to_rgb(self, hex_color: str) -> Tuple[int, int, int]:
        """Convert hex color to RGB tuple."""
        hex_color = hex_color.lstrip('#')
        if len(hex_color) == 6:
            return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        elif len(hex_color) == 8:
            # RGBA - ignore alpha
            return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        else:
            return (128, 128, 128)  # Default gray

    def render_to_file(
        self,
        boundaries: BoundarySet,
        output_path: str,
        format: str = 'png'
    ) -> str:
        """
        Render and save to a file.

        Args:
            boundaries: BoundarySet to render
            output_path: Path to save the file
            format: 'png' or 'svg'

        Returns:
            Path to the saved file
        """
        if format.lower() == 'svg':
            svg_data = self._render_as_svg(boundaries)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(svg_data)
        else:
            self.render(boundaries, output_path)

        return output_path
