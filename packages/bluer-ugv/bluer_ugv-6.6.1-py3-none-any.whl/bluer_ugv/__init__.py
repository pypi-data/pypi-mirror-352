NAME = "bluer_ugv"

ICON = "🐬"

DESCRIPTION = f"{ICON} AI x ROS."

VERSION = "6.6.1"

REPO_NAME = "bluer-ugv"

MARQUEE = (
    "https://github.com/waveshareteam/ugv_rpi/raw/main/media/UGV-Rover-details-23.jpg"
)

ALIAS = "@ugv"


def fullname() -> str:
    return f"{NAME}-{VERSION}"
