import gettext
from bs4 import BeautifulSoup
from pathlib import Path
from typing import Union, Dict, Iterator
import os
import json
import oora
from dataclasses import dataclass
from .config import USER_MAX_DIR

locales_dir = Path(__file__).parent / "locales"
gettext.bindtextdomain("messages", str(locales_dir))
gettext.textdomain("messages")
_ = gettext.gettext

CONFIG_INIT_TEMPLATE = """<?xml version="1.0" encoding="UTF-8"?>
<configuration xmlns="http://certic.unicaen.fr/max/ns/1.0" env="dev" vocabulary-bundle="max-dumb-xml">
    <version name="0.0.2" url="https://git.unicaen.fr/pdn-certic/max-v2/-/archive/0.0.2/max-v2-0.0.2.zip"/>
    <languages>
        <language>fr</language>
        <language>en</language>
    </languages>
    <title>mon Corpus Numérique</title>
    <bundles>    
        <bundle name="max-dumb-xml"/>
        <bundle name="max-export"/>
        <bundle name="max-dev"/>
    </bundles>
</configuration>
"""

DEFAULT_DOT_BASEX_FILE = """# General Options
DEBUG = false
DBPATH = .max/basex/data
LOGPATH = .logs
REPOPATH = .max/basex/repo
LANG = English
FAIRLOCK = false
CACHETIMEOUT = 3600
WRITESTORE = true

# Client/Server Architecture
HOST = localhost
PORT = 1984
SERVERPORT = 1984
USER = 
PASSWORD = 
SERVERHOST = 
PROXYHOST = 
PROXYPORT = 0
NONPROXYHOSTS = 
IGNORECERT = false
TIMEOUT = 30
KEEPALIVE = 600
PARALLEL = 8
LOG = data
LOGEXCLUDE = 
LOGCUT = 
LOGMSGMAXLEN = 1000
LOGTRACE = true

# HTTP Services
WEBPATH = .max/basex/webapp
GZIP = false
RESTPATH = 
RESTXQPATH = 
PARSERESTXQ = 3
RESTXQERRORS = true
HTTPLOCAL = false
STOPPORT = 8081
AUTHMETHOD = Basic

# Local Options
"""


