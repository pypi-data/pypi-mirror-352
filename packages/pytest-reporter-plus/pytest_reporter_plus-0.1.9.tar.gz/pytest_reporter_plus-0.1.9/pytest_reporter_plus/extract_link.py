def extract_links_from_item(item):
    links = []
    for marker in item.iter_markers(name="link"):
        if marker.args:
            links.extend(str(arg) for arg in marker.args)
    return links