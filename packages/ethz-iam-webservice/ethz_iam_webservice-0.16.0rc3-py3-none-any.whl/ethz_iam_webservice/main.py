import json
import os
import sys
import signal
import time
from dataclasses import asdict
from datetime import datetime

import click
import yaml
from click.exceptions import ClickException

from requests import ConnectionError as ConnError

from .ethz_iam import ETH_IAM
from .user import UserAlternative
from .group import RecertificationPeriod, GroupAlternative
from .utils import gen_password

recertification_period_map = {
    "A": "Annual",
    "Y": "Annual",
    "Q": "Quarterly",
    "B": "Biennial",
    "N": "No recertification",
}


class Credentials(object):
    def __init__(self, username=None, password=None):
        self.username = username
        self.password = password


def handle_second_sigint(*_):
    click.echo("Script aborted.")
    sys.exit()


def handle_sigint(*_):
    click.echo(
        "Cannot abort operation, since the request was already sent to the IAM webservice. Hit CTRL-C during next 5 sec to abort the script anyway."
    )
    signal.signal(signal.SIGINT, handler=handle_second_sigint)
    time.sleep(5)
    click.echo("Resuming script...")
    signal.signal(signal.SIGINT, handler=handle_sigint)


pass_iam_credentials = click.make_pass_decorator(Credentials)


def _load_configuration(paths, filename=".ethz_iam_webservice"):
    if paths is None:
        paths = [os.path.expanduser("~")]

    # look in all config file paths
    # for configuration files and load them
    admin_accounts = []
    for path in paths:
        abs_filename = os.path.join(path, filename)
        if os.path.isfile(abs_filename):
            with open(abs_filename, "r", encoding="utf-8") as stream:
                try:
                    config = yaml.safe_load(stream)
                    for admin_account in config["admin_accounts"]:
                        admin_accounts.append(admin_account)
                except yaml.YAMLError as exc:
                    raise ClickException(exc) from exc

    return admin_accounts


def login(credentials: Credentials = None):
    if not credentials:
        # info about persons and groups
        # do not require credentials
        return ETH_IAM()
    if not credentials.username:
        credentials.username = click.prompt(
            text="IAM admin username",
            default=os.environ.get("USER", ""),
            show_default=True,
        )
    if not credentials.password:
        credentials.password = click.prompt(text="IAM admin password", hide_input=True)
    return ETH_IAM(
        credentials.username,
        credentials.password,
    )


@click.group()
@click.option(
    "-u",
    "--username",
    envvar="IAM_USERNAME",
    help="username of ETHZ IAM admin account or IAM_USERNAME env",
)
@click.option(
    "--password",
    envvar="IAM_PASSWORD",
    help="password of ETHZ IAM admin account or IAM_PASSWORD env",
)
@click.version_option(prog_name="IAM command line tool")
@click.pass_context
def cli(ctx, username, password=None):
    """ETHZ IAM command-line tool."""
    ctx.obj = Credentials(username, password)


@cli.command("users", help="search for users at ETH Zurich")
@click.option("-u", "--username", help="username")
@click.option("-m", "--mail", help="email address of a user")
@click.option("-f", "--firstname", help="firstname of a user")
@click.option("-l", "--lastname", help="lastname of a user")
@click.option("-n", "--uidnumber", help="uidNumber of a user")
def get_users(
    username,
    mail,
    firstname,
    lastname,
    uidnumber,
):
    if not (username or mail or firstname or lastname or uidnumber):
        ctx = click.get_current_context()
        click.echo(ctx.get_help())
        ctx.exit()
    user_alt = UserAlternative()
    users = user_alt.search_users(
        username=username,
        mail=mail,
        firstname=firstname,
        lastname=lastname,
        uidNumber=uidnumber,
    )
    click.echo(
        json.dumps(
            [asdict(person) for person in users],
            indent=4,
            sort_keys=True,
            ensure_ascii=False,
        )
    )

