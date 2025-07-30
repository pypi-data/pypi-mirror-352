import subprocess
from pathlib import Path
from typing import Optional, Union, Iterator, List
from typing_extensions import Annotated
import gettext
import tempfile
import geler
import requests
import os
import hashlib
import platform
from bs4 import BeautifulSoup
import shutil
from functools import cache
import socket
import json
from .eggs import get_yolk
from .model import MaXProjectConfig, db as climax_db, DEFAULT_DOT_BASEX_FILE
from .config import (
    WELCOME_PAGE,
    USER_MAX_DIR,
    CACHE_DIR,
    MAX_CONFIG_FILE,
    BASEX_DISTRO,
    SAXON_DISTRO,
    JAVA_DISTROS,
    WEB_PORT,
    WEB_HOST,
    BASEX_PORT,
    STOP_PORT,
    max_releases,
    max_release,
    latest_max_release,
    CLI_MAIN_HELP,
    CRASH_MESSAGE,
)

locales_dir = Path(Path(__file__).parent, "locales")
gettext.bindtextdomain("messages", str(locales_dir))
gettext.textdomain("messages")
_ = gettext.gettext


import typer  # noqa: E402
from rich import print as rich_print  # noqa: E402
from rich.progress import track  # noqa: E402
from rich.console import Console  # noqa: E402
from rich.table import Table  # noqa: E402


def _ping_projects(max_install_directory: Path, meta: dict = None):
    if isinstance(max_install_directory, str):
        max_install_directory = Path(max_install_directory)
    db = climax_db()
    max_install = db.fetch_or_create_project_from_path(
        str(max_install_directory.resolve())
    )
    if meta is not None:
        max_install.meta = meta
    db.save(max_install)
    db.commit()


last_project_dir = None


def _track_last_dir(directory: Path) -> Path:
    global last_project_dir
    last_project_dir = directory
    _ping_projects(directory)
    return directory


def _port_is_in_use(port: int, host: str = "localhost") -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex((host, port)) == 0


def _closer_free_port_to(start_port: int) -> int:
    limit_iter = 0
    while _port_is_in_use(start_port) and limit_iter < 50:
        start_port = start_port + 1
        limit_iter = limit_iter + 1
    return start_port


def _free_port() -> int:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("localhost", 0))
    port = s.getsockname()[1]
    s.close()
    return port


def _scan_dir(start_path: Union[str, Path], extension: str = None) -> Iterator[Path]:
    for root, dirs, files in os.walk(start_path):
        for file in files:
            if extension:
                if file[(len(extension) * -1) :].lower() == extension.lower():
                    yield os.path.join(root, file)
            else:
                yield Path(os.path.join(root, file)).resolve()


@cache
def current_system() -> str:
    return f"{platform.system()}/{platform.machine()}".lower()


@cache
def current_os() -> str:
    return current_system().split("/")[0]


@cache
def class_path_separator() -> str:
    separator = ":"
    if current_os() == "windows":
        separator = ";"
    return separator


@cache
def cp_paths(working_dir: str = os.getcwd()) -> str:
    basex_dir_path = Path(working_dir, ".max", "basex")
    paths = class_path_separator().join(
        [
            str(Path(basex_dir_path, "BaseX.jar")),
            str(Path(basex_dir_path, "lib", "custom", "*")),
            str(Path(basex_dir_path, "lib", "*")),
        ]
    )
    return paths


@cache
def find_jdk(cur_sys: str = None) -> Optional[str]:
    if not cur_sys:
        cur_sys = current_system()
    return JAVA_DISTROS.get(cur_sys, None)


def dir_is_max(directory: Union[str, Path] = os.getcwd()) -> bool:
    directory = Path(directory)
    config_file = Path(directory, "config.xml")
    if config_file.exists():
        with open(config_file, "r") as f:
            soup = BeautifulSoup(f, "xml")
            conf = soup.find("configuration")
            if conf:
                ns = conf.get("xmlns")
                if ns == "http://certic.unicaen.fr/max/ns/1.0":
                    _track_last_dir(directory)
                    return True
    return False


def check_dir_is_max(directory):
    if not dir_is_max(directory):
        rich_print(
            "[red]{}[/red]".format(_("Le dossier n'est pas une installation de MaX."))
        )
        raise typer.Exit(code=1)