class MaXProjectConfig:
    def __init__(self, path_to_config_file: Union[str, Path]):
        self.config_file_path = Path(path_to_config_file).resolve()
        if os.path.isfile(self.config_file_path):
            with open(self.config_file_path, "r") as f:
                self.xml_soup = BeautifulSoup(f, "xml")
        else:
            self.xml_soup = BeautifulSoup(CONFIG_INIT_TEMPLATE, "xml")
        first = self.xml_soup.find()
        if first and first.name != "configuration":
            raise ValueError(
                _("{} is not a MaX configuration file").format(self.config_file_path)
            )
        conf = self.xml_soup.find("configuration")
        if not conf:
            conf = self.xml_soup.new_tag("configuration")
            conf["env"] = "dev"
            conf["vocabulary-bundle"] = "max-dumb-xml"
            conf["xmlns"] = "http://certic.unicaen.fr/max/ns/1.0"
            self.xml_soup.append(conf)

    @property
    def available_bundles(self) -> Dict[str, Dict]:
        active_bundles = self.bundles
        available_bundles = {}
        available_bundles_xml = Path(
            os.path.dirname(self.config_file_path),
            ".max",
            "resources",
            "available-bundles.xml",
        )
        if available_bundles_xml.is_file():
            with open(available_bundles_xml, "r") as file_handle:
                soup = BeautifulSoup(file_handle.read(), "xml")
                for b in soup.find_all("bundle"):
                    available_bundles[b["name"]] = {
                        "name": b["name"],
                        "url": b["url"] if b.has_attr("url") else "",
                        "description": b["description"]
                        if b.has_attr("description")
                        else "",
                        "active": b["name"] in active_bundles.keys(),
                        "vocabulary": True
                        if (
                            b.has_attr("vocabulary-bundle")
                            and b["vocabulary-bundle"] == "true"
                        )
                        else False,
                    }
        return dict(sorted(available_bundles.items()))

    @property
    def max_version_from_max_dir(self) -> str:
        expath_pkg = Path(
            os.path.dirname(self.config_file_path),
            ".max",
            "resources",
            "expath-pkg.xml",
        )
        if expath_pkg.is_file():
            with open(expath_pkg, "r") as expath_handle:
                soup = BeautifulSoup(expath_handle.read(), "xml")
                package = soup.find("package")
                if package:
                    return package["version"]
        return ""

    @property
    def env(self) -> str:
        conf = self.xml_soup.find("configuration")
        val = conf.get("env", "dev")
        return str(val)

    @env.setter
    def env(self, value: str):
        conf = self.xml_soup.find("configuration")
        conf["env"] = value

    @property
    def vocabulary_bundle(self) -> str:
        conf = self.xml_soup.find("configuration")
        val = conf.get("vocabulary-bundle", "max-dumb-xml")
        return str(val)

    @vocabulary_bundle.setter
    def vocabulary_bundle(self, value):
        conf = self.xml_soup.find("configuration")
        conf["vocabulary-bundle"] = value

    @property
    def title(self) -> str:
        val = "untitled"
        conf = self.xml_soup.find("configuration")
        xml_node = conf.find("title")
        if xml_node:
            val = xml_node.text.strip()
        return str(val)

    @title.setter
    def title(self, value):
        conf = self.xml_soup.find("configuration")
        xml_node = conf.find("title")
        if not xml_node:
            xml_node = self.xml_soup.new_tag("title")
            conf.append(xml_node)
        xml_node.string = value

    @property
    def languages(self) -> list[str]:
        vals = []
        conf = self.xml_soup.find("configuration")
        nodes = conf.find("languages")
        if nodes:
            for language in nodes.find_all("language"):
                vals.append(language.text.strip())
        return vals

    @languages.setter
    def languages(self, languages: list[str]):
        conf = self.xml_soup.find("configuration")
        nodes = conf.find("languages")
        if not nodes:
            nodes = self.xml_soup.new_tag("languages")
            conf.append(nodes)
        nodes.clear()
        for language in languages:
            language_tag = self.xml_soup.new_tag("language")
            language_tag.string = language
            nodes.append(language_tag)

    @property
    def bundles(self) -> Dict[str, Dict]:
        vals = {}
        conf = self.xml_soup.find("configuration")
        nodes = conf.find("bundles")
        if nodes:
            for bundle in nodes.find_all("bundle"):
                vals[bundle["name"]] = {
                    "name": bundle["name"],
                    "url": bundle["url"] if bundle.has_attr("url") else "",
                }
        return vals

    @bundles.setter
    def bundles(self, bundles: Dict[str, Dict]):
        conf = self.xml_soup.find("configuration")
        nodes = conf.find("bundles")
        if not nodes:
            nodes = self.xml_soup.new_tag("bundles")
            conf.append(nodes)
        nodes.clear()
        for bundle_name, bundle_dict in bundles.items():
            bundle_tag = self.xml_soup.new_tag("bundle")
            bundle_tag["name"] = bundle_dict["name"]
            if bundle_dict.get("url"):
                bundle_tag["url"] = bundle_dict["url"]
            nodes.append(bundle_tag)

    @property
    def max_version(self) -> Dict[str, str]:
        version_node = self.xml_soup.find("version")
        if not version_node:
            return {"name": "", "url": ""}
        return {"name": version_node["name"], "url": version_node["url"]}

    @max_version.setter
    def max_version(self, values: Dict[str, str]):
        conf = self.xml_soup.find("configuration")
        version_node = conf.find("version")
        if not version_node:
            version_node = self.xml_soup.new_tag("version")
            conf.append(version_node)
        version_node["name"] = values.get("name", "")
        version_node["url"] = values.get("url", "")

    def __str__(self):
        return self.xml_soup.prettify()

    def write(self):
        with open(self.config_file_path, "w") as f:
            f.write(str(self))


@dataclass
class MaxInstall:
    id: int
    path: str
    _meta: str = None

    def exists(self):
        own_path = Path(self.path)
        if own_path.is_dir() and Path(own_path, "config.xml").is_file():
            return True
        return False

    def config(self) -> Union[MaXProjectConfig, None]:
        if self.exists():
            return MaXProjectConfig(Path(self.path, "config.xml"))

    @property
    def meta(self) -> dict:
        if self._meta:
            return json.loads(self._meta)
        return {}

    @meta.setter
    def meta(self, data: dict = None):
        if data is not None:
            self._meta = json.dumps(data)
        else:
            self._meta = None


class ClimaxStore(oora.DB):
    def fetch_or_create_project_from_path(self, path) -> Union[MaxInstall, None]:
        row = self.execute(
            "select id, path, _meta from maxinstall where path = ?", [path]
        ).fetchone()
        if row:
            return self.hydrate(MaxInstall, row)
        else:
            return MaxInstall(None, path)

    def projects(self) -> Iterator[MaxInstall]:
        for row in self.execute("select id, path, _meta from maxinstall"):
            yield self.hydrate(MaxInstall, row)


def db() -> ClimaxStore:
    return ClimaxStore(
        db_path=Path(
            USER_MAX_DIR,
            "climax.sqlite3",
        ),
        migrations={
            "0000": "CREATE TABLE IF NOT EXISTS maxinstall(id INTEGER PRIMARY KEY, path TEXT UNIQUE ON CONFLICT REPLACE NOT NULL);",
            "0001": "ALTER TABLE maxinstall ADD COLUMN _meta TEXT;",
        },
    ).migrate()
