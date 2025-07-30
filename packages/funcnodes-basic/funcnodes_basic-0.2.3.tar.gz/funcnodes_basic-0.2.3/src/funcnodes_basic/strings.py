"""
basic functionalities for strings
"""

import funcnodes_core as fn
from typing import List, Tuple, Literal, Optional
import re


POSSIBLE_DECODINGS = [
    "ascii",
    "big5",
    "big5hkscs",
    "cp037",
    "cp273",
    "cp424",
    "cp437",
    "cp500",
    "cp720",
    "cp737",
    "cp775",
    "cp850",
    "cp852",
    "cp855",
    "cp856",
    "cp857",
    "cp858",
    "cp860",
    "cp861",
    "cp862",
    "cp863",
    "cp864",
    "cp865",
    "cp866",
    "cp869",
    "cp874",
    "cp875",
    "cp932",
    "cp949",
    "cp950",
    "cp1006",
    "cp1026",
    "cp1125",
    "cp1140",
    "cp1250",
    "cp1251",
    "cp1252",
    "cp1253",
    "cp1254",
    "cp1255",
    "cp1256",
    "cp1257",
    "cp1258",
    "euc_jp",
    "euc_jis_2004",
    "euc_jisx0213",
    "euc_kr",
    "gb2312",
    "gbk",
    "gb18030",
    "hz",
    "iso2022_jp",
    "iso2022_jp_1",
    "iso2022_jp_2",
    "iso2022_jp_2004",
    "iso2022_jp_3",
    "iso2022_jp_ext",
    "iso2022_kr",
    "latin_1",
    "iso8859_2",
    "iso8859_3",
    "iso8859_4",
    "iso8859_5",
    "iso8859_6",
    "iso8859_7",
    "iso8859_8",
    "iso8859_9",
    "iso8859_10",
    "iso8859_11",
    "iso8859_13",
    "iso8859_14",
    "iso8859_15",
    "iso8859_16",
    "johab",
    "koi8_r",
    "koi8_t",
    "koi8_u",
    "kz1048",
    "mac_cyrillic",
    "mac_greek",
    "mac_iceland",
    "mac_latin2",
    "mac_roman",
    "mac_turkish",
    "ptcp154",
    "shift_jis",
    "shift_jis_2004",
    "shift_jisx0213",
    "utf_32",
    "utf_32_be",
    "utf_32_le",
    "utf_16",
    "utf_16_be",
    "utf_16_le",
    "utf_7",
    "utf_8",
    "utf_8_sig",
]

POSSIBLE_DECODINGS_TYPE = Literal[*POSSIBLE_DECODINGS]


@fn.NodeDecorator(
    node_id="string.length",
    node_name="Length",
    description="Concatenate two strings",
    outputs=[
        {"name": "length"},
    ],
)
def string_length(s: str) -> int:
    return len(s)


@fn.NodeDecorator(
    node_id="string.concat",
    node_name="Concatenate",
    description="Concatenate two strings",
    outputs=[
        {"name": "concatenated"},
    ],
)
def string_concat(s1: str, s2: str) -> str:
    return s1 + s2


@fn.NodeDecorator(
    node_id="string.split",
    node_name="Split",
    description="Split a string by a delimiter",
    outputs=[
        {"name": "split"},
    ],
)
def string_split(s: str, delimiter: Optional[str] = None) -> List[str]:
    return s.split(delimiter)


@fn.NodeDecorator(
    node_id="string.join",
    node_name="Join",
    description="Join a list of strings by a delimiter",
    outputs=[
        {"name": "joined"},
    ],
)
def string_join(strings: List[str], delimiter: str = "") -> str:
    return delimiter.join(strings)


@fn.NodeDecorator(
    node_id="string.upper",
    node_name="Upper",
    description="Convert a string to uppercase",
    outputs=[
        {"name": "upper"},
    ],
)
def string_upper(s: str) -> str:
    return s.upper()


@fn.NodeDecorator(
    node_id="string.lower",
    node_name="Lower",
    description="Convert a string to lowercase",
    outputs=[
        {"name": "lower"},
    ],
)
def string_lower(s: str) -> str:
    return s.lower()


@fn.NodeDecorator(
    node_id="string.replace",
    node_name="Replace",
    description="Replace a substring with another",
    outputs=[
        {"name": "replaced"},
    ],
)
def string_replace(s: str, old: str, new: str) -> str:
    return s.replace(old, new)


