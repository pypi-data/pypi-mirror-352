import os

from bluer_objects import file, README

from bluer_ugv import NAME, VERSION, ICON, REPO_NAME


items = README.Items(
    [
        {
            "name": "bluer-beast",
            "marquee": "https://github.com/waveshareteam/ugv_rpi/raw/main/media/UGV-Rover-details-23.jpg",
            "description": "based on [UGV Beast PI ROS2](https://www.waveshare.com/wiki/UGV_Beast_PI_ROS2).",
            "url": "./bluer_ugv/docs/bluer-beast.md",
        },
        {
            "name": "bluer-fire",
            "description": "based on a used car.",
            "url": "./bluer_ugv/docs/bluer-fire.md",
        },
        {
            "name": "bluer-light",
            "description": "based on power wheels.",
            "url": "./bluer_ugv/docs/bluer-light.md",
        },
    ]
)


def build():
    return all(
        README.build(
            items=readme.get("items", []),
            path=os.path.join(file.path(__file__), readme["path"]),
            ICON=ICON,
            NAME=NAME,
            VERSION=VERSION,
            REPO_NAME=REPO_NAME,
        )
        for readme in [
            {
                "items": items,
                "path": "..",
            },
            {"path": "docs/bluer-beast.md"},
            {"path": "docs/bluer-fire.md"},
            {"path": "docs/bluer-light.md"},
        ]
    )
