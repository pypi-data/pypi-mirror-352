from secrets_safe_library import exceptions, managed_account, smart_rules
from secrets_safe_library.constants.endpoints import (
    GET_MANAGED_ACCOUNTS_ID,
    GET_MANAGED_SYSTEMS_SYSTEM_ID_MANAGED_ACCOUNTS,
)
from secrets_safe_library.constants.versions import Version
from secrets_safe_library.mapping.managed_accounts import (
    fields as managed_account_fields,
)

from ps_cli.core.controllers import CLIController
from ps_cli.core.decorators import aliases, command, option
from ps_cli.core.display import print_it


class ManagedAccount(CLIController):
    """
    Create, Delete, List, retrive, or print BeyondInsight ManagedAccounts that API user
    has rights to.

    Requires PasswordSafe Account Management (Read/Write, depending)
    """

    def __init__(self):
        super().__init__(
            name="managed-accounts",
            help="Managed accounts management commands",
        )

    _smart_rule_object: smart_rules.SmartRule | None = None

    @property
    def class_object(self) -> managed_account.ManagedAccount:
        if self._class_object is None and self.app is not None:
            self._class_object = managed_account.ManagedAccount(
                authentication=self.app.authentication, logger=self.log.logger
            )
        return self._class_object

    @property
    def smart_rule_object(self) -> smart_rules.SmartRule:
        if self._smart_rule_object is None and self.app is not None:
            self._smart_rule_object = smart_rules.SmartRule(
                authentication=self.app.authentication, logger=self.log.logger
            )
        return self._smart_rule_object

    @command
    @aliases("list")
    @option(
        "-id",
        "--managed-system-id",
        help="Managed System ID",
        type=int,
        required=True,
    )
    def list_managed_accounts(self, args):
        """
        Returns a list of managed accounts by managed system ID.
        """
        try:
            fields = self.get_fields(
                GET_MANAGED_SYSTEMS_SYSTEM_ID_MANAGED_ACCOUNTS,
                managed_account_fields,
                Version.DEFAULT,
            )
            self.display.v("Calling list_by_managed_system function")
            managed_accounts = self.class_object.list_by_managed_system(
                managed_system_id=args.managed_system_id
            )
            self.display.show(managed_accounts, fields)
        except exceptions.LookupError as e:
            self.display.v(e)
            self.log.error(e)
            print_it("It was not possible to list managed accounts")

    @command
    @aliases("get")
    @option(
        "-id",
        "--account-id",
        help="To get a managed account by ID",
        type=int,
        required=False,
    )
    @option(
        "-an",
        "--account-name",
        help="To get a managed account by name and managed system name",
        type=str,
        required=False,
    )
    @option(
        "-sn",
        "--system-name",
        help="To get a managed account by name and managed system name",
        type=str,
        required=False,
    )
    def get_managed_account(self, args):
        """
        Returns a managed account by ID or a list when searching by Account and
        System's name.
        """
        try:
            fields = self.get_fields(
                GET_MANAGED_ACCOUNTS_ID, managed_account_fields, Version.DEFAULT
            )

            if args.account_id:
                self.display.v("Searching directly by account ID")
                managed_account = self.class_object.get_by_id(
                    managed_account_id=args.account_id
                )
                self.display.show(managed_account, fields)
            elif args.account_name and args.system_name:
                self.display.v("Searching by account and system's name")
                managed_accounts = self.class_object.get_managed_accounts(
                    account_name=args.account_name,
                    system_name=args.system_name,
                )

                if isinstance(managed_accounts, dict):
                    # If a single account is returned, wrap it in a list
                    # to maintain consistency with how multiple accounts are handled
                    managed_accounts = [managed_accounts]

                managed_account_list = [
                    account
                    for account in managed_accounts
                    if account.get("AccountName") == args.account_name
                ]
                self.display.show(managed_account_list, fields)
            else:
                print_it(
                    "You must provide either an account ID or both an account name and "
                    "a system name"
                )
        except exceptions.LookupError as e:
            self.display.v(e)
            self.log.error(e)
            if args.account_id:
                print_it(
                    "It was not possible to get a managed account for ID: "
                    f"{args.account_id}"
                )
            else:
                print_it(
                    "It was not possible to get a managed account for Account Name: "
                    f"{args.account_name} and System Name: {args.system_name}"
                )

    @command
    @aliases("list-by-smart-rule", "list-by-sr")
    @option(
        "-id",
        "--smart-rule-id",
        help="To list managed accounts by Smart Rule ID",
        type=int,
        required=False,
    )
    @option(
        "-t",
        "--smart-rule-title",
        help="To list managed accounts by Smart Rule Title",
        type=str,
        required=False,
    )
    def list_managed_accounts_by_smart_rule(self, args):
        """
        List managed accounts by Smart Rule's ID or Title.
        """
        try:
            fields = self.get_fields(
                GET_MANAGED_ACCOUNTS_ID, managed_account_fields, Version.DEFAULT
            )
            if args.smart_rule_id:
                self.display.v(f"Searching by Smart Rule ID {args.smart_rule_id}")
                managed_accounts = self.class_object.list_by_smart_rule_id(
                    smart_rule_id=args.smart_rule_id
                )
            elif args.smart_rule_title:
                self.display.v(f"Searching by Smart Rule Name {args.smart_rule_title}")
                smart_rule = self.smart_rule_object.get_smart_rule_by_title(
                    title=args.smart_rule_title
                )

                if not smart_rule:
                    print_it(
                        f"Smart Rule with title {args.smart_rule_title} not found."
                    )
                    return

                managed_accounts = self.class_object.list_by_smart_rule_id(
                    smart_rule_id=smart_rule.get("SmartRuleID")
                )
            else:
                print_it("You must provide either a Smart Rule ID or a Smart Rule Name")
                return
            self.display.show(managed_accounts, fields)
        except exceptions.LookupError as e:
            self.display.v(e)
            self.log.error(e)
            if args.smart_rule_id:
                print_it(
                    "It was not possible to get a managed account for Smart Rule ID: "
                    f"{args.smart_rule_id}"
                )
            else:
                print_it(
                    "It was not possible to get a managed account for Smart Rule "
                    f"Title: {args.smart_rule_title}"
                )

    @command
    @aliases("list-by-quick-rule", "list-by-qr")
    @option(
        "-id",
        "--quick-rule-id",
        help="To list managed accounts by Quick Rule ID",
        type=int,
        required=False,
    )
    @option(
        "-t",
        "--quick-rule-title",
        help="To list managed accounts by Quick Rule Title",
        type=str,
        required=False,
    )
    def list_managed_accounts_by_quick_rule(self, args):
        """
        List managed accounts by Quick Rule's ID or Title.
        """
        try:
            fields = self.get_fields(
                GET_MANAGED_ACCOUNTS_ID, managed_account_fields, Version.DEFAULT
            )
            if args.quick_rule_id:
                self.display.v(f"Searching by Quick Rule ID {args.quick_rule_id}")
                managed_accounts = self.class_object.list_by_quick_rule_id(
                    quick_rule_id=args.quick_rule_id
                )
            elif args.quick_rule_title:
                self.display.v(f"Searching by Quick Rule Name {args.quick_rule_title}")
                quick_rule = self.smart_rule_object.get_quick_rule_by_title(
                    title=args.quick_rule_title
                )

                if not quick_rule:
                    print_it(
                        f"Quick Rule with title {args.quick_rule_title} not found."
                    )
                    return

                managed_accounts = self.class_object.list_by_quick_rule_id(
                    quick_rule_id=quick_rule.get("SmartRuleID")
                )
            else:
                print_it("You must provide either a Quick Rule ID or a Quick Rule Name")
                return
            self.display.show(managed_accounts, fields)
        except exceptions.LookupError as e:
            self.display.v(e)
            self.log.error(e)
            if args.quick_rule_id:
                print_it(
                    "It was not possible to get a managed account for Quick Rule ID: "
                    f"{args.quick_rule_id}"
                )
            else:
                print_it(
                    "It was not possible to get a managed account for Quick Rule "
                    f"Title: {args.quick_rule_title}"
                )
