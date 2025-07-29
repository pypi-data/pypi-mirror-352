import typing
from collections import defaultdict


def _graph_to_hierarchical_list(parents_node: typing.List, graph: typing.Dict, node_info: typing.Dict):

    def find_children(children_ids):
        level_pages = []
        for children_id in children_ids:
            if children_id not in node_info:
                # not a real page, add its children to this level
                level_pages.extend(graph[children_id])
            else:
                level_pages.append(children_id)

        sub_pages = []
        for children_id in level_pages:
            sub_pages.append({
                **node_info[children_id],
                "items": find_children(graph[children_id])
            })
        return sub_pages

    result = find_children(parents_node)
    result.sort(key=lambda x: x["title"])
    return result


def structure_pages(pages: typing.List):
    """
    Restructure pages got from notion search API
    Input format: [
        "id": uuid,
        "object": "database" or "page"
        "parent": {
            "type": "workspace" or "page_id" or "database_id",
            [type]: uuid
        }
        "properties": {
            "Title": {
                "title": [
                    "plain_text"
                ]
            }
        }
    ]
    Output format: {
        {
            "id": uuid,
            "title": str,
            "items": {
                "id": {
                    "id": uuid,
                    "title": str,
                    "items: {}
                }
            }
        },
        {}
    }
    """
    parents = []  # list of page_id at first layer of page
    parent_pages = defaultdict(list)  # dict of parent_id: [children_id]
    page_info = {}  # store info (id, title) of all pages
    for page in pages:
        page_id = page["id"]
        # Get page title
        try:
            if page["object"] == "database":
                page_title = page["title"][0]["plain_text"]
            elif page["object"] == "page":
                properties = page["properties"]
                title = properties.get("title") or properties.get("Title") or properties.get("Page")
                page_title = title["title"][0]["plain_text"]
        except:
            page_title = ""
        # Add page to page_info
        page_info[page_id] = {
            "id": page_id,
            "title": page_title
        }
        # Add page to parent_pages
        parent = page["parent"]
        if parent["type"] != "workspace":
            parent_id = parent[parent["type"]]
            parent_pages[parent_id].append(page_id)
    parents += [p_id for p_id in parent_pages.keys() if p_id not in page_info]
    return _graph_to_hierarchical_list(parents, parent_pages, page_info)

def get_page_section(pages: typing.Dict):
    """
    From page's content blocks, get block title and id
    Input format: {
        "block_id": {
            "value": {
                "type": 
            }
            "properties": {
                "title": [
                    [str]
                ]
            }
        }
    }
    Output format:
    [
        {
            "block_id": uuid (without '-')
            "block_title": str
        }
    ]
    """
    headers = []
    for block_id, block in pages.items():
        value = block["value"]
        type = value["type"]
        if "header" in type:
            header_text = value["properties"]["title"][0]
            header_text = [text for text in header_text if isinstance(text, str)]
            headers.append({
                "block_id": block_id.replace("-", ""),
                "block_title": " ".join(header_text)
            })
    return headers