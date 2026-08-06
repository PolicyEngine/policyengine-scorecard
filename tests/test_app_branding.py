from html.parser import HTMLParser
from pathlib import Path
from xml.etree import ElementTree


ROOT = Path(__file__).resolve().parents[1]
APP_DIR = ROOT / "app"


class LinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        if tag == "link":
            self.links.append(dict(attrs))


def test_scorecard_favicon_uses_policyengine_mark():
    parser = LinkParser()
    parser.feed((APP_DIR / "index.html").read_text())
    favicon_links = [
        link for link in parser.links if "icon" in link.get("rel", "").split()
    ]

    assert favicon_links == [
        {
            "rel": "icon",
            "type": "image/svg+xml",
            "href": "./favicon.svg",
        }
    ]

    favicon = APP_DIR / "public" / "favicon.svg"
    svg = ElementTree.parse(favicon).getroot()
    fills = {
        element.attrib["fill"].upper()
        for element in svg.iter()
        if "fill" in element.attrib
    }

    assert svg.attrib["viewBox"] == "0 0 244 244"
    assert "#2C7A7B" in fills
