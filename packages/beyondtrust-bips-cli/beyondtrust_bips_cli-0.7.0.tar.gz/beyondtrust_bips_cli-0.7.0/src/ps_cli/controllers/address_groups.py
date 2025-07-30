from secrets_safe_library import address_groups, exceptions
from secrets_safe_library.constants.endpoints import (
    GET_ADDRESS_GROUPS,
    GET_ADDRESS_GROUPS_ID,
)
from secrets_safe_library.constants.versions import Version
from secrets_safe_library.mapping.address_groups import fields as address_group_fields

from ps_cli.core.controllers import CLIController
from ps_cli.core.decorators import aliases, command, option
from ps_cli.core.display import print_it


class AddressGroup(CLIController):
    """
    BeyondInsight Address Groups functionalities.
    """

    def __init__(self):
        super().__init__(
            name="address-groups",
            help="Address groups management commands",
        )

    @property
    def class_object(self) -> address_groups.AddressGroup:
        if self._class_object is None and self.app is not None:
            self._class_object = address_groups.AddressGroup(
                authentication=self.app.authentication, logger=self.log.logger
            )
        return self._class_object

    @command
    @aliases("list")
    def list_address_groups(self, args):
        """
        List the address groups.
        """
        try:
            fields = self.get_fields(
                GET_ADDRESS_GROUPS, address_group_fields, Version.DEFAULT
            )
            self.display.v("Calling list_address_groups function")
            safes = self.class_object.list_address_groups()
            self.display.show(safes, fields)
        except exceptions.LookupError as e:
            self.display.v(e)
            self.log.error(e)
            print_it("It was not possible to list address groups")

    @command
    @aliases("get")
    @option(
        "-n",
        "--name",
        help="The Address Group name",
        type=str,
        required=False,
    )
    @option(
        "-id",
        "--address-group-id",
        help="The Address Group id",
        type=int,
        required=False,
    )
    def get_address_group(self, args):
        """
        Returns an Address Group by name or ID.
        """
        try:
            if args.address_group_id:
                self.display.v("Calling get_address_group_by_id function")
                address_group = self.class_object.get_address_group_by_id(
                    args.address_group_id
                )
            elif args.name:
                self.display.v("Calling get_address_group_by_name function")
                address_group = self.class_object.get_address_group_by_name(args.name)
            else:
                print_it("You must provide either a name or an ID")
                return

            fields = self.get_fields(
                GET_ADDRESS_GROUPS_ID, address_group_fields, Version.DEFAULT
            )
            self.display.show(address_group, fields)
        except exceptions.LookupError as e:
            self.display.v(e)
            self.log.error(e)
            if args.address_group_id:
                print_it(
                    f"It was not possible to get an address group by ID: "
                    f"{args.address_group_id}"
                )
            else:
                print_it(
                    f"It was not possible to get address group by name: {args.name}"
                )
