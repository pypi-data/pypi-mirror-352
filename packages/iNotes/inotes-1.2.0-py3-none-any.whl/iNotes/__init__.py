from .main import generate_notes
from .summarize import summarize
import warnings
import pkg_resources


def check_version():
    try:
        current_version = "1.2.0"  # Replace with the current version of your package
        installed_version = pkg_resources.get_distribution("iNotes").version
        if installed_version != current_version:
            warnings.warn(
                f"\n A newer version of iNotes had dropped.\n"
                f"💡 Update iNotes to the latest version.\n"
                f"   pip install --upgrade iNotes\n",
                category=UserWarning
            )
    except Exception as e:
        # Optional: silently pass if version check fails
        pass

check_version()