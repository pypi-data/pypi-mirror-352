from .core import load_and_describe, missing_report, info_summary
from .plotting import quick_plot, plot_advanced

__version__ = "0.2.3"

# Debug information
import sys
print(f"Loaded dashcamcsv version {__version__} from {__file__}")
print(f"Using Python {sys.version}")