@cli.command("groups", help="search for groups at ETH Zurich (in LDAP only)")
@click.option("-u", "--username", help="Username that is member of a group")
@click.option("-n", "--group-name", help="Name of the group. Supports wildcards *")
@click.option("-g", "--gidnumber", help="gidNumber of the group")
@click.option(
    "-t", "--type", "type_", help="type of the group, e.g. custom, lz, realm, "
)
@click.option("-m", "--mail", help="email of a member of the group")
@click.option("-f", "--firstname", help="firstname of a member of the group")
@click.option("-l", "--lastname", help="lastname of a member of the group")
@click.option(
    "--member-details",
    is_flag=True,
    help="Show some details of every member in the groups",
)
@click.option(
    "-p",
    "--prop",
    multiple=True,
    help="define properties you want to display, e.g. -p cn -p members",
)
@click.option(
    "--no-members", is_flag=True, help="Only show the group infos, no group users"
)
# @pass_iam_credentials
def get_groups(
    # credentials,
    username,
    group_name,
    gidnumber,
    type_,
    mail,
    firstname,
    lastname,
    member_details,
    prop,
    no_members,
):
    if not (
        username
        or group_name
        or gidnumber
        or type_
        or mail
        or firstname
        or lastname
        or member_details
    ):
        ctx = click.get_current_context()
        click.echo(ctx.get_help())
        ctx.exit()
    if prop:
        if "members" not in prop:
            no_members = True
        for p in prop:
            valid_props = ("cn", "description", "gidNumber", "members", "type")
            if p not in valid_props:
                raise click.ClickException(
                    f"{p} is not a valid property. Valid properties are: {', '.join(valid_props)}"
                )

    group = GroupAlternative()
    groups = group.search_groups(
        group_name=group_name,
        member=username,
        gidnumber=gidnumber,
        group_type=type_,
        email=mail,
        firstname=firstname,
        lastname=lastname,
        member_details=member_details,
        no_members=no_members,
    )
    if prop:
        click.echo(
            json.dumps(
                [{p: getattr(group, p) for p in prop} for group in groups],
                indent=4,
                sort_keys=True,
                ensure_ascii=False,
            )
        )
    else:
        click.echo(
            json.dumps(
                [asdict(group) for group in groups],
                indent=4,
                sort_keys=True,
                ensure_ascii=False,
            )
        )


