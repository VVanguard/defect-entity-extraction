from difflib import SequenceMatcher


def get_method_type(action):
    # Update
    if SequenceMatcher(None, "update", action).ratio() > 0.5:
        return "Update"

    if SequenceMatcher(None, "patch", action).ratio() > 0.5:
        return "Update"

    if SequenceMatcher(None, "change", action).ratio() > 0.5:
        return "Update"

    # Create
    if SequenceMatcher(None, "create", action).ratio() > 0.5:
        return "Create"

    if SequenceMatcher(None, "add", action).ratio() > 0.5:
        return "Create"

    # Delete
    if SequenceMatcher(None, "remove", action).ratio() > 0.5:
        return "Delete"

    if SequenceMatcher(None, "delete", action).ratio() > 0.5:
        return "Delete"


def get_search_name(name):

    search_name = name

    if "Update" in name:
        search_name = name.replace("Update", "") + "Update"

    if "Create" in name:
        search_name = name.replace("Create", "") + "Create"

    if "Delete" in name:
        search_name = name.replace("Delete", "") + "Delete"

    return search_name