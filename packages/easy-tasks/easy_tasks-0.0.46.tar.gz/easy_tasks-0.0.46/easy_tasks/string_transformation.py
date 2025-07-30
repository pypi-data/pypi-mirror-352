def upper_case_first_letter_of_word(String: str, lower_case_words: list = []):
    """Get a string with your string transformed to have the firts letter in upper case.

    Args:
        String (str): Your string to transform. (not in place)
        lower_case_words (list, optional): List of words which should allways be in lower case. Defaults to [].

    Returns:
        string: AThe transformed string.
    """
    wörter = String.split(" ")
    _ws = []
    for w in wörter:
        dw = ""
        for iw, cw in enumerate(w):
            if iw == 0:
                dw += cw.upper()
            else:
                dw += cw
        if w.lower() in [w.lower() for w in lower_case_words]:
            dw = w.lower()
        _ws.append(dw)
    dn = " ".join(_ws)
    return dn


def upper_case_first_letter_of_words(List: list[str], lower_case_words: list = []):
    """Get a list with the strings transformed to have the firts letter in upper case in your list.

    Args:
        Liste (list[str]): Your list of strings to transform. (not in place)
        lower_case_words (list, optional): List of words which should allways be in lower case. Defaults to [].

    Returns:
        list: A list containing the transformed strings.
    """
    result = []
    for n in List:
        dn = upper_case_first_letter_of_word(n, lower_case_words)
        result.append(dn)
    return result


def insert_into_string(
    content, markers, insert, after=True, align_to_line=False, pos_shift=0
):
    """
    Insert a string into content at a position relative to a series of marker substrings.

    Args:
        content (str): The original string content to modify.
        markers (list[str]): A list of marker substrings to locate in order.
        insert (str): The string to insert.
        after (bool, optional): If True, insert after the final marker; if False, insert before. Defaults to True.
        align_to_line (bool, optional): If True, align the insertion to the start or end of the nearest line. Defaults to False.
        pos_shift (int, optional): Additional offset (positive or negative) to adjust insertion position. Defaults to 0.

    Returns:
        content (str | bool): The modified content if successful, or False if any marker is not found.
    """
    interest = content
    pos = 0
    for marker in markers:
        if marker in interest:
            p = interest.find(marker)
            interest = interest[p:]
            pos += p
            print(pos)
        else:
            colored_print(Fore.RED + "False")
            return False
    if after:
        if align_to_line:
            if "\n" in interest:
                end_of_line = pos + interest.find("\n") + pos_shift
                content = content[:end_of_line] + insert + content[end_of_line:]
            else:
                content += insert
        else:
            p = pos + len(marker) + pos_shift
            content = content[:p] + insert + content[p:]
    else:
        if align_to_line:
            interest = content[:pos]
            if "\n" in interest:
                end_of_line = interest.rfind("\n") + 1 + pos_shift
                content = content[:end_of_line] + insert + content[end_of_line:]
        else:
            p = pos + pos_shift
            content = content[:p] + insert + content[p:]

    return content


def insert_into_file(
    filepath, markers, insert, after=True, align_to_line=False, pos_shift=0
):
    """
    Insert a string into a file at a position relative to a series of marker substrings.

    Args:
        filepath (str): The path to the file to modify.
        markers (list[str]): A list of marker substrings to locate in order within the file content.
        insert (str): The string to insert.
        after (bool, optional): If True, insert after the final marker; if False, insert before. Defaults to True.
        align_to_line (bool, optional): If True, align the insertion to the start or end of the nearest line. Defaults to False.
        pos_shift (int, optional): Additional offset (positive or negative) to adjust insertion position. Defaults to 0.

    Returns:
        content (str | bool): The modified file content if successful, or False if any marker is not found.
    """
    with open(filepath, "r") as f:
        content = f.read()

    content = insert_into_string(
        content, markers, insert, after, align_to_line, pos_shift
    )

    if content:
        with open(filepath, "w") as f:
            f.write(content)

    return content