@cli.command("group", help="manage groups")
@click.argument("name")
@click.option(
    "--new-name",
    help="New name for this group (only used when renaming an existing group)",
)
@click.option(
    "-d",
    "--description",
    help="Description about this group.",
)
@click.option(
    "--agroup",
    "--ag",
    help="Admingroup for this group, mandatory for new a group",
)
@click.option(
    "-t",
    "--target",
    help="Add target system for this group. Can be used multiple times: -t AD -t LDAP",
    multiple=True,
)
@click.option(
    "--remove-target",
    "--rt",
    help="Remove target system for this group. Can be used multiple times.",
    multiple=True,
)
@click.option(
    "--organizational-unit",
    "--ou",
    help="OU (organizational unit) for this group, e.g. AGRL, USYS, INFK etc. where this group should be stored. If not specified, this group will appear in OU=Custom,OU=ETHLists",
)
@click.option(
    "--certification-period",
    "--cp",
    help="Define a certification period, whithin this group needs to be verified. [A]nnually, [B]iennial, [Q]uarterly, [N]one (default)",
)
@click.option(
    "--certification-note",
    "--cn",
    help="Reason (certification note) in case you don't want to periodically certify this group",
)
@click.option(
    "-m",
    "--manager",
    help="Username of the group manager for this group. Can appear multiple times. -m '' to remove all managers",
    multiple=True,
)
@click.option(
    "-a",
    "--add",
    help="Add username as member to group. Can be used multiple times: -a user1 -a user2",
    multiple=True,
)
@click.option(
    "-r",
    "--remove",
    help="Remove username as member to group. Can be used multiple times: -r user1 -r user2",
    multiple=True,
)
@click.option(
    "--add-subgroup",
    "--as",
    help="Add subgroup as member to group. Can be used multiple times.",
    multiple=True,
)
@click.option(
    "--remove-subgroup",
    "--rs",
    help="Remove subgroup as member from group. Can be used multiple times.",
    multiple=True,
)
@click.option("--new", "-n", is_flag=True, help="Create a group")
@click.option("--update", is_flag=True, help="Update a group")
@click.option("--recertify", is_flag=True, help="Recertify a group")
@click.option("--delete", is_flag=True, help="Delete a group")
@pass_iam_credentials
def manage_group(
    credentials,
    name,
    new_name=None,
    description=None,
    agroup=None,
    target=None,
    remove_target=None,
    organizational_unit=None,
    certification_period=None,
    certification_note="No recertification needed",
    manager=None,
    add=None,
    remove=None,
    add_subgroup=None,
    remove_subgroup=None,
    new=False,
    update=False,
    recertify=False,
    delete=False,
):
    """manage groups
    Name of the group must start with the admingroup's nickname,
    followed by a dash, e.g. agrl-xxxx
    """
    iam = login(credentials)

    def get_group(name):
        try:
            group = iam.get_group(name)
        except ValueError as exc:
            raise ClickException(
                f"{exc}. No group found with name {name}. Use --new if you want to create a new group."
            ) from exc
        except ConnError as exc:
            raise ClickException(exc) from exc
        return group

    group = iam.group
    group.name = name

    if certification_period:
        if certification_period.upper() not in recertification_period_map:
            raise ClickException(
                "Please specify [A]nnual, [B]iennial, [Q]uarterly or [N]o recertification period."
            )
        certification_period = recertification_period_map[certification_period.upper()]

    signal.signal(signal.SIGINT, handler=handle_sigint)
    if new:
        if certification_period is None:
            certification_period = RecertificationPeriod.NONE.value
        if not agroup:
            raise ClickException("Please provide an admingroup with --agroup")
        if not description:
            raise ClickException(
                "Description of the group is missing. Use -d 'some description'"
            )
        try:
            group = iam.new_group(
                name=name,
                description=description,
                admingroup=agroup,
                targets=[t.upper() for t in target],
                group_ad_ou=organizational_unit,
                certification_period=certification_period,
                certification_note=certification_note,
                managers=manager,
            )
        except ValueError as exc:
            raise ClickException(exc) from exc
        except ConnError as exc:
            raise ClickException(
                f"Cannot connect to IAM webservice at {exc.request.url}"
            ) from exc
    elif delete:
        group.delete()
        click.echo(f"Successfully deleted group {name}")
        return
    elif recertify:
        group.recertify()
        click.echo(f"Group {name} successfully recertified.")
    elif update:
        try:
            new_group = group.update(
                current_name=name,
                new_name=new_name,
                description=description,
                group_ad_ou=organizational_unit,
                certification_period=certification_period,
                certification_note=certification_note,
                managers=list(manager),
            )
            group = new_group if new_group else group
        except ValueError as exc:
            raise ClickException(exc) from exc

    if add or add_subgroup:
        group.add_members(users=add, subgroups=add_subgroup)
    if remove or remove_subgroup:
        group.remove_members(users=remove, subgroups=remove_subgroup)
    if target and not new:
        targets = [t.upper() for t in target]
        try:
            group.set_targets(targets)
        except ValueError as exc:
            if "already present" in str(exc):
                pass
            else:
                raise ClickException(exc) from exc
    if remove_target:
        targets = [t.upper() for t in remove_target]
        try:
            group.remove_targets(targets)
        except ValueError as exc:
            if "already not present" in str(exc):
                pass
            else:
                raise ClickException(exc) from exc
    if not group.mod_date:
        group = get_group(name=name)

    click.echo(json.dumps(asdict(group), indent=4, sort_keys=True, ensure_ascii=False))


