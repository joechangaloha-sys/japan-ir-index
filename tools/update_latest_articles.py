"""Render both homepage story lists from the published feeds before deployment."""

from datetime import timezone, timedelta
from email.utils import parsedate_to_datetime
from html import escape
from html.parser import HTMLParser
from pathlib import Path
import re
import sys
from urllib.parse import urlsplit
from xml.etree import ElementTree


class ArchiveLinks(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_card = False
        self.links = set()

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "article":
            self.in_card = "cx-card" in attrs.get("class", "").split()
        if tag == "a" and self.in_card and "href" in attrs:
            self.links.add(urlsplit(attrs["href"]).path)

    def handle_endtag(self, tag):
        if tag == "article":
            self.in_card = False


def update_home(site, lang):
    insights = site / lang / "insights"
    items = ElementTree.parse(insights / "feed.xml").findall("./channel/item")
    dated = sorted(items, key=lambda item: parsedate_to_datetime(item.findtext("pubDate")), reverse=True)
    paths = [urlsplit(item.findtext("link")).path for item in dated]
    if not paths or len(paths) != len(set(paths)):
        raise ValueError(f"{lang}: empty feed or duplicate story links")
    archive = ArchiveLinks()
    archive.feed((insights / "index.html").read_text())
    stories = {f"/{lang}/insights/{p.parent.name}/" for p in insights.glob("*/index.html")}
    missing = (stories - set(paths)) | (stories - archive.links)
    if missing:
        raise ValueError(f"{lang}: stories missing from the archive or feed: {sorted(missing)}")

    rows = []
    for item, path in zip(dated[:4], paths[:4]):
        if not path.startswith(f"/{lang}/") or not (site / path.strip("/") / "index.html").is_file():
            raise ValueError(f"{lang}: invalid story link {path}")
        date = parsedate_to_datetime(item.findtext("pubDate")).astimezone(timezone(timedelta(hours=9))).date()
        rows.append(f'<li><a href="{escape(path, quote=True)}"><span class="date">{date}</span>'
                    f'<strong>{escape(item.findtext("title"))}</strong>'
                    f'<span class="muted">{escape(item.findtext("description"))}</span></a></li>')
    home = site / lang / "index.html"
    html, count = re.subn(r'(<ul class="rd-articles">).*?(</ul>)',
                          lambda match: match[1] + "".join(rows) + match[2], home.read_text(), flags=re.S)
    if count != 1:
        raise ValueError(f"{lang}: expected one homepage article list, found {count}")
    home.write_text(html)
    print(f"{lang}: {len(rows)} homepage stories, newest {paths[0]}")


if __name__ == "__main__":
    for language in ("ja", "en"):
        update_home(Path(sys.argv[1]), language)
