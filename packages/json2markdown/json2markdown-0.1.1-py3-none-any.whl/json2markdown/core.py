import re
import json


# --- Generic Table Helpers (assuming these are correct from before) ---
def _escape_markdown_cell(cell_value) -> str:
    if cell_value is None:
        return ""
    s = str(cell_value)
    return s.replace("|", "\\|").replace("\n", "<br>")


def _generic_list_of_dicts_to_table(lst: list[dict]) -> str:
    if not lst or not all(isinstance(item, dict) for item in lst):
        return ""
    headers = []
    for item_dict in lst:  # Iterate through dicts in the list
        if isinstance(item_dict, dict):  # Ensure item is a dict
            for k in item_dict.keys():
                if k not in headers:
                    headers.append(k)
    if not headers:
        return ""

    table = ["| " + " | ".join(map(_escape_markdown_cell, headers)) + " |"]
    table.append("| " + " | ".join(["---"] * len(headers)) + " |")
    for item_dict in lst:  # Iterate through dicts in the list
        if isinstance(item_dict, dict):  # Ensure item is a dict
            row_values = []
            for h in headers:
                value = item_dict.get(h)
                if isinstance(value, (list, dict)):
                    cell_text_raw = json.dumps(value, separators=(",", ":"))
                else:
                    cell_text_raw = value
                row_values.append(_escape_markdown_cell(cell_text_raw))
            table.append("| " + " | ".join(row_values) + " |")
    return "\n".join(table) + "\n"


def _is_list_flat_enough_for_table(
    lst: list[dict], ratio_threshold: float
) -> bool:
    if not lst:
        return False
    complex_cells, total_cells = 0, 0
    sample = lst[: min(len(lst), 5)]
    if not sample:
        return False
    for item_dict in sample:  # Iterate through dicts
        if not isinstance(item_dict, dict) or not item_dict:
            continue
        for v in item_dict.values():
            total_cells += 1
            if isinstance(v, (list, dict)):
                complex_cells += 1
    if total_cells == 0:
        return False
    return (complex_cells / total_cells) < ratio_threshold


def _is_a_list_of_dictionaries_structure(el) -> bool:
    if not isinstance(el, list) or not el:
        return False
    if not all(isinstance(item, dict) for item in el):
        return False
    return any(d for d in el if isinstance(d, dict) and d)


def _has_nested_list_of_dicts_in_cells(lst: list[dict]) -> bool:
    if not lst:
        return False
    sample = lst[: min(len(lst), 5)]
    for item_dict in sample:  # Iterate through dicts
        if isinstance(item_dict, dict):
            for cell_val in item_dict.values():
                if _is_a_list_of_dictionaries_structure(cell_val):
                    return True
    return False


def make_bullet_point(text, escape=False) -> str:
    s_text = str(text)
    if escape:
        s_text = _escape_markdown_cell(s_text)
    spaces = " " * (len(s_text) - len(s_text.lstrip()))
    content = s_text.lstrip()
    if re.match(
        r"^\s*([-*+]|\d+\.|\b[a-zA-Z\.|\b[IVXLCDMivxlcdm]+\.)\s+",
        content,
        re.I,
    ):
        return f"{spaces}{content}"  # Return as is if already a list item
    return f"{spaces}- {content}"


# --- Main Conversion Logic ---
def convert_json_to_markdown_document(
    json_data,
    depth=1,
    current_item_number_for_section=1,  # Number for the current section/dict if it's an item from a list
    parent_numbering_prefix="",
    max_cell_complexity_ratio_for_generic_tables=0.4,
):
    markdown_parts = []

    if isinstance(json_data, dict):
        # Standard dictionary processing (no special section-defining key found at this dict's top level)
        key_order_in_dict = 0
        for key, value in json_data.items():
            key_order_in_dict += 1

            effective_depth = depth
            display_number_for_key = ""

            if not parent_numbering_prefix:  # Root dictionary keys
                display_number_for_key = f"{key_order_in_dict}."
            else:
                # This dict is nested. parent_numbering_prefix is its "address".
                # Keys within this nested dict are sub-numbered.
                display_number_for_key = (
                    f"{parent_numbering_prefix}{key_order_in_dict}."
                )

            markdown_parts.append(
                f"{'#' * effective_depth} {display_number_for_key} **{key}**\n"
            )

            if isinstance(value, dict):
                markdown_parts.append(
                    convert_json_to_markdown_document(
                        value,
                        depth + 1,
                        current_item_number_for_section=1,
                        parent_numbering_prefix=display_number_for_key,
                        max_cell_complexity_ratio_for_generic_tables=max_cell_complexity_ratio_for_generic_tables,
                    )
                )
            elif isinstance(value, list):
                if (
                    _is_a_list_of_dictionaries_structure(value)
                    and not _has_nested_list_of_dicts_in_cells(value)
                    and _is_list_flat_enough_for_table(
                        value, max_cell_complexity_ratio_for_generic_tables
                    )
                ):
                    markdown_parts.append(
                        _generic_list_of_dicts_to_table(value)
                    )
                else:
                    for i_list_item, item_in_list in enumerate(value):
                        if isinstance(item_in_list, dict):
                            # When a dict is an item in a list, its "section number" is i_list_item + 1
                            # Its parent_numbering_prefix is the number of the list's key (display_number_for_key)
                            markdown_parts.append(
                                convert_json_to_markdown_document(
                                    item_in_list,
                                    depth,  # For items like UserStory/APIInfo dicts, their main heading is at current key's depth
                                    current_item_number_for_section=i_list_item
                                    + 1,
                                    parent_numbering_prefix=display_number_for_key,
                                    max_cell_complexity_ratio_for_generic_tables=max_cell_complexity_ratio_for_generic_tables,
                                )
                            )
                        else:
                            markdown_parts.append(
                                make_bullet_point(item_in_list, escape=True)
                                + "\n"
                            )
            else:  # Scalar
                markdown_parts.append(f"{_escape_markdown_cell(value)}\n")

    elif isinstance(json_data, list):
        for i_list_item, item_in_list in enumerate(json_data):
            # Each item_in_list (e.g., a User Story dict) gets its number from i_list_item + 1
            markdown_parts.append(
                convert_json_to_markdown_document(
                    item_in_list,
                    depth,  # The depth for the section defined by this list item
                    current_item_number_for_section=i_list_item + 1,
                    parent_numbering_prefix=parent_numbering_prefix,
                    max_cell_complexity_ratio_for_generic_tables=max_cell_complexity_ratio_for_generic_tables,
                )
            )

    return "\n".join(filter(None, markdown_parts))