@fn.NodeDecorator(
    node_id="string.strip",
    node_name="Strip",
    description="Remove leading and trailing whitespace or specified characters",
    outputs=[
        {"name": "stripped"},
    ],
)
def string_strip(s: str, chars: str = None) -> str:
    return s.strip(chars)


@fn.NodeDecorator(
    node_id="string.startswith",
    node_name="Starts With",
    description="Check if a string starts with a substring",
    outputs=[
        {"name": "starts_with"},
    ],
)
def string_startswith(s: str, prefix: str) -> bool:
    return s.startswith(prefix)


@fn.NodeDecorator(
    node_id="string.endswith",
    node_name="Ends With",
    description="Check if a string ends with a substring",
    outputs=[
        {"name": "ends_with"},
    ],
)
def string_endswith(s: str, suffix: str) -> bool:
    return s.endswith(suffix)


@fn.NodeDecorator(
    node_id="string.contains",
    node_name="Contains",
    description="Check if a string contains a substring",
    outputs=[
        {"name": "contains"},
    ],
)
def string_contains(s: str, sub: str) -> bool:
    return sub in s


@fn.NodeDecorator(
    node_id="string.format_map",
    node_name="Format Map",
    description="Format a string with a mapping",
    outputs=[
        {"name": "formatted"},
    ],
)
def string_format_map(s: str, mapping: dict) -> str:
    return s.format_map(mapping)


@fn.NodeDecorator(
    node_id="string.capitalize",
    node_name="Capitalize",
    description="Capitalize the first character of a string",
    outputs=[
        {"name": "capitalized"},
    ],
)
def string_capitalize(s: str) -> str:
    return s.capitalize()


@fn.NodeDecorator(
    node_id="string.title",
    node_name="Title",
    description="Capitalize the first character of each word in a string",
    outputs=[
        {"name": "titled"},
    ],
)
def string_title(s: str) -> str:
    return s.title()


@fn.NodeDecorator(
    node_id="string.swapcase",
    node_name="Swapcase",
    description="Swap the case of each character in a string",
    outputs=[
        {"name": "swapped"},
    ],
)
def string_swapcase(s: str) -> str:
    return s.swapcase()


@fn.NodeDecorator(
    node_id="string.zfill",
    node_name="Zfill",
    description="Fill a string with zeros to a specified width",
    outputs=[
        {"name": "zfilled"},
    ],
)
def string_zfill(s: str, width: int) -> str:
    return s.zfill(width)


@fn.NodeDecorator(
    node_id="string.center",
    node_name="Center",
    description="Center a string in a field of a specified width",
    outputs=[
        {"name": "centered"},
    ],
)
def string_center(s: str, width: int, fillchar: str = " ") -> str:
    return s.center(width, fillchar)


@fn.NodeDecorator(
    node_id="string.ljust",
    node_name="Left Justify",
    description="Left justify a string in a field of a specified width",
    outputs=[
        {"name": "left_justified"},
    ],
)
def string_ljust(s: str, width: int, fillchar: str = " ") -> str:
    return s.ljust(width, fillchar)


@fn.NodeDecorator(
    node_id="string.rjust",
    node_name="Right Justify",
    description="Right justify a string in a field of a specified width",
    outputs=[
        {"name": "right_justified"},
    ],
)
def string_rjust(s: str, width: int, fillchar: str = " ") -> str:
    return s.rjust(width, fillchar)


@fn.NodeDecorator(
    node_id="string.count",
    node_name="Count",
    description="Count the occurrences of a substring in a string",
    outputs=[
        {"name": "count"},
    ],
)
def string_count(s: str, sub: str) -> int:
    return s.count(sub)


@fn.NodeDecorator(
    node_id="string.find",
    node_name="Find",
    description="Find the index of the first occurrence of a substring in a string",
    outputs=[
        {"name": "index"},
    ],
)
def string_find(s: str, sub: str) -> int:
    return s.find(sub)


@fn.NodeDecorator(
    node_id="string.rfind",
    node_name="Rfind",
    description="Find the index of the last occurrence of a substring in a string",
    outputs=[
        {"name": "index"},
    ],
)
def string_rfind(s: str, sub: str) -> int:
    return s.rfind(sub)


@fn.NodeDecorator(
    node_id="string.index",
    node_name="Index",
    description="Find the index of the first occurrence of a substring in a string",
    outputs=[
        {"name": "index"},
    ],
)
def string_index(s: str, sub: str) -> int:
    return s.index(sub)


