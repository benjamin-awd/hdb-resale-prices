from PIL import Image

from webapp.utils import get_project_root

icon = Image.open(get_project_root() / "webapp" / "logo" / "favicon.ico")