def max_config(directory: Union[Path, str] = os.getcwd()) -> MaXProjectConfig:
    return MaXProjectConfig(Path(directory, MAX_CONFIG_FILE))


def unzip(source: Union[Path, str], destination: Union[Path, str]) -> bool:
    shutil.unpack_archive(source, destination)
    os.remove(source)
    return True


def cached_download(
    source: str, destination: Union[Path, str], chunk_size: int = 1024
) -> bool:
    cache_path = Path(CACHE_DIR, hashlib.sha1(source.encode("utf-8")).hexdigest())
    if cache_path.exists():
        shutil.copy(cache_path, destination)
    else:
        response = requests.get(source, stream=True)
        if response.status_code != 200:
            rich_print(
                "[red]{}[/red] {}".format(_("Impossible de télécharger"), source)
            )
            raise typer.Exit(code=1)
        try:
            total_size = int(response.headers["Content-length"])
            seq_len = total_size // chunk_size
        except KeyError:
            # missing Content-length
            seq_len = 100
        with open(cache_path, "wb") as f:
            for data in track(
                response.iter_content(chunk_size=chunk_size),
                total=seq_len,
                description=os.path.basename(source),
            ):
                f.write(data)
        shutil.copy(cache_path, destination)
    return True


@cache
def ensure_java() -> Path:
    java_bin = shutil.which("java")
    if not java_bin:
        cur_sys = current_system()
        suitable_jdk = find_jdk(cur_sys)
        if suitable_jdk:
            destination_folder = Path(USER_MAX_DIR, "jdk")
            if not destination_folder.exists():
                destination_archive = Path(USER_MAX_DIR, os.path.basename(suitable_jdk))
                cached_download(suitable_jdk, destination_archive)
                unzip(destination_archive, destination_folder)
            if cur_sys in ["linux/x86_64", "linux/amd64"]:
                java_bin = Path(destination_folder, "jdk-22.0.2", "bin", "java")
            if cur_sys in ["windows/x86_64", "windows/amd64"]:
                java_bin = Path(destination_folder, "jdk-22.0.2", "bin", "java.exe")
            if cur_sys == "darwin/arm64":
                java_bin = Path(
                    destination_folder,
                    "jdk-22.0.2.jdk",
                    "Contents",
                    "Home",
                    "bin",
                    "java",
                )
    if not java_bin:
        rich_print(
            "[red]"
            + _("Java est requis pour utiliser MaX: https://openjdk.org/install/")
            + "[/red]"
        )
        raise typer.Exit(code=1)
    return java_bin


def ensure_available_max_directory(directory: str = os.getcwd()) -> tuple[Path, bool]:
    directory = Path(directory)
    if not directory.exists():
        directory.mkdir(parents=True, exist_ok=False)
    directory = directory.resolve()
    is_empty = not any(directory.iterdir())
    is_max = dir_is_max(directory)
    if not is_empty and not is_max:
        rich_print(
            "[red]{}[/red]".format(
                _(
                    "Le dossier n'est pas vide et n'est pas un projet MaX valide, veuillez en choisir un autre."
                )
            )
        )
        raise typer.Exit(code=1)
    return directory, is_max


app = typer.Typer(help=_(CLI_MAIN_HELP))