@fn.NodeDecorator(
    node_id="string.rindex",
    node_name="Rindex",
    description="Find the index of the last occurrence of a substring in a string",
    outputs=[
        {"name": "index"},
    ],
)
def string_rindex(s: str, sub: str) -> int:
    return s.rindex(sub)


@fn.NodeDecorator(
    node_id="string.isalnum",
    node_name="Is Alphanumeric",
    description="Check if a string is alphanumeric",
    outputs=[
        {"name": "is_alphanumeric"},
    ],
)
def string_isalnum(s: str) -> bool:
    return s.isalnum()


@fn.NodeDecorator(
    node_id="string.isalpha",
    node_name="Is Alphabetical",
    description="Check if a string is alphabetical",
    outputs=[
        {"name": "is_alphabetical"},
    ],
)
def string_isalpha(s: str) -> bool:
    return s.isalpha()


@fn.NodeDecorator(
    node_id="string.isdigit",
    node_name="Is Digit",
    description="Check if a string is a digit",
    outputs=[
        {"name": "is_digit"},
    ],
)
def string_isdigit(s: str) -> bool:
    return s.isdigit()


@fn.NodeDecorator(
    node_id="string.islower",
    node_name="Is Lowercase",
    description="Check if a string is lowercase",
    outputs=[
        {"name": "is_lowercase"},
    ],
)
def string_islower(s: str) -> bool:
    return s.islower()


@fn.NodeDecorator(
    node_id="string.isupper",
    node_name="Is Uppercase",
    description="Check if a string is uppercase",
    outputs=[
        {"name": "is_uppercase"},
    ],
)
def string_isupper(s: str) -> bool:
    return s.isupper()


@fn.NodeDecorator(
    node_id="string.isspace",
    node_name="Is Space",
    description="Check if a string is whitespace",
    outputs=[
        {"name": "is_space"},
    ],
)
def string_isspace(s: str) -> bool:
    return s.isspace()


@fn.NodeDecorator(
    node_id="string.istitle",
    node_name="Is Title",
    description="Check if a string is titlecase",
    outputs=[
        {"name": "is_title"},
    ],
)
def string_istitle(s: str) -> bool:
    return s.istitle()


@fn.NodeDecorator(
    node_id="string.isprintable",
    node_name="Is Printable",
    description="Check if a string is printable",
    outputs=[
        {"name": "is_printable"},
    ],
)
def string_isprintable(s: str) -> bool:
    return s.isprintable()


@fn.NodeDecorator(
    node_id="string.isidentifier",
    node_name="Is Identifier",
    description="Check if a string is a valid identifier",
    outputs=[
        {"name": "is_identifier"},
    ],
)
def string_isidentifier(s: str) -> bool:
    return s.isidentifier()


@fn.NodeDecorator(
    node_id="string.isdecimal",
    node_name="Is Decimal",
    description="Check if a string is a decimal",
    outputs=[
        {"name": "is_decimal"},
    ],
)
def string_isdecimal(s: str) -> bool:
    return s.isdecimal()


@fn.NodeDecorator(
    node_id="string.isnumeric",
    node_name="Is Numeric",
    description="Check if a string is numeric",
    outputs=[
        {"name": "is_numeric"},
    ],
)
def string_isnumeric(s: str) -> bool:
    return s.isnumeric()


@fn.NodeDecorator(
    node_id="string.isascii",
    node_name="Is ASCII",
    description="Check if a string is ASCII",
    outputs=[
        {"name": "is_ascii"},
    ],
)
def string_isascii(s: str) -> bool:
    return s.isascii()


@fn.NodeDecorator(
    node_id="string.encode",
    node_name="Encode",
    description="Encode a string",
    outputs=[
        {"name": "encoded"},
    ],
)
def string_encode(
    s: str,
    encoding: POSSIBLE_DECODINGS_TYPE = "utf-8",
    errors: Literal[
        "strict",
        "replace",
        "ignore",
        "xmlcharrefreplace",
        "backslashreplace",
        "namereplace",
    ] = "replace",
) -> bytes:
    return s.encode(encoding, errors)


@fn.NodeDecorator(
    node_id="string.decode",
    node_name="Decode",
    description="Decode a string",
    outputs=[
        {"name": "decoded"},
    ],
)
def string_decode(
    b: bytes,
    encoding: POSSIBLE_DECODINGS_TYPE = "utf_8",
    errors: Literal[
        "strict",
        "replace",
        "ignore",
        "xmlcharrefreplace",
        "backslashreplace",
        "namereplace",
    ] = "replace",
) -> str:
    return b.decode(encoding, errors)


