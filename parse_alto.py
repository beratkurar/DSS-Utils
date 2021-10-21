# -*- coding: utf-8 -*-
from collections import namedtuple

from lxml import etree

AltoElement = namedtuple(
    "AltoElement", ["type", "bbox", "element", "children", "content"]
)


class BoundingBox(object):
    def __init__(self, xml_element):
        self.x0 = int(float(xml_element.get("HPOS")))
        self.y0 = int(float(xml_element.get("VPOS")))
        self.width = int(float(xml_element.get("WIDTH")))
        self.height = int(float(xml_element.get("HEIGHT")))

    def expand(self, pixels):
        return BoundingBox(
            {
                "HPOS": str(self.x0 - pixels),
                "VPOS": str(self.y0 - pixels),
                "WIDTH": str(self.width + pixels * 2),
                "HEIGHT": str(self.height + pixels * 2),
            }
        )

    def serialize(self):
        return [self.x0, self.y0, self.x0 + self.width, self.y0 + self.height]

    def center_top(self):
        return (self.x0 + (self.width / 2), self.y0 + 10)

    def serialize_polygon(self):
        return [
            [self.x0, self.y0],
            [self.x0 + self.width, self.y0],
            [self.x0 + self.width, self.y0 + self.height],
            [self.x0, self.y0 + self.height],
            [self.x0, self.y0],
        ]


def parse_alto(alto_file):
    alto_elements = []
    xml_tree = etree.parse(alto_file)
    root = xml_tree.getroot()

    # Remove namespace prefixes
    for elem in root.getiterator():
        elem.tag = etree.QName(elem).localname

    for line in root.findall("Layout/Page/PrintSpace/TextBlock/TextLine"):
        line_element = AltoElement(
            type="line",
            bbox=BoundingBox(line),
            element=line,
            children=[],
            content=line.get("CONTENT"),
        )
        alto_elements.append(line_element)

        for word in line.findall("String"):
            word_element = AltoElement(
                type="word",
                bbox=BoundingBox(word),
                element=word,
                children=[],
                content=word.get("CONTENT"),
            )
            line_element.children.append(word_element)

            for char in word.findall("Glyph"):
                char_element = AltoElement(
                    type="char",
                    bbox=BoundingBox(char),
                    element=char,
                    children=[],
                    content=char.get("CONTENT"),
                )
                word_element.children.append(char_element)

    return alto_elements
