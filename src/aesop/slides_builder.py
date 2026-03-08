"""
Google Slides presentation builder.

Creates and populates Google Slides presentations with text and images.
Supports both public image URLs and local file paths (uploads to Drive temporarily).
"""

from __future__ import annotations

import os
import re
import sys
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Sequence

if TYPE_CHECKING:
    from aesop.storybrand_schema import StoryBrandSchema

# EMU = English Metric Units (1 inch = 914400 EMU, 1 pt = 12700 EMU)
PT_TO_EMU = 12_700
# Default slide size: 10" x 7.5" (1 inch = 72 pt)
SLIDE_WIDTH_PT = 720
SLIDE_HEIGHT_PT = 540
MARGIN_PT = 36  # 0.5 inch
DEFAULT_IMAGE_SIZE_PT = 72  # 1 inch
IMAGE_COLUMN_WIDTH_PT = 180  # 2.5" for side-by-side layout
GAP_PT = 18


@dataclass
class SlideContent:
    """Content for a single slide.

    Attributes:
        title: Optional slide title (displayed prominently at top).
        body: Body text content. Can be a single string or list of paragraphs.
        images: List of image sources. Each can be:
            - A publicly accessible URL (http/https)
            - A local file path (will be uploaded to Drive first)

    Example:
        SlideContent(
            title="Introduction",
            body="Welcome to our presentation. Key points:\n• Item one\n• Item two",
            images=["https://example.com/photo.png", "/path/to/local/image.jpg"]
        )
    """

    title: str | None = None
    body: str | list[str] | None = None
    images: list[str] = field(default_factory=list)


def create_presentation(
    title: str,
    slides: Sequence[SlideContent],
    credentials_path: str = "credentials.json",
    token_path: str = "token.json",
) -> str:
    """Create and populate a Google Slides presentation.

    Args:
        title: Presentation title.
        slides: List of SlideContent objects, one per slide.
        credentials_path: Path to OAuth2 credentials JSON.
        token_path: Path to store/load OAuth2 token.

    Returns:
        The presentation URL (e.g. https://docs.google.com/presentation/d/ID/edit).

    Raises:
        FileNotFoundError: If credentials_path does not exist.
        Exception: On API or authentication errors.
    """
    builder = GoogleSlidesBuilder(credentials_path=credentials_path, token_path=token_path)
    return builder.create_and_populate(title=title, slides=slides)


def create_presentation_from_storybrand_json(
    json_str: str,
    title: str = "StoryBrand Presentation",
    credentials_path: str = "credentials.json",
    token_path: str = "token.json",
) -> str:
    """Create a presentation from a StoryBrand framework JSON string.

    Parses the JSON into a StoryBrandSchema, converts each slide to SlideContent,
    and creates the presentation.

    Args:
        json_str: JSON string matching the StoryBrand schema (slides keyed by id).
        title: Presentation title.
        credentials_path: Path to OAuth2 credentials JSON.
        token_path: Path to store/load OAuth2 token.

    Returns:
        The presentation URL.
    """
    from aesop.storybrand_schema import StoryBrandSchema

    schema = StoryBrandSchema.from_json(json_str)
    slides_content = _storybrand_to_slide_content(schema)
    return create_presentation(
        title=title,
        slides=slides_content,
        credentials_path=credentials_path,
        token_path=token_path,
    )


def _storybrand_to_slide_content(schema: StoryBrandSchema) -> list[SlideContent]:
    """Convert a StoryBrandSchema to a list of SlideContent."""
    return [
        SlideContent(
            title=slide.title,
            body=slide.description,
            images=[slide.image_url] if slide.image_url.strip() else [],
        )
        for slide in schema.slides
    ]