def _sync_bundles(root_directory: Path):
    ignore_file = ".ignore"
    dot_max_dir = Path(root_directory, ".max")
    official_bundles_dir = Path(dot_max_dir, "basex", "webapp", "max", "bundles")
    # first deactivate everything
    for item in os.listdir(official_bundles_dir):
        if os.path.isdir(Path(official_bundles_dir, item)):
            Path(official_bundles_dir, item, ignore_file).touch()
    config = MaXProjectConfig(Path(root_directory, "config.xml"))
    vocabulary_bundle = config.vocabulary_bundle
    # then activate or install what is in config file
    for bundle_name, bundle in config.bundles.items():
        bundle_dir = Path(official_bundles_dir, bundle_name)
        if os.path.isdir(bundle_dir):
            Path(bundle_dir, ignore_file).unlink(missing_ok=True)
        else:
            if str(bundle["url"]).startswith("http://") or str(
                bundle["url"]
            ).startswith("https://"):
                bundle_archive_path = Path(official_bundles_dir, f"{bundle_name}.zip")
                cached_download(bundle["url"], bundle_archive_path)
                shutil.unpack_archive(bundle_archive_path, official_bundles_dir)
                dir_name, _ignore = os.path.splitext(os.path.basename(bundle["url"]))
                Path(official_bundles_dir, dir_name).rename(bundle_dir)
                bundle_archive_path.unlink()
            if str(bundle["url"]).startswith("local://"):
                zip_name = str(bundle["url"])[len("local://") :]
                bundle_archive_path = Path(
                    dot_max_dir, "resources", "local_bundles", f"{zip_name}"
                )
                shutil.unpack_archive(bundle_archive_path, official_bundles_dir)
                dir_name, _ignore = os.path.splitext(os.path.basename(bundle["url"]))
                Path(official_bundles_dir, dir_name).rename(bundle_dir)
                bundle_archive_path.unlink()
        if (
            Path(bundle_dir, "expath-pkg.xml").exists()
            and bundle_name != vocabulary_bundle
        ):
            # deactivate vocabulary bundles if they're not the vocabulary used in the projects
            print(_("Ce bundle de vocabulaire sera ignoré: "), bundle_name)
            Path(bundle_dir, ignore_file).touch()
    _ping_projects(root_directory)


def _copy_max_tree(
    dot_max_dir: Union[str, Path], max_release_name: str, max_release_url: str
):
    with tempfile.TemporaryDirectory() as tmpdirname:
        zip_destination = Path(tmpdirname, "max.zip")
        cached_download(max_release_url, zip_destination)
        unzip(zip_destination, tmpdirname)
        shutil.copytree(
            Path(tmpdirname, f"max-v2-{max_release_name}", "src", "main", "core"),
            Path(dot_max_dir, "basex", "webapp", "max", "core"),
            dirs_exist_ok=True,
        )
        shutil.copytree(
            Path(tmpdirname, f"max-v2-{max_release_name}", "src", "main", "bundles"),
            Path(dot_max_dir, "basex", "webapp", "max", "bundles"),
            dirs_exist_ok=True,
        )
        shutil.copytree(
            Path(tmpdirname, f"max-v2-{max_release_name}", "src", "resources"),
            Path(dot_max_dir, "resources"),
            dirs_exist_ok=True,
        )


def _install_new_max_instance(root_directory: Path, init_values: dict = None):
    rich_print(
        "[bold]"
        + _("Initialisation d'une nouvelle instance de MaX dans {}").format(
            root_directory
        )
        + "[/bold]"
    )
    config_file_path = Path(root_directory, "config.xml")

    with open(Path(root_directory, ".gitignore"), "w", encoding="utf-8") as f:
        f.write(".max\n")

    conf = MaXProjectConfig(config_file_path)
    if init_values is not None:
        conf.title = init_values.get("title", "")
        conf.env = init_values.get("env", "prod")
        conf.max_version = {
            "name": init_values.get("max_version"),
            "url": init_values.get("max_url"),
        }
    else:
        conf.title = "inconnu"
        conf.env = "prod"
        latest_max = latest_max_release()
        conf.max_version = {
            "name": latest_max["name"],
            "url": latest_max["zip_url"],
        }
    conf.write()

    _sync_max_instance(root_directory, verbose=False)

    Path(root_directory, "content_html", "fr").mkdir(exist_ok=True, parents=True)
    welcome_page = Path(root_directory, "content_html", "fr", "index.html")
    with open(welcome_page, "w", encoding="utf-8") as f:
        f.write(WELCOME_PAGE)
    rich_print(
        "[bold]"
        + _("La nouvelle instance de MaX est prête dans {}").format(root_directory)
        + "[/bold]"
    )
    rich_print(
        _(
            'Vous pouvez éventuellement installer un projet de démonstration avec "climax demo".'
        )
    )


