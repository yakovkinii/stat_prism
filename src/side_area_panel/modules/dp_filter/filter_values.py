from src.data.data import category_display_value

# Legacy value used by older saved categorical filters for missing / blank cells. New configs store
# the same visible label used in the UI (mdash), but all readers still accept this sentinel.
EMPTY_SENTINEL = "__EMPTY__"


def saved_filter_value_label(value) -> str:
    return category_display_value(None) if value == EMPTY_SENTINEL else category_display_value(value)
