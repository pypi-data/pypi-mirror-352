"""
BIPS CLI Entrypoint
"""

from ps_cli.controllers import (
    AddressGroup,
    Asset,
    Database,
    Entitlement,
    EntityType,
    Folder,
    ManagedAccount,
    ManagedSystem,
    Organization,
    Safe,
    Secret,
    Settings,
    User,
    Workgroup,
)
from ps_cli.core.app import App


def main() -> None:
    controllers = [
        AddressGroup,
        Safe,
        Folder,
        Secret,
        ManagedAccount,
        ManagedSystem,
        Workgroup,
        User,
        Database,
        Organization,
        Settings,
        Asset,
        Entitlement,
        EntityType,
    ]

    app = App(controllers=controllers)
    app.run()


if __name__ == "__main__":
    main()