def _sync_max_instance(root_directory: Path, verbose=True):
    if verbose:
        rich_print(
            "[bold]"
            + _("Initialisation de l'instance de MaX existant dans {}").format(
                root_directory
            )
            + "[/bold]"
        )
    config = MaXProjectConfig(Path(root_directory, "config.xml"))
    config.max_version_from_max_dir
    dot_max_dir = Path(root_directory, ".max")
    if not os.path.isdir(
        dot_max_dir
    ) or config.max_version_from_max_dir != config.max_version.get("name"):
        dot_max_dir.mkdir(parents=True, exist_ok=True)
        basex_zip_destination = Path(dot_max_dir, "BaseX.zip")
        cached_download(BASEX_DISTRO, basex_zip_destination)
        unzip(basex_zip_destination, dot_max_dir)
        saxon_zip_destination = Path(
            dot_max_dir, "basex", "lib", "custom", "Saxon-HE-10.8.jar"
        )
        cached_download(SAXON_DISTRO, saxon_zip_destination)

        _copy_max_tree(
            Path(root_directory, ".max"),
            config.max_version.get("name"),
            config.max_version.get("url"),
        )

        with open(
            Path(root_directory, dot_max_dir, "basex", ".basex"), "w", encoding="utf-8"
        ) as f:
            f.write(DEFAULT_DOT_BASEX_FILE)

    _sync_bundles(root_directory)
    if verbose:
        rich_print(
            "[bold]"
            + _("L'instance de MaX est prête dans {}").format(root_directory)
            + "[/bold]"
        )


@app.command(
    help=_(
        "Création d'une nouvelle instance de MaX\n\nL'option --interactive propose un menu pour choisir sa configuration."
    )
)
def new(
    directory: Annotated[
        Optional[Path], typer.Argument(help=_("chemin vers un dossier"))
    ] = os.getcwd(),
    interactive: bool = False,
):
    ensure_java()
    root_directory, is_max = ensure_available_max_directory(directory)
    if is_max:
        rich_print(
            _("Le dossier contient une instance de MaX. Utilisez la commande sync")
        )
        raise typer.Exit()
    init_values = None
    if interactive:
        try:
            init_values = {}
            init_values["max_version"] = _choose_between(
                [x["name"] for x in max_releases()], _("Version de max")
            )
            init_values["max_url"] = max_release(init_values["max_version"]).get(
                "zip_url"
            )
            init_values["env"] = _choose_between(["dev", "prod"], _("Environnement"))
            init_values["title"] = typer.prompt(_("Titre du projet"))
        except (KeyboardInterrupt, TypeError):
            root_directory.rmdir()
            return
    _install_new_max_instance(root_directory, init_values)


@app.command(help=_("Installe une édition de démonstration."))
def demo(
    directory: Annotated[
        str, typer.Option(help=_("Dossier du projet MaX"))
    ] = os.getcwd(),
):
    directory = Path(directory).resolve()
    check_dir_is_max(directory)
    os.chdir(directory)
    if typer.confirm(
        _("Voulez-vous installer une édition de démonstration ?"), default=False
    ):
        cur_dir = directory
        config = MaXProjectConfig(Path(cur_dir, "config.xml"))
        with tempfile.TemporaryDirectory() as tmpdirname:
            zip_destination = Path(tmpdirname, "max.zip")
            cached_download(config.max_version["url"], zip_destination)
            unzip(zip_destination, tmpdirname)
            tmp_max_release_dir = Path(
                tmpdirname, f"max-v2-{config.max_version['name']}"
            )

            shutil.copytree(  ## BaseX databases
                Path(tmp_max_release_dir, "fixtures", "max"),
                Path(cur_dir, ".max", "basex", "data", "max"),
                dirs_exist_ok=True,
            )

            shutil.copytree(
                Path(tmp_max_release_dir, "fixtures"),
                Path(cur_dir),
                dirs_exist_ok=True,
            )
            shutil.rmtree(Path(cur_dir, "max"), ignore_errors=True)
            _sync_max_instance(cur_dir, verbose=False)

        rich_print("[green]" + _("édition de démonstration installée") + "[/green]")
        rich_print(
            _("Vous pouvez démarrer MaX avec la commande [bold]climax start[/bold]")
        )


