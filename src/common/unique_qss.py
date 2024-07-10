LATEST_ID = 0


def get_id():
    global LATEST_ID
    LATEST_ID += 1
    return f"id{LATEST_ID}"


def set_stylesheet(element, style: str):
    unique_id = get_id()
    element.setObjectName(unique_id)
    element.setStyleSheet(style.replace("#id", "#" + unique_id))