@cli.group("guest", help="manage guests")
def guest_group():
    pass


@cli.command("guests", help="search for guests")
@click.option("-l", "--leitzahl", help="Leitzahl of the host organization")
@click.option("-h", "--host", help="username of the guest host")
@click.option("-a", "--admingroup", help="responsible admin group of the guest")
@click.option("--ends-in-days", help="search for guests that end in this many days", type=int)
@click.option("-c", "--contact", help="email address of the technical contact")
@pass_iam_credentials
def search_guests(credentials, leitzahl, host, admingroup, ends_in_days, contact):
    """Search for guests at ETH Zurich.
    """

    iam = login(credentials)
    if not (leitzahl or host or admingroup):
        ctx = click.get_current_context()
        click.echo(ctx.get_help())
        ctx.exit()

    guests = iam.guest.search_guests(host_leitzahl=leitzahl, host_username=host, host_admingroup=admingroup)
    if ends_in_days:
        guests = [guest for guest in guests if guest.end_date and (guests[0].end_date - datetime.today().date()).days <= ends_in_days]
    if contact:
        guests = [guest for guest in guests if guest.technical_contact and contact.lower() == guest.technical_contact.lower()]

    click.echo(
        json.dumps(
            [asdict(guest) for guest in guests],
            # convert datetime objects to string
            default=str,
            indent=4,
            sort_keys=True,
            ensure_ascii=False
        )
    )

@guest_group.command("get", help="get an existing guest")
@click.argument("username")
@pass_iam_credentials
def get_guest(credentials, username):
    iam = login(credentials)
    try:
        guest = iam.get_guest(username)
    except ConnError as exc:
        raise ClickException(
            f"Cannot connect to IAM webservice at {exc.request.url}"
        ) from exc
    except ValueError as exc:
        raise ClickException(f"No such guest: {username}") from exc
    click.echo(json.dumps(asdict(guest), default=str, indent=4, sort_keys=True, ensure_ascii=False))


@guest_group.command(
    "extend", help="extend validation of an existing guest. Default is today+1 year."
)
@click.option(
    "-e", "--end-date", help="specify end date of guest (YYYY-MM-DD or DD.MM.YYYY)."
)
@click.option(
    "-m", "--months", help="extend validation of an existing guest by this many months."
)
@click.argument("username")
@pass_iam_credentials
def extend_guest(credentials, end_date, months, username):
    iam = login(credentials)
    try:
        guest = iam.extend_guest(username=username, end_date=end_date, months=months)
        click.echo(json.dumps(guest.data, indent=4, sort_keys=True, ensure_ascii=False))
    except Exception as exc:
        raise ClickException(exc) from exc