def _start_http_server(
    http_host: str = WEB_HOST,
    http_port: int = WEB_PORT,
    basex_port: int = BASEX_PORT,
    http_stop_port: int = STOP_PORT,
    service: bool = False,
    directory: str = os.getcwd(),
    ping_projects: bool = True,
):
    basex_port = _closer_free_port_to(basex_port)
    http_port = _closer_free_port_to(http_port)
    if http_stop_port <= http_port:
        http_stop_port = http_port + 1
    http_stop_port = _closer_free_port_to(http_stop_port)
    directory = Path(directory).resolve()
    check_dir_is_max(directory)
    os.chdir(directory)
    java_bin_path = ensure_java()
    process_args = [
        str(java_bin_path),
        "-cp",
        cp_paths(directory),
        "-Xmx2g",
        "org.basex.BaseXHTTP",
        f"-p{basex_port}",
        f"-h{http_port}",
        f"-n{http_host}",
        f"-s{http_stop_port}",
    ]
    if service:
        process_args.append("-S")
    rich_print(
        "[green]"
        + _("Démarrage de MaX sur http://{}:{}").format(http_host, http_port)
        + "[/green]"
    )
    if ping_projects:
        _ping_projects(
            directory,
            {
                "basex_port": basex_port,
                "http_port": http_port,
                "http_host": http_host,
                "http_stop_port": http_stop_port,
            },
        )
    try:
        subprocess.run(process_args)
    except KeyboardInterrupt:
        _ping_projects(directory, {})


@app.command(
    help=_(
        "Démarre l'instance de MaX.\n\nSi les ports choisis ne sont pas disponibles, climax tentera de lancer le serveur sur d'autres ports."
    )
)
def start(
    http_host: str = WEB_HOST,
    http_port: int = WEB_PORT,
    basex_port: int = BASEX_PORT,
    http_stop_port: int = STOP_PORT,
    service: Annotated[
        bool,
        typer.Option(
            help=_(
                'Démarrer MaX en tant que service. Utilisez "climax stop" pour arrêter le service.'
            )
        ),
    ] = False,
    directory: Annotated[
        str, typer.Option(help=_("Dossier du projet MaX"))
    ] = os.getcwd(),
):
    _start_http_server(
        http_host, http_port, basex_port, http_stop_port, service, directory, True
    )


def _choose_between(values: List[str], label: str = "") -> str:
    try:
        from simple_term_menu import TerminalMenu

        terminal_menu = TerminalMenu(values, title=label)
        menu_entry_index = terminal_menu.show()
        return values[menu_entry_index]
    except NotImplementedError:  # mainly windows
        choice = None
        while choice not in values:
            choice = typer.prompt("{} ({})".format(_(label), ", ".join(values)))
        return choice


@app.command(help=_("Arrête l'instance de MaX"))
def stop(
    http_stop_port: int = STOP_PORT,
    directory: Annotated[
        str, typer.Option(help=_("Dossier du projet MaX"))
    ] = os.getcwd(),
):
    directory = Path(directory).resolve()
    check_dir_is_max(directory)
    os.chdir(directory)
    java_bin_path = ensure_java()
    process_args = [
        str(java_bin_path),
        "-cp",
        cp_paths(directory),
        "-Xmx2g",
        "org.basex.BaseXHTTP",
        f"-s{http_stop_port}",
        "stop",
    ]
    subprocess.run(process_args)
    _ping_projects(directory, {})


@app.command(help=_("Affiche la configuration de MaX"))
def info(
    directory: Annotated[
        str, typer.Option(help=_("Dossier du projet MaX"))
    ] = os.getcwd(),
    json_out: bool = False,
):
    directory = Path(directory).resolve()
    check_dir_is_max(directory)
    os.chdir(directory)
    config = max_config(directory)
    if json_out:
        print(
            json.dumps(
                {
                    "max_version": config.max_version.get("name"),
                    "title": config.title,
                    "environment": config.env,
                    "languages": config.languages,
                    "bundles": config.bundles,
                    "vocabulary_bundle": config.vocabulary_bundle,
                },
                indent=4,
            )
        )
    else:
        console = Console()
        table = Table(_("Nom"), _("Valeur"), show_lines=True)
        table.add_row(_("Version de MaX"), config.max_version.get("name"))
        table.add_row(_("Titre"), config.title)
        table.add_row(_("Environnement"), config.env)
        table.add_row(_("Langues"), ", ".join(config.languages))
        table.add_row(_("Bundles installés"), ", ".join(config.bundles.keys()))
        table.add_row(_("Bundle de vocabulaire XML"), config.vocabulary_bundle)
        console.print(table)


