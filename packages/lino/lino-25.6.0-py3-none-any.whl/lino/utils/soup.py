# -*- coding: UTF-8 -*-
# Copyright 2016-2025 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

# See https://dev.lino-framework.org/dev/bleach.html

import re
from bs4 import BeautifulSoup, NavigableString, Comment, Doctype
from bs4.element import Tag
import logging
logger = logging.getLogger(__file__)
# from lino.api import dd


PARAGRAPH_TAGS = {
    "p",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "h7",
    "h8",
    "h9",
    "pre",
    "li",
    "div",
}

WHITESPACE_TAGS = PARAGRAPH_TAGS | {
    "[document]",
    "ul",
    "html",
    "head",
    "body",
    "base",
}

SHORT_PREVIEW_IMAGE_HEIGHT = "8em"
REMOVED_IMAGE_PLACEHOLDER = "⌧"


class Style:
    # TODO: Extend rstgen.sphinxconf.sigal_image.Format to incoroporate this.
    def __init__(self, s):
        self._map = {}
        if s:
            for i in s.split(";"):
                k, v = i.split(":", maxsplit=1)
                self._map[k.strip()] = v.strip()
        self.is_dirty = False

    def __contains__(self, *args):
        return self._map.__contains__(*args)

    def __setitem__(self, k, v):
        if k in self._map and self._map[k] == v:
            return
        self._map[k] = v
        self.is_dirty = True

    def __delitem__(self, k):
        if k in self._map:
            self.is_dirty = True
        return self._map.__delitem__(k)

    def adjust_size(self):
        # if self['float'] == "none":
        #     return
        if "width" in self._map:
            del self["width"]
        self["height"] = SHORT_PREVIEW_IMAGE_HEIGHT

    def as_string(self):
        return ";".join(["{}:{}".format(*kv) for kv in self._map.items()])


# def truncate_soup(soup, max_length=None):
#     elems = []
#     found_image = False
#     remaining = max_length or settings.SITE.plugins.memo.short_preview_length
#     stop = False
#     for ch in soup:
#         if ch.name == "img":
#             if found_image:
#                 continue
#             style = Style(ch.get("style", None))
#             if not "float" in style:
#                 style["float"] = "right"
#             style.adjust_size()
#             if style.is_dirty:
#                 ch["style"] = style.as_string()
#             found_image = True
#             elems.append(ch)
#             continue
#
#         if ch.string is not None:
#             strlen = len(ch.string)
#             if strlen > remaining:
#                 stop = True
#                 end_text = ch.string[:remaining] + "..."
#                 ch.string.replace_with(end_text)
#             elems.append(ch)
#             remaining -= strlen
#     if isinstance(ch, Tag):
#         for c in ch.children:
#             if c.name in PARAGRAPH_TAGS:
#                 c.unwrap()
#
#         if stop:


class TextCollector:
    def __init__(self, max_length=None):
        self.text = ""
        self.sep = ""  # becomes " " after WHITESPACE_TAGS
        self.remaining = max_length or settings.SITE.plugins.memo.short_preview_length
        self.found_image = False

    def add_chunk(self, ch):
        # print(f"20250207 add_chunk {ch.__class__} {ch.name} {ch}")
        # if isinstance(ch, Tag):
        if ch.name in WHITESPACE_TAGS:
            # for c in ch.contents:
            # for c in ch:
            for c in ch.children:
                if not self.add_chunk(c):
                    return False
            # if ch.name in PARAGRAPH_TAGS:
            #     # self.sep = "\n\n"
            #     self.sep = "<br/>"
            # else:
            #     self.sep = " "
            self.sep = " "
            return True

        # assert ch.name != "IMG"
        we_want_more = True

        # Ignore all images except the first one. And for the first one we
        # enforce our style.
        if ch.name == "img":
            if self.found_image:
                # self.text += self.sep
                self.text += REMOVED_IMAGE_PLACEHOLDER
                return True
            self.found_image = True
            style = Style(ch.get("style", None))
            if not "float" in style:
                style["float"] = "right"
            style.adjust_size()
            if style.is_dirty:
                ch["style"] = style.as_string()
            # print("20231023 a", ch)

        elif ch.string is not None:
            text = ch.string
            strlen = len(text)
            # print(f"20250208b add_chunk {repr(ch)} len={strlen} remaining={self.remaining}")
            # chop = self.remaining
            if strlen > self.remaining:
                we_want_more = False
                # ch.string = ch.string[: self.remaining] + "..."
                end_text = text[:self.remaining] + "..."
                # raise Exception(f"20250208 {strlen} > {self.remaining} {end_text}")
                if isinstance(ch, NavigableString):
                    # ch = NavigableString(end_text)
                    ch = end_text
                else:
                    ch.string.replace_with(end_text)
                #     # ch = NavigableString(ch.string[:chop] + "...")
                #     # self.text += self.sep + ch.string
                #     self.text += self.sep + end_text
                #     return False
                # p = ch.string.parent
                # previous_sibling = ch.previous_sibling
                # ch = NavigableString(end_text)
                # ch = previous_sibling.next_sibling
                # raise Exception(f"20250208 Old {p} and new parent {ch.parent}")
                # if isinstance(ch, NavigableString):
                #     ch.replace_with(end_text)
                # else:
                #     ch.string.replace_with(end_text)
                # self.text += self.sep + str(ch)
                # for c in ch.children:
                #     self.add_chunk(c)
                # return False
                # raise Exception(f"20250208 {end_text} -- {ch}")
                # print(f"20250208c {repr(end_text)} in {ch}")
                # print("20230927", ch.string, ch)
                # self.text += str(ch.string) + "..."
                # self.remaining = 0
                # return True
                # return we_want_more
            self.remaining -= strlen
            # print(f"20250207c add_chunk {ch.__class__} {ch}")

        # if isinstance(ch, NavigableString):
        #     self.text += self.sep + ch.string
        # else:
        #     self.text += self.sep + str(ch)
        self.text += self.sep + str(ch)
        self.remaining -= len(self.sep)
        # self.remaining -= 1  # any separator counts as 1 char
        self.sep = ""
        return we_want_more


