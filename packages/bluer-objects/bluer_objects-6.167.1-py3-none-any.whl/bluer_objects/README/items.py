from typing import List, Dict


# name, url, marquee, description
def Items(
    items: List[Dict[str, str]],
) -> List[str]:
    return [
        (
            "[`{}`]({}) [![image]({})]({}) {}".format(
                item["name"],
                item.get(
                    "url",
                    "#",
                ),
                item.get(
                    "marquee",
                    "https://github.com/kamangir/assets/raw/main/blue-plugin/marquee.png?raw=true",
                ),
                item.get(
                    "url",
                    "#",
                ),
                item.get("description", ""),
            )
            if "name" in item
            else ""
        )
        for item in items
    ]