@app.command(help=_("Fait une copie HTML statique"))
def freeze(
    output: Annotated[
        str, typer.Option(help=_("Dossier de sortie des fichiers HTML"))
    ] = None,
    directory: Annotated[str, typer.Option(help=_("Dossier du projet MaX"))] = Path(
        os.getcwd()
    ),
    debug: bool = False,
):
    if output is None:
        output = Path(directory, "html_output")
    max_config(directory)
    # start server on specific port
    port_number = _free_port()
    stop_port = port_number + 1
    stop_port = _closer_free_port_to(stop_port)
    _start_http_server(
        WEB_HOST,
        port_number,
        http_stop_port=stop_port,
        service=True,
        directory=directory,
        ping_projects=False,
    )
    # copy website
    try:
        start_url = f"http://localhost:{port_number}/"
        geler.freeze(start_url, output)
    except Exception as e:
        stop(stop_port)
        raise e
    # stop server
    stop(stop_port, directory)
    rich_print("[green]" + _("Site copié dans {}").format(str(output)) + "[/green]")


@app.command(help=_("Liste les bundles disponibles"))
def bundles_list(
    directory: Annotated[
        str, typer.Option(help=_("Dossier du projet MaX"))
    ] = os.getcwd(),
):
    directory = Path(directory).resolve()
    check_dir_is_max(directory)
    os.chdir(directory)
    config = max_config(directory)
    console = Console()
    table = Table(_("Nom"), _("Installé"), _("Description"), show_lines=True)
    bundles_done = {}

    for bundle_name, bundle in config.available_bundles.items():
        bundles_done[bundle_name] = [
            "[bold]{}[/bold]".format(bundle["name"]),
            "[green]{}[/green]".format(_("oui"))
            if bundle["active"]
            else "[red]{}[/red]".format(_("non")),
            bundle["description"],
        ]

    for bundle_name, bundle in config.bundles.items():
        if bundle_name not in bundles_done.keys():
            bundles_done[bundle_name] = [
                "[bold]{}[/bold]".format(bundle_name),
                "[green]{}[/green]".format(_("oui")),
                _("(bundle local sans description)"),
            ]
    for k, row in dict(sorted(bundles_done.items())).items():
        table.add_row(*row)
    console.print(table)


@app.command(help=_("Ajoute un bundle"))
def bundles_add(
    bundle_name: str,
    directory: Annotated[
        str, typer.Option(help=_("Dossier du projet MaX"))
    ] = os.getcwd(),
):
    from_archive = None
    directory = Path(directory).resolve()
    check_dir_is_max(directory)
    os.chdir(directory)
    config = max_config(directory)
    current_bundles_config = config.bundles
    # bundle_name is a local archive
    if bundle_name.endswith(".zip") and Path(bundle_name).is_file():
        from_archive = bundle_name
        bundle_name = os.path.splitext(os.path.basename(bundle_name))[0]
    if from_archive is not None:
        if type(from_archive) is str:
            from_archive = Path(from_archive)
        if not from_archive.is_file():
            rich_print(
                _("[red][bold]{}[/bold] n'est pas un chemin valide[/red]").format(
                    from_archive
                )
            )
            raise typer.Exit(code=1)
        fname, extension = os.path.splitext(from_archive)
        if extension != ".zip":
            rich_print(_("[red]{} n'est pas un bundle[/red]").format(from_archive))
            raise typer.Exit(code=1)
        local_destination = Path(
            directory,
            ".max",
            "resources",
            "local_bundles",
            os.path.basename(from_archive),
        )
        Path(os.path.dirname(local_destination)).mkdir(exist_ok=True, parents=True)
        shutil.copy(from_archive, local_destination)
        current_bundles_config[bundle_name] = {
            "name": bundle_name,
            "url": f"local://{os.path.basename(local_destination)}",
        }
        config.bundles = current_bundles_config
        # if bundle has expath-pkg.xml, it's a vocabulary bundle
        if Path(local_destination, "expath-pkg.xml").exists():
            config.vocabulary_bundle = bundle_name
        config.write()
        _sync_max_instance(directory, verbose=False)
        bundles_list(directory)
    else:
        if bundle_name not in config.available_bundles.keys():
            rich_print(
                _("[red]{} n'est pas un bundle disponible[/red]").format(bundle_name)
            )
            raise typer.Exit(code=1)
        else:
            for (
                available_bundle_name,
                available_bundle,
            ) in config.available_bundles.items():
                if available_bundle_name == bundle_name:
                    if available_bundle["vocabulary"]:
                        config.vocabulary_bundle = bundle_name
                    current_bundles_config[bundle_name] = {
                        "name": bundle_name,
                        "url": available_bundle["url"],
                    }
                    config.bundles = current_bundles_config
                    config.write()
                    _sync_max_instance(directory, verbose=False)
                    bundles_list()