@click.option("-d", "--description", help="")
@click.option("-m", "--mail", required=True, help="email address")
@click.option("-h", "--host-username", help="ETHZ Username of host")
@click.option(
    "-a",
    "--host-admingroup",
    help="Name of the admin group this guest should be connected to. Default: same as the technical user which is creating this guest.",
)
@click.option(
    "-o",
    "--host-leitzahl",
    help="Leitzahl of host organization, see http://www.org.ethz.ch. Default: Leitzahl of the host.",
)
@click.option(
    "-c",
    "--technical-contact",
    help="email address of technical contact. Default: email of the host of this guest.",
)
@click.option(
    "-n",
    "--notification",
    help="g=guest, h=host, t=technical contact. Use any combination of the 3 chars. Defaults to «gh»",
)
@click.option(
    "-e", "--end-date", help="End date of guest (YYYY-MM-DD). Default: today+1 year"
)
@click.option(
    "--deactivation-start-date",
    help='Deactivation start date of guest (YYYY-DD-MM). Set it to "" to remove',
)
@click.option(
    "--deactivation-end-date",
    help='Deactivation end date of guest (YYYY-MM-DD). Set it to "" to remove',
)
@guest_group.command("update", help="update an existing guest")
@click.argument("username")
@pass_iam_credentials
def update_guest(
    credentials,
    description,
    mail,
    host_leitzahl,
    host_username,
    technical_contact,
    host_admingroup,
    notification,
    end_date,
    username,
    deactivation_start_date,
    deactivation_end_date,
):
    iam = login(credentials)
    try:
        signal.signal(signal.SIGINT, handler=handle_sigint)
        guest = iam.update_guest(
            username=username,
            mail=mail,
            host_username=host_username,
            host_admingroup=host_admingroup,
            description=description,
            technical_contact=technical_contact,
            notification=notification,
            host_leitzahl=host_leitzahl,
            end_date=end_date,
            deactivation_start_date=deactivation_start_date,
            deactivation_end_date=deactivation_end_date,
        )
        click.echo(json.dumps(guest.data, indent=4, sort_keys=True, ensure_ascii=False))
    except ConnError as exc:
        raise ClickException(
            f"Cannot connect to IAM webservice at {exc.request.url}"
        ) from exc


@guest_group.command("delete", help="delete an existing guest")
@click.argument("username")
@pass_iam_credentials
def delete_guest(
    credentials,
    username,
):
    iam = login(credentials)
    try:
        signal.signal(signal.SIGINT, handler=handle_sigint)
        iam.delete_guest(username=username)
        click.echo(f"Guest {username} successfully deleted.")
    except ConnError as exc:
        raise ClickException(
            f"Cannot connect to IAM webservice at {exc.request.url}"
        ) from exc


@guest_group.command("new", help="create a new guest")
@click.option("-f", "--firstname", required=True, help="given name")
@click.option("-l", "--lastname", required=True, help="surname")
@click.option("-m", "--mail", required=True, help="email address")
@click.option("-d", "--description", required=True, help="")
@click.option("-h", "--host-username", required=True, help="ETHZ Username of host")
@click.option(
    "-a",
    "--host-admingroup",
    required=True,
    help="Name of the administrative group that hosts this guest.",
)
@click.option(
    "-o",
    "--host-leitzahl",
    help="Leitzahl of host organization, see http://www.org.ethz.ch. If not provided, the leitzahl of the host will be used.",
)
@click.option(
    "-c",
    "--technical-contact",
    help="email address of technical contact. If not provided, the email address of the host will be used.",
)
@click.option(
    "-b",
    "--birth-date",
    help="birthdate in YYYY-MM-DD format. Default: Today's date + year 2000",
)
@click.option(
    "-n",
    "--notification",
    default="gh",
    help="g=guest, h=host, t=technical contact. Use any combination of the 3 chars. ",
)
@click.option(
    "-s", "--start-date", help="Start date of guest (YYYY-DD-MM). Default: today"
)
@click.option(
    "-e", "--end-date", help="End date of guest (YYYY-MM-DD). Default: today+1 year"
)
@click.option(
    "--init-password",
    is_flag=True,
    help="Set initial password and return it in cleartext",
)
@click.option(
    "--ignore-existing-email",
    is_flag=True,
    help="Ignore the few cases where users with the same email address already exists (usually Empa users)",
)
@pass_iam_credentials
def new_guest(
    credentials,
    firstname,
    lastname,
    mail,
    description,
    birth_date,
    host_leitzahl,
    host_username,
    technical_contact,
    host_admingroup,
    notification,
    start_date,
    end_date,
    init_password,
    ignore_existing_email,
):
    iam = login(credentials)
    try:
        if not ignore_existing_email:
            persons = iam.search_users(mail=mail)
            if persons:
                raise ClickException(
                    f"Account(s) with same email address already exists: {','.join([person['uid'] for person in persons])}"
                )
        signal.signal(signal.SIGINT, handler=handle_sigint)
        guest = iam.new_guest(
            firstname=firstname,
            lastname=lastname,
            mail=mail,
            birth_date=birth_date,
            host_username=host_username,
            host_admingroup=host_admingroup,
            description=description,
            technical_contact=technical_contact,
            notification=notification,
            host_leitzahl=host_leitzahl,
            start_date=start_date,
            end_date=end_date,
        )
    except ConnError as exc:
        raise ClickException(
            f"Cannot connect to IAM webservice at {exc.request.url}"
        ) from exc
    except ValueError as exc:
        raise ClickException(exc) from exc

    ldap_password = gen_password()
    vpn_password = gen_password()
    guest_data = guest.data

    if not guest.username:
        raise ClickException(
            "could not set inital password for the guest because the guest has no username."
        )

    if init_password:
        guest_user = iam.get_user(guest.username)
        try:
            guest_user.set_password(password=ldap_password, service_name="LDAP")
            guest_data["init_ldap_password"] = ldap_password
        except Exception as exc:
            print(exc)

        try:
            guest_user.set_password(password=vpn_password, service_name="VPN")
            guest_data["init_vpn_password"] = vpn_password
        except Exception as exc:
            print(exc)

    click.echo(json.dumps(guest_data, indent=4, sort_keys=True, ensure_ascii=False))


