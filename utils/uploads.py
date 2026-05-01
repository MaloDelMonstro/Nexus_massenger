import os
import uuid

from flask import current_app
from werkzeug.datastructures import FileStorage


def _get_allowed_extensions() -> set[str]:
    return current_app.config.get("ALLOWED_EXTENSIONS", {"png", "jpg", "jpeg", "gif", "webp"})


def allowed_file(filename: str) -> bool:
    allowed = _get_allowed_extensions()
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed


def save_uploaded_image(file: FileStorage) -> tuple[str | None, str | None]:
    if not file or not file.filename:
        return None, "Файл не выбран"

    if not allowed_file(file.filename):
        allowed = _get_allowed_extensions()
        return None, f"Разрешены только: {', '.join(sorted(allowed))}"

    ext = file.filename.rsplit(".", 1)[1].lower()
    safe_name = f"{uuid.uuid4().hex}.{ext}"

    upload_folder = current_app.config.get("UPLOAD_FOLDER")
    if not upload_folder:
        return None, "UPLOAD_FOLDER не настроен"

    os.makedirs(upload_folder, exist_ok=True)
    filepath = os.path.join(upload_folder, safe_name)

    try:
        file.save(filepath)
        return f"/static/uploads/images/{safe_name}", None
    except OSError as exc:
        return None, f"Ошибка сохранения: {exc}"


def validate_image_url(url: str) -> tuple[str | None, str | None]:
    if not url or not url.strip():
        return None, "URL пуст"

    url = url.strip()
    if not url.startswith(("http://", "https://")):
        return None, "URL должен начинаться с http:// или https://"

    return url, None