class GoogleSlidesBuilder:
    """Builds Google Slides presentations from structured content."""

    SCOPES = [
        "https://www.googleapis.com/auth/presentations",
        "https://www.googleapis.com/auth/drive.file",
        "https://www.googleapis.com/auth/drive",
    ]

    def __init__(
        self,
        credentials_path: str = "credentials.json",
        token_path: str = "token.json",
    ) -> None:
        """Initialize the builder with auth paths.

        Args:
            credentials_path: Path to OAuth2 client credentials.
            token_path: Path for storing OAuth2 tokens.
        """
        self.credentials_path = credentials_path
        self.token_path = token_path
        self._slides_service = None
        self._drive_service = None

    def _get_credentials(self):
        """Load or refresh OAuth2 credentials."""
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow

        creds = None
        if os.path.exists(self.token_path):
            creds = Credentials.from_authorized_user_file(self.token_path, self.SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(self.credentials_path):
                    raise FileNotFoundError(
                        f"Credentials not found at {self.credentials_path}. "
                        "Download OAuth2 client secrets from Google Cloud Console "
                        "and save as credentials.json."
                    )
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, self.SCOPES
                )
                creds = flow.run_local_server(port=0)
            with open(self.token_path, "w") as f:
                f.write(creds.to_json())
        return creds

    def _get_slides_service(self):
        """Lazy-initialize Slides API service."""
        if self._slides_service is None:
            from googleapiclient.discovery import build

            creds = self._get_credentials()
            self._slides_service = build("slides", "v1", credentials=creds)
        return self._slides_service

    def _get_drive_service(self):
        """Lazy-initialize Drive API service (for local image uploads)."""
        if self._drive_service is None:
            from googleapiclient.discovery import build

            creds = self._get_credentials()
            self._drive_service = build("drive", "v3", credentials=creds)
        return self._drive_service

    def _resolve_image_url(self, source: str) -> str:
        """Convert image source to a publicly accessible URL.

        If source is http(s), return as-is (converting Drive view URLs to
        direct download format). If local path, upload to Drive and return
        public URL.
        """
        if source.startswith(("http://", "https://")):
            return self._convert_drive_url_to_direct(source)
        path = Path(source)
        if not path.exists():
            raise FileNotFoundError(f"Image not found: {source}")
        return self._upload_image_to_drive(path)

    def _convert_drive_url_to_direct(self, url: str) -> str:
        """Convert Google Drive view/share URLs to direct download format.

        Drive view URLs (e.g. .../file/d/ID/view) return HTML, not image
        bytes. The Slides API requires a URL that serves raw image data.
        """
        # Match: drive.google.com/file/d/FILE_ID/view or /open?id=FILE_ID
        match = re.search(r"/d/([a-zA-Z0-9_-]+)", url)
        if not match:
            match = re.search(r"[?&]id=([a-zA-Z0-9_-]+)", url)
        if match:
            file_id = match.group(1)
            return f"https://drive.google.com/uc?export=download&id={file_id}"
        return url

    def _upload_image_to_drive(self, path: Path) -> str:
        """Upload local image to Drive, make public, return URL."""
        from googleapiclient.http import MediaFileUpload

        drive = self._get_drive_service()
        mime = "image/png" if path.suffix.lower() == ".png" else "image/jpeg"
        media = MediaFileUpload(str(path), mimetype=mime, resumable=True)
        file_metadata = {"name": path.name}
        result = drive.files().create(
            body=file_metadata,
            media_body=media,
            fields="id, webContentLink",
        ).execute()
        file_id = result["id"]
        drive.permissions().create(
            fileId=file_id,
            body={"type": "anyone", "role": "reader"},
        ).execute()
        url = result.get("webContentLink")
        if not url:
            url = f"https://drive.google.com/uc?export=download&id={file_id}"
        return url

    def _generate_object_id(self, prefix: str) -> str:
        """Generate a unique object ID for Slides API."""
        safe = re.sub(r"[^a-zA-Z0-9_-]", "", prefix)[:20]
        return f"{safe}_{uuid.uuid4().hex[:8]}"

    def _pt_to_emu(self, pt: float) -> dict:
        """Convert points to EMU dimension dict."""
        return {"magnitude": int(pt * PT_TO_EMU), "unit": "EMU"}

    def create_and_populate(
        self, title: str, slides: Sequence[SlideContent]
    ) -> str:
        """Create a new presentation and populate it with slides.

        Args:
            title: Presentation title.
            slides: Sequence of SlideContent for each slide.

        Returns:
            The presentation URL.
        """
        from googleapiclient.errors import HttpError

        service = self._get_slides_service()

        presentation = (
            service.presentations()
            .create(body={"title": title})
            .execute()
        )
        presentation_id = presentation["presentationId"]
        existing_slides = presentation.get("slides", [])

        if not slides:
            return self._presentation_url(presentation_id)

        requests = []
        for idx, content in enumerate(slides):
            slide_id = self._generate_object_id(f"Slide_{idx}")
            requests.append(
                {
                    "createSlide": {
                        "objectId": slide_id,
                        "insertionIndex": idx + 1,
                        "slideLayoutReference": {"predefinedLayout": "BLANK"},
                    }
                }
            )

        body = {"requests": requests}
        try:
            service.presentations().batchUpdate(
                presentationId=presentation_id, body=body
            ).execute()
        except HttpError as e:
            raise RuntimeError(f"Failed to create slides: {e}") from e

        # Remove default blank slide if it exists
        if existing_slides:
            default_slide_id = existing_slides[0]["objectId"]
            service.presentations().batchUpdate(
                presentationId=presentation_id,
                body={"requests": [{"deleteObject": {"objectId": default_slide_id}}]},
            ).execute()

        for idx, content in enumerate(slides):
            slide_id = requests[idx]["createSlide"]["objectId"]
            self._populate_slide(
                presentation_id=presentation_id,
                slide_id=slide_id,
                content=content,
                slide_index=idx,
            )

        return self._presentation_url(presentation_id)

    def _populate_slide(
        self, presentation_id: str, slide_id: str, content: SlideContent, slide_index: int
    ) -> None:
        """Add text and images to a slide via batchUpdate."""
        from googleapiclient.errors import HttpError

        service = self._get_slides_service()
        requests = []
        y_offset_pt = MARGIN_PT  # 0.5" from top
        content_width_pt = SLIDE_WIDTH_PT - 2 * MARGIN_PT  # 9"
        x_center_pt = MARGIN_PT  # left edge of content area (centered with margins)

        if content.title:
            title_height_pt = 54  # ~0.75"
            title_id = self._generate_object_id(f"Title_{slide_index}")
            is_title_slide = slide_index == 0
            requests.extend(
                self._create_text_box_requests(
                    slide_id=slide_id,
                    object_id=title_id,
                    text=content.title,
                    x_pt=x_center_pt,
                    y_pt=y_offset_pt,
                    width_pt=content_width_pt,
                    height_pt=title_height_pt,
                    font_size_pt=24,
                    center_text=is_title_slide,
                    foreground_color={"red": 0, "green": 0, "blue": 0}
                    if is_title_slide
                    else None,
                )
            )
            y_offset_pt += title_height_pt + GAP_PT

        # Side-by-side layout when images exist: text left, images right
        has_images = bool(content.images)
        content_area_height_pt = SLIDE_HEIGHT_PT - y_offset_pt - MARGIN_PT
        if has_images:
            text_width_pt = content_width_pt - IMAGE_COLUMN_WIDTH_PT - GAP_PT
            image_x_pt = MARGIN_PT + text_width_pt + GAP_PT
            body_height_pt = min(240, content_area_height_pt)  # ~3.3", keeps it compact
        else:
            text_width_pt = content_width_pt
            body_height_pt = content_area_height_pt

        if content.body:
            body_text = (
                "\n".join(content.body)
                if isinstance(content.body, list)
                else content.body
            )
            body_id = self._generate_object_id(f"Body_{slide_index}")
            requests.extend(
                self._create_text_box_requests(
                    slide_id=slide_id,
                    object_id=body_id,
                    text=body_text,
                    x_pt=x_center_pt,
                    y_pt=y_offset_pt,
                    width_pt=text_width_pt,
                    height_pt=body_height_pt,
                    font_size_pt=14,
                )
            )
            if not has_images:
                y_offset_pt += body_height_pt + GAP_PT

        image_requests = []
        image_y_pt = y_offset_pt
        for img_idx, img_source in enumerate(content.images):
            try:
                url = self._resolve_image_url(img_source)
            except FileNotFoundError:
                continue
            image_id = self._generate_object_id(f"Img_{slide_index}_{img_idx}")
            if has_images:
                size_pt = IMAGE_COLUMN_WIDTH_PT
                x_pt = image_x_pt
                y_pt = image_y_pt + img_idx * (size_pt + GAP_PT)
            else:
                size_pt = DEFAULT_IMAGE_SIZE_PT
                x_pt = MARGIN_PT + (img_idx % 3) * (size_pt + GAP_PT)
                y_pt = image_y_pt + (img_idx // 3) * (size_pt + GAP_PT)
            image_requests.append(
                {
                    "createImage": {
                        "objectId": image_id,
                        "url": url,
                        "elementProperties": {
                            "pageObjectId": slide_id,
                            "size": {
                                "height": self._pt_to_emu(size_pt),
                                "width": self._pt_to_emu(size_pt),
                            },
                            "transform": {
                                "scaleX": 1,
                                "scaleY": 1,
                                "translateX": self._pt_to_emu(x_pt)["magnitude"],
                                "translateY": self._pt_to_emu(y_pt)["magnitude"],
                                "unit": "EMU",
                            },
                        },
                    }
                }
            )

        if requests:
            # Execute text requests in chunks to avoid 500 "Internal error"
            batch_size = 8
            for i in range(0, len(requests), batch_size):
                chunk = requests[i : i + batch_size]
                service.presentations().batchUpdate(
                    presentationId=presentation_id, body={"requests": chunk}
                ).execute()

        # Execute image requests separately; skip any that fail (e.g. too large)
        for req in image_requests:
            try:
                service.presentations().batchUpdate(
                    presentationId=presentation_id, body={"requests": [req]}
                ).execute()
            except HttpError as e:
                print(f"Warning: Skipped image - {e}", file=sys.stderr)

    def _create_text_box_requests(
        self,
        slide_id: str,
        object_id: str,
        text: str,
        x_pt: float,
        y_pt: float,
        width_pt: float,
        height_pt: float,
        font_size_pt: int = 12,
        center_text: bool = False,
        foreground_color: dict | None = None,
    ) -> list[dict]:
        """Build requests to create a text box and insert text.

        Args:
            slide_id: Target slide object ID.
            object_id: Unique ID for the new shape.
            text: Text content.
            x_pt: X position in points.
            y_pt: Y position in points.
            width_pt: Box width in points.
            height_pt: Box height in points.
            font_size_pt: Font size in points.
            center_text: If True, center-align paragraph text.
            foreground_color: Optional RGB dict with red/green/blue 0-1.

        Returns:
            List of Slides API request dicts.
        """
        style_fields = ["fontSize"]
        text_style = {"fontSize": {"magnitude": font_size_pt, "unit": "PT"}}
        if foreground_color is not None:
            style_fields.append("foregroundColor")
            text_style["foregroundColor"] = {
                "opaqueColor": {"rgbColor": foreground_color}
            }

        requests = [
            {
                "createShape": {
                    "objectId": object_id,
                    "shapeType": "TEXT_BOX",
                    "elementProperties": {
                        "pageObjectId": slide_id,
                        "size": {
                            "width": self._pt_to_emu(width_pt),
                            "height": self._pt_to_emu(height_pt),
                        },
                        "transform": {
                            "scaleX": 1,
                            "scaleY": 1,
                            "translateX": self._pt_to_emu(x_pt)["magnitude"],
                            "translateY": self._pt_to_emu(y_pt)["magnitude"],
                            "unit": "EMU",
                        },
                    },
                }
            },
            {
                "insertText": {
                    "objectId": object_id,
                    "text": text,
                    "insertionIndex": 0,
                }
            },
            {
                "updateTextStyle": {
                    "objectId": object_id,
                    "textRange": {"type": "ALL"},
                    "style": text_style,
                    "fields": ",".join(style_fields),
                }
            },
        ]
        if center_text:
            requests.append(
                {
                    "updateParagraphStyle": {
                        "objectId": object_id,
                        "textRange": {"type": "ALL"},
                        "style": {"alignment": "CENTER"},
                        "fields": "alignment",
                    }
                }
            )
        return requests

    def _presentation_url(self, presentation_id: str) -> str:
        """Return the edit URL for a presentation."""
        return f"https://docs.google.com/presentation/d/{presentation_id}/edit"
