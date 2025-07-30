import os
import json
from pathlib import Path
from typing import List, Dict
from requests import get
from functools import cache
import logging

logger = logging.getLogger(__name__)

GITLAB_API_READ_TOKEN = "glpat-5BCYCid1WaxxBgax-7VW"

CLI_MAIN_HELP = """Utilitaire en ligne de commande pour la gestion des projets MaX.

La plupart des commandes sont à lancer dans le dossier du projet MaX, à l'exception des
commandes new, projects et cache-clear qui peuvent être lancées aussi en dehors d'un dossier MaX.
"""


CRASH_MESSAGE = r"""
OH NON !

  ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⡶⠛⠛⢦⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
  ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣴⠋⠀⠀⠀⠈⣧⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
  ⠀⠀⠀⠀⠀⢀⣠⠴⠞⠛⠉⠉⠉⠉⠉⠉⠛⠒⠾⢤⣀⠀⣀⣠⣤⣄⡀⠀⠀⠀
  ⠀⠀⠀⣠⡶⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠛⢭⡀⠀⠈⣷⠀⠀⠀
  ⠀⠀⡴⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⢦⢀⡟⠀⠀⠀
  ⠀⣾⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⢻⡅⠀⠀⠀
  ⢸⠇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢻⣄⣀⠀
  ⣾⠀⠀⣠⣤⣤⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣤⣤⣄⠀⠀⠀⠀⠀⠀⠸⡇⠉⣷
  ⣿⠀⠰⣿⣿⣿⡗⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⣿⣿⠀⠀⠀⠀⠀⠀⠀⣧⡴⠋
  ⣿⠀⠀⢸⠛⢫⠀⠀⢠⠴⠒⠲⡄⠀⠀⠀⠀⡝⠛⢡⠀⠀⠀⠀⠀⠀⢰⡏⠀⠀
  ⢸⡄⠀⢸⡀⢸⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡇⠀⢸⠀⠀⠀⠀⠀⠀⡼⣄⠀⠀
  ⠀⢳⡄⠀⡇⢸⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢹⠀⢸⠀⠀⠀⠀⢀⡼⠁⢸⡇⠀
  ⠀⠀⠙⢦⣷⡈⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⠀⠈⡇⠀⣀⡴⠟⠒⠚⠋⠀⠀
  ⠀⠀⠀⠀⠈⠛⠾⢤⣤⣀⣀⡀⠀⠀⠀⠀⣀⣈⣇⡤⣷⠚⠉⠀⠀⠀⠀⠀⠀⠀
  ⠀⠀⠀⠀⠀⠀⠀⣰⠇⠀⠩⣉⠉⠉⠉⣩⠍⠁⠀⢷⣟⠀⠀⠀⠀⠀⠀⠀⠀⠀
  ⠀⠀⠀⠀⠀⠀⠀⡟⠐⠦⠤⠼⠂⠀⠸⠥⠤⠔⠂⠘⣿⣇⠀⠀⠀⠀⠀⠀⠀⠀
  ⠀⠀⠀⠀⠀⠀⣸⣧⡟⠳⠒⡄⠀⠀⠀⡔⠲⠚⣧⣀⣿⠿⠷⣶⡆⠀⠀⠀⠀⠀
  ⠀⠀⠀⠀⠀⠀⠻⣄⢀⠀⠀⡗⠀⠀⠀⡇⠄⢠⠀⣼⠟⠀⢀⣨⠇⠀⠀⠀⠀⠀
  ⠀⠀⠀⠀⠀⠀⠀⠙⢶⠬⠴⢧⣤⣤⣤⣽⣬⡥⠞⠛⠛⠋⠉⠀⠀⠀⠀⠀⠀⠀

Climax s'est planté... nous somme navrés.

Vous vous rendriez un fier service en transmettant le rapport suivant à l'adresse contact.certic@unicaen.fr:

{}

N'hésitez pas à ajouter des détails sur les circonstances de cette erreur.
"""

WELCOME_PAGE = """
<h1>Bienvenue dans MaX !</h1>
<p>
    Vous pouvez personnaliser cette page en éditant le fichier content_html/fr/index.html
</p>
<p>
    Retrouvez la documentation de MaX à l'adresse suivante: 
    <a href="https://www.certic.unicaen.fr/max-v2/">
        https://www.certic.unicaen.fr/max-v2/
    </a>
</p>
"""

USER_MAX_DIR = os.getenv("CLIMAX_HOME") or Path(Path.home(), ".climax")
USER_MAX_DIR = Path(USER_MAX_DIR)
USER_MAX_DIR.mkdir(exist_ok=True)
CACHE_DIR = Path(USER_MAX_DIR, "cache")
CACHE_DIR.mkdir(exist_ok=True)
MAX_CONFIG_FILE = "config.xml"
BASEX_DISTRO = "https://files.basex.org/releases/11.7/BaseX117.zip"
SAXON_DISTRO = (
    "https://repo1.maven.org/maven2/net/sf/saxon/Saxon-HE/10.8/Saxon-HE-10.8.jar"
)

JAVA_DISTROS = {
    "linux/aarch64": "https://download.java.net/java/GA/jdk22.0.2/c9ecb94cd31b495da20a27d4581645e8/9/GPL/openjdk-22.0.2_linux-aarch64_bin.tar.gz",
    "darwin/arm64": "https://download.java.net/java/GA/jdk22.0.2/c9ecb94cd31b495da20a27d4581645e8/9/GPL/openjdk-22.0.2_macos-aarch64_bin.tar.gz",
    "linux/x86_64": "https://download.java.net/java/GA/jdk22.0.2/c9ecb94cd31b495da20a27d4581645e8/9/GPL/openjdk-22.0.2_linux-x64_bin.tar.gz",
    "windows/amd64": "https://download.java.net/java/GA/jdk22.0.2/c9ecb94cd31b495da20a27d4581645e8/9/GPL/openjdk-22.0.2_windows-x64_bin.zip",
}
WEB_PORT = 8080
WEB_HOST = "127.0.0.1"
BASEX_PORT = 1984
STOP_PORT = 8081


@cache
def max_releases() -> List[Dict]:
    try:
        response = get(
            "https://git.unicaen.fr/api/v4/projects/2429/releases",
            headers={"PRIVATE-TOKEN": GITLAB_API_READ_TOKEN},
            timeout=5,
        )
        if response.ok:
            return json.loads(response.content)
    except:  # noqa: E722
        logger.warning(
            "Could not fetch MaX releases from Gitlab API, fallback to cached response."
        )

    with open(
        Path(os.path.dirname(os.path.realpath(__file__)), "max_releases.json")
    ) as f:
        return json.load(f)


@cache
def max_release(release_name: str) -> Dict:
    for release in max_releases():
        if release.get("name") == release_name:
            if release["assets"]["count"] > 0:
                for source in release["assets"]["sources"]:
                    if source["format"] == "zip":
                        release["zip_url"] = source["url"]
            return release


@cache
def latest_max_release() -> Dict:
    return max_release(max_releases()[0]["name"])
