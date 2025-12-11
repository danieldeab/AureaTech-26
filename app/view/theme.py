"""
AureaTech global theme

Single source of truth for:
- Brand palette (primary, secondary, accent colors)
- Semantic color aliases (backgrounds, text, cards, inputs, borders)
- Layout constants (panels, paddings)

IMPORTANT:
- Legacy names are preserved for backwards compatibility.
- New code should prefer the SEMANTIC names where possible.
"""

# ============================================================
# 1) BRAND PALETTE (from Imagen de Empresa)
#    Reference:
#      #2F4F46 – primary green
#      #FAF9F6 – off-white background
#      #D8D8D8 – light grey
#      #3C5199 – accent blue
#      #3D3D3D – dark grey
# ============================================================

# Core brand colors
BRAND_PRIMARY_GREEN = "#2F4F46"   # main AureaTech green
BRAND_BACKGROUND    = "#FAF9F6"   # off-white used as app background
BRAND_LIGHT_GREY    = "#D8D8D8"   # neutral light for borders / inputs
BRAND_ACCENT_BLUE   = "#3C5199"   # highlight / links
BRAND_DARK_GREY     = "#3D3D3D"   # primary text on light background

# ============================================================
# 2) SEMANTIC COLORS (use these in new views/components)
# ============================================================

# Surfaces / backgrounds
BG_APP             = BRAND_BACKGROUND      # main background (outside cards)
BG_CARD_PRIMARY    = BRAND_BACKGROUND      # default card background
BG_CARD_ELEVATED   = "#FFFFFF"             # slightly brighter card if needed
BG_INPUT           = BRAND_LIGHT_GREY      # text fields, dropdowns
BG_NAVBAR          = BRAND_PRIMARY_GREEN   # top/bottom bars on dark green
BG_HEADER          = BRAND_PRIMARY_GREEN   # header bar for dashboards
BG_FOOTER          = BRAND_PRIMARY_GREEN   # footer or bottom nav background

# Text
TEXT_PRIMARY       = BRAND_DARK_GREY       # main text color
TEXT_SECONDARY     = "#343232"       # muted labels, helper text
TEXT_ON_PRIMARY    = BRAND_DARK_GREY           # text on green/navy
TEXT_ON_ACCENT     = BRAND_DARK_GREY           # text on accent blue
TEXT_LINK          = BRAND_ACCENT_BLUE     # links, clickable labels

# Borders / outlines
BORDER_STRONG      = BRAND_DARK_GREY       # strong separators
BORDER_SUBTLE      = f"{BRAND_DARK_GREY}33"  # same but with alpha (~20%)
BORDER_INPUT       = "transparent"         # we default to no visible border
BORDER_FOCUS       = BRAND_ACCENT_BLUE     # focus or active field outline

# Buttons
BTN_PRIMARY_BG     = BRAND_PRIMARY_GREEN
BTN_PRIMARY_FG     = TEXT_ON_PRIMARY
BTN_SECONDARY_BG   = BRAND_BACKGROUND
BTN_SECONDARY_FG   = BRAND_PRIMARY_GREEN
BTN_DANGER_BG      = "#B00020"             # same as ERROR_RED
BTN_DANGER_FG      = "#FFFFFF"

# Cards / panels (sugar aliases)
CARD_AUTH_BG       = BG_CARD_PRIMARY
CARD_DASHBOARD_BG  = BG_CARD_PRIMARY
CARD_LIST_BG       = BG_CARD_PRIMARY

# Inputs / chips / pills
INPUT_BG           = BG_INPUT
INPUT_PLACEHOLDER  = BRAND_ACCENT_BLUE
INPUT_TEXT         = BRAND_DARK_GREY
CHIP_BG_DEFAULT    = BRAND_LIGHT_GREY
CHIP_BG_SELECTED   = BRAND_ACCENT_BLUE
CHIP_TEXT_DEFAULT  = TEXT_PRIMARY
CHIP_TEXT_SELECTED = TEXT_ON_ACCENT

# ============================================================
# 3) ALERT COLORS (status + semantic meaning)
# ============================================================

ERROR_RED      = "#B00020"
WARNING_YELLOW = "#FFEB99"
INFO_BLUE      = "#CFE2FF"
SUCCESS_GREEN  = "#2E7D32"
LIGHT_GREEN   = "#D0F0C0"

# Alternates for foreground text on alert backgrounds
ALERT_TEXT_DARK  = "#1E1E1E"
ALERT_TEXT_LIGHT = "#FFFFFF"

# ============================================================
# 4) LAYOUT CONSTANTS
#    These match the auth/dashboard card sizes used in the UI
# ============================================================

# Main auth/dashboard panel size (center card)
PANEL_W = 980
PANEL_H = 640

# Global paddings (for consistent spacing)
PADDING_XSM = 6
PADDING_SM  = 10
PADDING_MD  = 14
PADDING_LG  = 20
PADDING_XL  = 28

# Optional: breakpoints if you later want responsive tweaks
BP_SMALL_MAX_WIDTH  = 800
BP_MEDIUM_MAX_WIDTH = 1200
# BP_LARGE – anything above BP_MEDIUM_MAX_WIDTH

# ============================================================
# 5) LEGACY NAMES (BACKWARDS COMPATIBILITY)
#    Keep these so existing code keeps working.
#    New code should prefer SEMANTIC names above.
# ============================================================

# Old color aliases used in existing views
PRIMARY_GREEN = BRAND_PRIMARY_GREEN
BACK_BLUE     = BRAND_ACCENT_BLUE
LIGHT_GREY    = BRAND_LIGHT_GREY
WHITE         = BRAND_BACKGROUND
FULL_BLACK    = BRAND_DARK_GREY
BORDER_SOFT   = BORDER_SUBTLE
DARK_BG       = BRAND_PRIMARY_GREEN  # used as dark background in some views