@app.command(help=_("Supprime un bundle"))
def bundles_remove(
    bundle_name: str,
    directory: Annotated[
        str, typer.Option(help=_("Dossier du projet MaX"))
    ] = os.getcwd(),
):
    directory = Path(directory).resolve()
    check_dir_is_max(directory)
    os.chdir(directory)
    config = max_config(directory)
    keep_bundles = {}
    bundle_name = bundle_name.lower().strip()
    if bundle_name not in config.bundles.keys():
        rich_print(_("[red]{} n'est pas un bundle actif[/red]").format(bundle_name))
        raise typer.Exit(code=1)
    for active_bundle_name, active_bundle_url in config.bundles.items():
        if active_bundle_name.strip() != bundle_name.strip():
            keep_bundles[active_bundle_name] = active_bundle_url
    config.bundles = keep_bundles
    config.write()
    _sync_max_instance(directory, verbose=False)
    bundles_list(directory)


@app.command(help=_("Ajoute un fichier ou un dossier XML"))
def feed(
    feed_path: Path,
    directory: Annotated[
        str, typer.Option(help=_("Dossier du projet MaX"))
    ] = os.getcwd(),
):
    directory = Path(directory).resolve()
    check_dir_is_max(directory)
    os.chdir(directory)
    java_bin_path = ensure_java()
    feed_path = Path(feed_path).resolve()
    if not feed_path.is_file() and not feed_path.is_dir():
        rich_print(_("[red]{} n'existe pas[/red]").format(feed_path))
        raise typer.Exit(code=1)
    process_args = [
        str(java_bin_path),
        "-cp",
        cp_paths(directory),
        "-Xmx2g",
        "org.basex.BaseX",
        "if(not(db:exists('max'))) then db:create('max') else ()",
    ]
    subprocess.run(process_args)

    if feed_path.is_file():
        process_args = [
            str(java_bin_path),
            "-cp",
            cp_paths(directory),
            "-Xmx2g",
            "org.basex.BaseX",
            f"db:put('max', '{feed_path}', '{feed_path.name}')",
            # f"-cOPEN max; REPLACE {feed_path.resolve()}",
        ]
        rich_print(feed_path)
        subprocess.run(process_args)
    elif feed_path.is_dir():
        offset = len(str(feed_path))
        for f in _scan_dir(feed_path, ".xml"):
            process_args = [
                str(java_bin_path),
                "-cp",
                cp_paths(directory),
                "-Xmx2g",
                "org.basex.BaseX",
                f"db:put('max', '{f}', '{str(f)[offset:]}')",
                # f"-cOPEN max; REPLACE {f}",
            ]
            rich_print(f)
            subprocess.run(process_args)


@app.command(
    help=_(
        "Initialisation d'une instance existante de MaX.\n\nTélécharge et installe les dépendances nécessaires ainsi que les bundles configurés."
    )
)
def sync(
    directory: Annotated[
        Optional[Path], typer.Option(help=_("Dossier du projet MaX"))
    ] = os.getcwd(),
):
    ensure_java()
    root_directory, is_max = ensure_available_max_directory(directory)

    if is_max:
        _sync_max_instance(root_directory)
    else:
        rich_print(
            _(
                "Le dossier ne contient pas une instance de MaX. Utiliser la commande new"
            )
        )
        raise typer.Exit()


@app.command(help=_("Lance le shell de BaseX"))
def basex(
    directory: Annotated[
        str, typer.Option(help=_("Dossier du projet MaX"))
    ] = os.getcwd(),
):
    directory = Path(directory).resolve()
    check_dir_is_max(directory)
    os.chdir(directory)
    java_bin_path = ensure_java()
    process_args = [
        str(java_bin_path),
        "-cp",
        cp_paths(directory),
        "-Xmx2g",
        "org.basex.BaseX",
    ]
    subprocess.run(process_args)