@cli.command("user", help="manage IAM users")
@click.argument("username")
@click.option("-r", "--show-relations", is_flag=True, help="show relations of this user")
@click.option("-p", "--show-personas", is_flag=True, help="show personas of this user")
@click.option("-d", "--delete", is_flag=True, help="delete this user")
@pass_iam_credentials
def get_user(
    credentials,
    show_relations,
    show_personas,
    username,
    delete,
):
    iam = login(credentials)

    try:
        user = iam.get_user(username)
    except ValueError as exc:
        raise ClickException(f"No such user: {username}.") from exc
    
    if show_personas:
        user.get_personas()

    if show_relations:
        user.get_relations()

    if delete:
        click.confirm("Do you really want to delete this user?", abort=True)
        user.delete()

    print(json.dumps(asdict(user), default=str, indent=4, sort_keys=True, ensure_ascii=False))


@cli.command("service", help="manage services of IAM users")
@click.argument("username")
@click.option(
    "-s",
    "--service",
    multiple=True,
    help="specify the service you want to manage, e.g. AD, LDAPS, VPN.",
)
@click.option(
    "-g",
    "--grant-service",
    multiple=True,
    help="grant a service to this user, e.g. AD, LDAPS, VPN. Use this option for every service you want to grant",
)
@click.option(
    "-r",
    "--revoke-service",
    multiple=True,
    help="revoke a service from this user, e.g. AD, LDAPS, VPN. Use this option for every service you want to revoke",
)
@click.option(
    "-p",
    "--service-password",
    help="set a password for the given service. Use the --service option to specify the service.",
)
@pass_iam_credentials
def manage_service(
    credentials,
    username,
    service=None,
    grant_service=None,
    revoke_service=None,
    service_password=None,
):
    iam = login(credentials)

    if grant_service:

        for service_name in grant_service:
            try:
                service_name = iam.grant_service(username, service_name)
            except ValueError as exc:
                raise click.ClickException(exc)
            service_info = {"services": service_info}
            click.echo(
                json.dumps(
                    service_info,
                    indent=4,
                    sort_keys=True,
                    ensure_ascii=False
                )
            )

    elif revoke_service:
        for service_name in revoke_service:
            try:
                iam.revoke_service(username, service_name)
            except ValueError as exc:
                raise click.ClickException(exc)
    else:
        # display all services of this user 
        services = iam.get_services(username)
        click.echo(json.dumps(services, indent=4, sort_keys=True, ensure_ascii=False))


if __name__ == "__main__":
    cli()