def truncate_comment(html_str, max_length=300):
    # Returns a single paragraph with a maximum number of visible chars.
    # new implementation since 20230713
    html_str = html_str.strip()  # remove leading or trailing newlines

    if False:  # no longer need to test for specil case
      if not html_str.startswith("<"):
        # print("20231023 c", html_str)
        if len(html_str) > max_length:
            return html_str[:max_length] + "..."
        return html_str

    # if "choose one or the other" in html_str:
    #     print(html_str)
    #     raise Exception("20230928 {} {}".format(len(html_str), max_length))

    # soup = BeautifulSoup(html_str, features="html.parser")
    soup = BeautifulSoup(html_str, features="lxml")
    # soup = sanitized_soup(html_str)
    # truncate_soup(soup, max_length)
    # return str(soup)
    # return "".join([str(s) for s in walk(soup, max_length)])
    tc = TextCollector(max_length)
    tc.add_chunk(soup)
    return tc.text


# remove these tags including their content.
blacklist = frozenset(["script", "style", "head"])

# unwrap these tags (remove the wrapper and leave the content)
unwrap = frozenset(["html", "body"])

useless_main_tags = frozenset(["p", "div", "span"])

ALLOWED_TAGS = frozenset([
    "a",
    "b",
    "i",
    "em",
    "ul",
    "ol",
    "li",
    "strong",
    "p",
    "br",
    "span",
    "pre",
    "def",
    "div",
    "img",
    "table",
    "th",
    "tr",
    "td",
    "thead",
    "tfoot",
    "tbody",
])

GENERALLY_ALLOWED_ATTRS = {"title", "style", "class"}

# Map of allowed attributes by tag. Originally copied from bleach.sanitizer.
ALLOWED_ATTRIBUTES = {
    "a": {"href"} | GENERALLY_ALLOWED_ATTRS,
    "img": {"src", "alt"} | GENERALLY_ALLOWED_ATTRS,
}

ALLOWED_ATTRIBUTES["span"] = GENERALLY_ALLOWED_ATTRS | {
    "data-index",
    "data-denotation-char",
    "data-link",
    "data-title",
    "data-value",
    "contenteditable",
}

ALLOWED_ATTRIBUTES["p"] = GENERALLY_ALLOWED_ATTRS | {"align"}

# def safe_css(attr, css):
#     if attr == "style":
#         return re.sub("(width|height):[^;]+;", "", css)
#     return css


def sanitized_soup(old):

    # Inspired by https://chase-seibert.github.io/blog/2011/01/28/sanitize-html-with-beautiful-soup.html

    try:
        soup = BeautifulSoup(old, features="lxml")
    except HTMLParseError as e:
        logger.warning("Could not sanitize %r : %s", old, e)
        return f"Could not sanitize content ({e})"

    for tag in soup.find_all():
        # print(tag)
        tag_name = tag.name.lower()
        if tag_name in blacklist:
            # blacklisted tags are removed in their entirety
            tag.extract()
        elif tag_name in unwrap:
            tag.unwrap()
        elif tag_name in ALLOWED_TAGS:
            # tag is allowed. Make sure all the attributes are allowed.
            allowed = ALLOWED_ATTRIBUTES.get(tag_name, GENERALLY_ALLOWED_ATTRS)
            tag.attrs = {k: v for k, v in tag.attrs.items() if k in allowed}
        else:
            # print(tag.name)
            # tag.decompose()
            # tag.extract()
            # not a whitelisted tag. I'd like to remove it from the tree
            # and replace it with its children. But that's hard. It's much
            # easier to just replace it with an empty span tag.
            tag.name = "span"
            tag.attrs = dict()

    # remove all comments because they might contain scripts
    comments = soup.find_all(
        text=lambda text: isinstance(text, (Comment, Doctype)))
    for comment in comments:
        comment.extract()

    # remove the wrapper tag if it is useless
    # if len(soup.contents) == 1:
    #     main_tag = soup.contents[0]
    #     if main_tag.name in useless_main_tags and not main_tag.attrs:
    #         main_tag.unwrap()

    return soup


def sanitize(s, **kwargs):
    s = s.strip()
    if not s:
        return s

    soup = sanitized_soup(s)

    for func in SANITIZERS:
        func(soup, **kwargs)

    # do we want to remove whitespace between tags?
    # s = re.sub(">\s+<", "><", s)
    # return sanitized_soup(s).decode(formatter="html").strip()
    return str(soup).strip()


SANITIZERS = []


def register_sanitizer(func):
    SANITIZERS.append(func)