@app.command(help=_("Liste les templates du bundle de vocabulaire"))
def templates_list(
    directory: Annotated[
        str, typer.Option(help=_("Dossier du projet MaX"))
    ] = os.getcwd(),
):
    directory = Path(directory).resolve()
    check_dir_is_max(directory)
    os.chdir(directory)
    config = max_config(directory)
    vocab_bundle = config.vocabulary_bundle
    tpl_dir = Path(
        directory,
        ".max",
        "basex",
        "webapp",
        "max",
        "bundles",
        vocab_bundle,
        "templates",
    )
    tpls_list = []
    offset = len(str(tpl_dir))
    for f in _scan_dir(tpl_dir):
        if f.is_file():
            tpls_list.append(str(f)[offset:])
    for item in sorted(tpls_list):
        print(item)


@app.command(
    help=_("Liste les fichiers statiques (js, css, etc) du bundle de vocabulaire")
)
def static_list(
    directory: Annotated[
        str, typer.Option(help=_("Dossier du projet MaX"))
    ] = os.getcwd(),
):
    directory = Path(directory).resolve()
    check_dir_is_max(directory)
    os.chdir(directory)
    config = max_config(directory)
    vocab_bundle = config.vocabulary_bundle
    tpl_dir = Path(
        directory,
        ".max",
        "basex",
        "webapp",
        "max",
        "bundles",
        vocab_bundle,
        "static",
    )
    tpls_list = []
    offset = len(str(tpl_dir))
    for f in _scan_dir(tpl_dir):
        if f.is_file():
            tpls_list.append(str(f)[offset:])
    for item in sorted(tpls_list):
        print(item)


@app.command(help=_("Liste les projets gérés par climax"))
def projects(json_out: bool = False):
    console = Console()
    table = Table(_("Projet"), _("Chemin"), _("URL"), show_lines=True)
    db = climax_db()
    projects_list = []
    for max_install in db.projects():
        if max_install.exists():
            config = max_install.config()
            url = ""
            if max_install.meta:
                if _port_is_in_use(
                    max_install.meta.get("http_port"), max_install.meta.get("http_host")
                ):
                    url = f"http://{max_install.meta.get('http_host')}:{max_install.meta.get('http_port')}/"
            table.add_row(config.title, max_install.path, url)
            projects_list.append(
                {
                    "title": str(config.title),
                    "path": str(max_install.path),
                    "url": str(url),
                }
            )
        else:
            db.delete("maxinstall", "id = ?", max_install.id)
            db.commit()
    if json_out:
        print(json.dumps({"projects": projects_list}, indent=4))
    else:
        console.print(table)


@app.command(help=_("Efface le cache de climax"))
def cache_clear():
    for p in CACHE_DIR.iterdir():
        if p.is_file():
            p.unlink(missing_ok=True)
    shutil.rmtree(Path(USER_MAX_DIR, "max"), ignore_errors=True)


@app.command(help=_("Affiche la version de climax"))
def version():
    import climax

    print(climax.__version__)


if os.environ.get("CLIMAX_DEBUG") == "True":

    @app.command(help=_("Planter Climax"))
    def crash(
        directory: Annotated[
            str, typer.Option(help=_("Dossier du projet MaX"))
        ] = os.getcwd(),
    ):
        dir_is_max(directory)
        raise ValueError("Something wrong happened.")


# @app.command(help=_("Application web (test)"))
# def ui(max_dir: str = None):
#    from .gui import app

#    app.max_directory = max_dir
#    app.run(port=8888, reloader=True, debug=True)


get_yolk()


def wrap_app_exceptions():
    try:
        app()
    except Exception:
        import traceback
        import datetime
        import platform
        import json
        import sys
        from . import __version__ as climax_version

        global last_project_dir
        max_config = ""
        if last_project_dir is not None:
            with open(Path(last_project_dir, "config.xml"), "r") as f:
                max_config = f.read()

        bug_report = {
            "time": datetime.datetime.now(datetime.UTC).timestamp(),
            "platform": platform.platform(),
            "climax_version": climax_version,
            "max_config": max_config,
            "working_dir": os.getcwd(),
            "traceback": traceback.format_exc(),
        }
        sys.exit(CRASH_MESSAGE.format(json.dumps(bug_report, indent=2)))


if __name__ == "__main__":
    wrap_app_exceptions()
