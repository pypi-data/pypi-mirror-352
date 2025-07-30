from typing import List, Dict, Union, Callable
import os
import yaml

from blueness import module

from bluer_objects import NAME as MY_NAME, ICON as MY_ICON
from bluer_objects.metadata import get_from_object
from bluer_objects import file
from bluer_objects import markdown
from bluer_objects.logger import logger

MY_NAME = module.name(__file__, MY_NAME)


def build(
    NAME: str,
    VERSION: str,
    REPO_NAME: str,
    items: List[str] = [],
    template_filename: str = "",
    filename: str = "",
    path: str = "",
    cols: int = 3,
    ICON: str = "",
    MODULE_NAME: str = "",
    macros: Dict[str, str] = {},
    help_function: Union[Callable[[List[str]], str], None] = None,
    legacy_mode: bool = True,
    assets_repo: str = "kamangir/assets",
) -> bool:
    if path:
        if path.endswith(".md"):
            filename = path
            template_filename = file.add_suffix(path, "template")
        else:
            filename = os.path.join(path, "README.md")
            template_filename = os.path.join(path, "template.md")

    if not MODULE_NAME:
        MODULE_NAME = REPO_NAME

    logger.info(
        "{}.build: {}-{}: {}[{}]: {} -{}> {}".format(
            MY_NAME,
            NAME,
            VERSION,
            REPO_NAME,
            MODULE_NAME,
            template_filename,
            "+legacy-" if legacy_mode else "",
            filename,
        )
    )

    table_of_items = markdown.generate_table(items, cols=cols) if cols > 0 else items

    signature = [
        "",
        " ".join(
            [
                f"[![pylint](https://github.com/kamangir/{REPO_NAME}/actions/workflows/pylint.yml/badge.svg)](https://github.com/kamangir/{REPO_NAME}/actions/workflows/pylint.yml)",
                f"[![pytest](https://github.com/kamangir/{REPO_NAME}/actions/workflows/pytest.yml/badge.svg)](https://github.com/kamangir/{REPO_NAME}/actions/workflows/pytest.yml)",
                f"[![bashtest](https://github.com/kamangir/{REPO_NAME}/actions/workflows/bashtest.yml/badge.svg)](https://github.com/kamangir/{REPO_NAME}/actions/workflows/bashtest.yml)",
                f"[![PyPI version](https://img.shields.io/pypi/v/{MODULE_NAME}.svg)](https://pypi.org/project/{MODULE_NAME}/)",
                f"[![PyPI - Downloads](https://img.shields.io/pypi/dd/{MODULE_NAME})](https://pypistats.org/packages/{MODULE_NAME})",
            ]
        ),
        "",
        "built by {} [`{}`]({}), based on {}[`{}-{}`]({}).".format(
            MY_ICON,
            "bluer README",
            "https://github.com/kamangir/bluer-objects/tree/main/bluer_objects/README",
            f"{ICON} " if ICON else "",
            NAME,
            VERSION,
            f"https://github.com/kamangir/{REPO_NAME}",
        ),
    ]

    success, template = file.load_text(template_filename)
    if not success:
        return success

    def apply_legacy(line: str) -> str:
        for before, after in {
            "yaml:::": "metadata:::",
            "--help--": "help:::",
            "--include": "include:::",
            "--table--": "items:::",
            "--signature--": "signature:::",
        }.items():
            line = line.replace(before, after)
        return line

    if legacy_mode:
        logger.info("applying legacy conversions...")
        template = [apply_legacy(line) for line in template]

    content: List[str] = []
    mermaid_started: bool = False
    variables: Dict[str, str] = {}
    for template_line in template:
        if template_line.startswith("ignore:::"):
            content_section = [template_line.split(":::", 1)[1].strip()]
        else:
            if template_line.startswith("set:::"):
                key, value = template_line.split("set:::", 1)[1].split(" ", 1)
                variables[key] = value
                logger.info(f":::{key} = {value}")
                continue

            for key, value in variables.items():
                template_line = template_line.replace(
                    f"get:::{key}",
                    value,
                )

            if "assets:::" in template_line:
                template_line = " ".join(
                    [
                        (
                            (
                                "![image](https://github.com/{}/blob/main/{}?raw=true)".format(
                                    assets_repo,
                                    token.split(":::")[1].strip(),
                                )
                                if any(
                                    token.endswith(extension)
                                    for extension in ["png", "jpg", "jpeg", "gif"]
                                )
                                else "[{}](https://github.com/{}/blob/main/{})".format(
                                    file.name_and_extension(
                                        token.split(":::")[1].strip()
                                    ),
                                    assets_repo,
                                    token.split(":::")[1].strip(),
                                )
                            )
                            if token.startswith("assets:::")
                            else token
                        )
                        for token in template_line.split(" ")
                    ]
                )

            if "object:::" in template_line:
                template_line = " ".join(
                    [
                        (
                            "[{}]({}/{}.tar.gz)".format(
                                token.split(":::")[1].strip(),
                                "TBA",
                                token.split(":::")[1].strip(),
                            )
                            if token.startswith("object:::")
                            else token
                        )
                        for token in template_line.split(" ")
                    ]
                )

            content_section: List[str] = [template_line]

            if template_line.startswith("details:::"):
                suffix = template_line.split(":::", 1)[1]
                if suffix:
                    content_section = [
                        "",
                        "<details>",
                        f"<summary>{suffix}</summary>",
                        "",
                    ]
                else:
                    content_section = [
                        "",
                        "</details>",
                        "",
                    ]
            elif template_line.startswith("metadata:::"):
                object_name_and_key = template_line.split(":::", 1)[1]
                if ":::" not in object_name_and_key:
                    object_name_and_key += ":::"
                object_name, key = object_name_and_key.split(":::", 1)

                value = get_from_object(
                    object_name,
                    key,
                    {},
                    download=True,
                )

                content_section = (
                    ["```yaml"]
                    + yaml.dump(
                        value,
                        default_flow_style=False,
                    ).split("\n")
                    + ["```"]
                )
            elif template_line.startswith("```mermaid"):
                mermaid_started = True
                logger.info("🧜🏽‍♀️  detected ...")
            elif mermaid_started and template_line.startswith("```"):
                mermaid_started = False
            elif mermaid_started:
                if '"' in template_line and ":::folder" not in template_line:
                    template_line_pieces = template_line.split('"')
                    if len(template_line_pieces) != 3:
                        logger.error(
                            f"🧜🏽‍♀️  mermaid line not in expected format: {template_line}."
                        )
                        return False

                    template_line_pieces[1] = (
                        template_line_pieces[1]
                        .replace("<", "&lt;")
                        .replace(">", "&gt;")
                        .replace(" ", "<br>")
                        .replace("~~", " ")
                    )

                    content_section = ['"'.join(template_line_pieces)]
            elif "items:::" in template_line:
                content_section = table_of_items
            elif "signature:::" in template_line:
                content_section = signature
            elif "include:::" in template_line:
                include_filename_relative = template_line.split(" ")[1].strip()
                include_filename = file.absolute(
                    include_filename_relative,
                    file.path(template_filename),
                )

                success, content_section = file.load_text(include_filename)
                if not success:
                    return success

                content_section = [
                    line for line in content_section if not line.startswith("used by:")
                ]

                include_title = (template_line.split(" ", 2) + ["", "", ""])[2]
                if include_title:
                    content_section = [f"## {include_title}"] + content_section[1:]

                if "include:::noref" not in template_line:
                    content_section += [
                        "using [{}]({}).".format(
                            file.name(include_filename),
                            include_filename_relative,
                        )
                    ]

                logger.info(f"{MY_NAME}.build: including {include_filename} ...")
            elif "help:::" in template_line:
                if help_function is not None:
                    help_command = template_line.split("help:::")[1].strip()

                    tokens = help_command.strip().split(" ")[1:]

                    help_content = help_function(tokens)
                    if not help_content:
                        logger.warning(f"help not found: {help_command}: {tokens}")
                        return False

                    logger.info(f"+= help: {help_command}")
                    print(help_content)
                    content_section = [
                        "```bash",
                        help_content,
                        "```",
                    ]
            else:
                for macro, macro_value in macros.items():
                    if macro in template_line:
                        content_section = macro_value
                        break

        content += content_section

    return file.save_text(filename, content)