@fn.NodeDecorator(
    node_id="re.match",
    node_name="Match",
    description="Match a string against a regular expression",
    outputs=[
        {"name": "match"},
        {"name": "groups"},
    ],
)
def re_match(pattern: str, string: str) -> Tuple[bool, List[str]]:
    matches = re.match(pattern, string)
    if not matches:
        return False, []

    groups = [matches[0]] + list(matches.groups())
    return True, groups


@fn.NodeDecorator(
    node_id="re.fullmatch",
    node_name="Full Match",
    description="Match a string against a regular expression",
    outputs=[
        {"name": "match"},
        {"name": "groups"},
    ],
)
def re_fullmatch(pattern: str, string: str) -> Tuple[bool, List[str]]:
    matches = re.fullmatch(pattern, string)
    if not matches:
        return False, []

    groups = [matches[0]] + list(matches.groups())
    return True, groups


@fn.NodeDecorator(
    node_id="re.search",
    node_name="Search",
    description="Search a string for a regular expression",
    outputs=[
        {"name": "match"},
        {"name": "groups"},
    ],
)
def re_search(pattern: str, string: str) -> Tuple[bool, List[str]]:
    matches = re.search(pattern, string)
    if not matches:
        return False, []

    groups = [matches[0]] + list(matches.groups())
    return True, groups


@fn.NodeDecorator(
    node_id="re.findall",
    node_name="Find All",
    description="Find all occurrences of a regular expression in a string",
    outputs=[
        {"name": "matches"},
    ],
)
def re_findall(pattern: str, string: str) -> List[List[str]]:
    return re.findall(pattern, string)


@fn.NodeDecorator(
    node_id="re.sub",
    node_name="Substitute",
    description="Substitute occurrences of a regular expression in a string",
    outputs=[
        {"name": "substituted"},
    ],
)
def re_sub(pattern: str, repl: str, string: str) -> str:
    return re.sub(pattern, repl, string)


@fn.NodeDecorator(
    node_id="re.subn",
    node_name="Substitute N",
    description="Substitute occurrences of a regular expression in a string",
    outputs=[
        {"name": "substituted"},
        {"name": "count"},
    ],
)
def re_subn(pattern: str, repl: str, string: str) -> Tuple[str, int]:
    return re.subn(pattern, repl, string)


@fn.NodeDecorator(
    node_id="re.escape",
    node_name="Escape",
    description="Escape special characters in a regular expression",
    outputs=[
        {"name": "escaped"},
    ],
)
def re_escape(pattern: str) -> str:
    return re.escape(pattern)


@fn.NodeDecorator(
    node_id="re.split",
    node_name="Split",
    description="Split a string by a regular expression",
    outputs=[
        {"name": "splitted"},
    ],
)
def re_split(pattern: str, string: str) -> List[str]:
    return re.split(pattern, string)


regex_shelf = fn.Shelf(
    nodes=[
        re_match,
        re_fullmatch,
        re_search,
        re_findall,
        re_sub,
        re_subn,
        re_escape,
        re_split,
    ],
    subshelves=[],
    name="Regular Expressions",
    description="Basic regular expression operations.",
)


@fn.NodeDecorator(
    node_id="string.input",
    node_name="Input",
    description="Input a string",
    outputs=[
        {"name": "string"},
    ],
)
def string_input(s: str) -> str:
    return s


NODE_SHELF = fn.Shelf(
    nodes=[
        string_length,
        string_concat,
        string_split,
        string_join,
        string_encode,
        string_decode,
        string_upper,
        string_lower,
        string_replace,
        string_strip,
        string_startswith,
        string_endswith,
        string_contains,
        string_format_map,
        string_capitalize,
        string_title,
        string_swapcase,
        string_zfill,
        string_center,
        string_ljust,
        string_rjust,
        string_count,
        string_find,
        string_rfind,
        string_index,
        string_rindex,
        string_isalnum,
        string_isalpha,
        string_isdigit,
        string_islower,
        string_isupper,
        string_isspace,
        string_istitle,
        string_isprintable,
        string_isidentifier,
        string_isdecimal,
        string_isnumeric,
        string_isascii,
        string_input,
    ],
    subshelves=[regex_shelf],
    name="Strings",
    description="Basic string manipulation and regular expressions.",
)
