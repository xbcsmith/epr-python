# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: © 2024 Brett Smith <xbcsmith@gmail.com>
# SPDX-License-Identifier: Apache-2.0

import argparse
import logging
import os
import sys

from . import constants, create, errors, search
from .config import Config
from .models import Event, EventReceiver, EventReceiverGroup

debug = os.environ.get("EPR_DEBUG", False)
level = logging.INFO
if debug:
    sys.excepthook = errors.debug_except_hook
    level = logging.DEBUG
log_format = "%(asctime)s %(name)s:[%(levelname)s] %(message)s"
logging.basicConfig(stream=sys.stderr, level=level, format=log_format)
logger = logging.getLogger(__name__)


class CmdLine(object):
    def __init__(self):
        parser = argparse.ArgumentParser(
            description="EPR CLI",
            usage="""eprcli <command> [<args>]

            eprcli commands are:
                create      create Events, Event Receivers, and Event Receiver Groups
                search      search Events, Event Receivers, and Event Receiver Groups

            """,
        )

        parser.add_argument("command", help="Subcommand to run")
        # parse_args defaults to [1:] for args, but you need to
        # exclude the rest of the args too, or validation will fail
        args = parser.parse_args(sys.argv[1:2])
        if not hasattr(self, args.command):
            logger.error("Unrecognized command")
            parser.print_help()
            sys.exit(1)
        # use dispatch pattern to invoke method with same name
        getattr(self, args.command)()

    def create(self):
        """
        create Events, Event Receivers, and Event Receiver Groups
        """
        parser = argparse.ArgumentParser(description="create Events, Event Receivers, and Event Receiver Groups\n")
        parser.add_argument(
            "--token",
            dest="epr_api_token",
            action="store",
            help="EPR Access Token",
        )
        parser.add_argument(
            "--url",
            dest="epr_url",
            action="store",
            help="EPR Server URL",
        )
        parser.add_argument(
            "--jsonpath",
            dest="jsonpath_expr",
            action="store",
            help="Apply jsonpath to the results",
        )

        parser.add_argument(
            "--dry-run",
            dest="dryrun",
            action="store_true",
            default=False,
            help="Do not do anything",
        )
        parser.add_argument(
            "--debug",
            dest="debug",
            action="store_true",
            default=False,
            help="Turn debug on",
        )
        subparsers = parser.add_subparsers(dest="subparser_name", help="Sub-commands for create")
        event_parser = subparsers.add_parser("event", help="Event related options")
        event_parser.add_argument(
            "--name",
            dest="name",
            action="store",
            default=None,
            required=True,
            help="Name of the Event",
        )
        event_parser.add_argument(
            "--version",
            dest="version",
            action="store",
            default=None,
            required=True,
            help="Version of the Event",
        )
        event_parser.add_argument(
            "--release",
            dest="release",
            action="store",
            default=None,
            required=True,
            help="Release of the Event",
        )
        event_parser.add_argument(
            "--platform-id",
            dest="platform_id",
            action="store",
            default=None,
            required=True,
            help="Platform ID of the Event",
        )
        event_parser.add_argument(
            "--package",
            dest="package",
            action="store",
            default=None,
            required=True,
            help="Package of the Event",
        )
        event_parser.add_argument(
            "--description",
            dest="description",
            action="store",
            default=None,
            required=True,
            help="Description of the Event",
        )
        event_parser.add_argument(
            "--payload",
            dest="payload",
            action="store",
            default=None,
            required=True,
            help="Payload of the Event",
        )
        event_parser.add_argument(
            "--success",
            dest="success",
            action="store_true",
            default=False,
            required=False,
            help="Success of the Event",
        )
        event_parser.add_argument(
            "--event-receiver-id",
            dest="event_receiver_id",
            action="store",
            default=None,
            required=True,
            help="Event Receiver ID of the Event",
        )
        event_receiver_parser = subparsers.add_parser("event-receiver", help="Event Receiver related options")
        event_receiver_parser.add_argument(
            "--name",
            dest="name",
            action="store",
            default=None,
            required=True,
            help="Name of the Event Receiver",
        )
        event_receiver_parser.add_argument(
            "--type",
            dest="type",
            action="store",
            default=None,
            required=True,
            help="Type of the Event Receiver",
        )
        event_receiver_parser.add_argument(
            "--version",
            dest="version",
            action="store",
            default=None,
            required=True,
            help="Version of the Event Receiver",
        )
        event_receiver_parser.add_argument(
            "--description",
            dest="description",
            action="store",
            default=None,
            required=True,
            help="Description of the Event Receiver",
        )
        event_receiver_parser.add_argument(
            "--schema",
            dest="schema",
            action="store",
            default=None,
            required=True,
            help="Schema of the Event Receiver",
        )
        event_receiver_group_parser = subparsers.add_parser(
            "event-receiver-group", help="Event Receiver Group related options"
        )
        event_receiver_group_parser.add_argument(
            "--name",
            dest="name",
            action="store",
            default=None,
            required=True,
            help="Name of the Event Receiver Group",
        )
        event_receiver_group_parser.add_argument(
            "--type",
            dest="type",
            action="store",
            default=None,
            help="Type of the Event Receiver Group",
        )
        event_receiver_group_parser.add_argument(
            "--version",
            dest="version",
            action="store",
            default=None,
            required=True,
            help="Version of the Event Receiver Group",
        )
        event_receiver_group_parser.add_argument(
            "--description",
            dest="description",
            action="store",
            default=None,
            required=True,
            help="Description of the Event Receiver Group",
        )
        event_receiver_group_parser.add_argument(
            "--event-receiver-ids",
            dest="event_receiver_ids",
            action="store",
            default=None,
            required=True,
            help="Event Receiver IDs of the Event Receiver Group",
        )
        event_receiver_group_parser.add_argument(
            "--disable",
            dest="disable",
            action="store_true",
            default=False,
            help="Disable the Event Receiver Group",
        )
        args = vars(parser.parse_args(sys.argv[2:]))

        url = args["epr_url"]
        token = args["epr_api_token"]
        cfg = Config(url=url, token=token)

        cfg.debug = args["debug"]
        if args["subparser_name"] == "event":
            event = Event()
            event.name = args["name"]
            event.version = args["version"]
            event.release = args["release"]
            event.platform_id = args["platform_id"]
            event.package = args["package"]
            event.description = args["description"]
            event.payload = args["payload"]
            event.success = args["success"]
            event.event_receiver_id = args["event_receiver_id"]
            cfg.events.append(event)
        elif args["subparser_name"] == "event-receiver":
            event_receiver = EventReceiver()
            event_receiver.name = args["name"]
            event_receiver.type = args["type"]
            event_receiver.version = args["version"]
            event_receiver.description = args["description"]
            event_receiver.schema = args["schema"]
            cfg.event_receivers.append(event_receiver)
        elif args["subparser_name"] == "event-receiver-group":
            event_receiver_group = EventReceiverGroup()
            event_receiver_group.name = args["name"]
            event_receiver_group.type = args["type"]
            event_receiver_group.version = args["version"]
            event_receiver_group.description = args["description"]
            event_receiver_group.event_receiver_ids = [x.strip() for x in args["event_receiver_ids"].split(",")]
            event_receiver_group.enabled = True if not args["disable"] else False
            cfg.event_receiver_groups.append(event_receiver_group)
        return create.create(cfg)

    def search(self):
        """
        search Events, Event Receivers, and Event Receiver Groups
        """
        parser = argparse.ArgumentParser(description="search Events, Event Receivers, and Event Receiver Groups\n")
        parser.add_argument(
            "--token",
            dest="epr_api_token",
            action="store",
            help="EPR Access Token",
        )
        parser.add_argument(
            "--url",
            dest="epr_url",
            action="store",
            help="EPR Server URL",
        )
        parser.add_argument(
            "--jsonpath",
            dest="jsonpath_expr",
            action="store",
            help="Apply jsonpath to the results",
        )

        parser.add_argument(
            "--dry-run",
            dest="dryrun",
            action="store_true",
            default=False,
            help="Do not do anything",
        )
        parser.add_argument(
            "--debug",
            dest="debug",
            action="store_true",
            default=False,
            help="Turn debug on",
        )
        subparsers = parser.add_subparsers(dest="subparser_name", help="Sub-commands for create")
        event_parser = subparsers.add_parser("event", help="Event related options")
        event_parser.add_argument(
            "--id",
            dest="id",
            action="store",
            default=None,
            help="ID of the Event",
        )
        event_parser.add_argument(
            "--name",
            dest="name",
            action="store",
            default=None,
            help="Name of the Event",
        )
        event_parser.add_argument(
            "--version",
            dest="version",
            action="store",
            default=None,
            help="Version of the Event",
        )
        event_parser.add_argument(
            "--release",
            dest="release",
            action="store",
            default=None,
            help="Release of the Event",
        )
        event_parser.add_argument(
            "--platform-id",
            dest="platform_id",
            action="store",
            default=None,
            help="Platform ID of the Event",
        )
        event_parser.add_argument(
            "--package",
            dest="package",
            action="store",
            default=None,
            help="Package of the Event",
        )
        event_parser.add_argument(
            "--description",
            dest="description",
            action="store",
            default=None,
            help="Description of the Event",
        )
        event_parser.add_argument(
            "--payload",
            dest="payload",
            action="store",
            default=None,
            help="Payload of the Event",
        )
        event_parser.add_argument(
            "--success",
            dest="success",
            action="store",
            default=None,
            help="Success of the Event",
        )
        event_parser.add_argument(
            "--event-receiver-id",
            dest="event_receiver_id",
            action="store",
            default=None,
            help="Event Receiver ID of the Event",
        )
        event_parser.add_argument(
            "--fields",
            dest="fields",
            action="store",
            default=None,
            help="Fields to return of the Event (comma separated list)",
        )
        event_receiver_parser = subparsers.add_parser("event-receiver", help="Event Receiver related options")
        event_receiver_parser.add_argument(
            "--id",
            dest="id",
            action="store",
            default=None,
            help="ID of the Event Receiver",
        )
        event_receiver_parser.add_argument(
            "--name",
            dest="name",
            action="store",
            default=None,
            help="Name of the Event Receiver",
        )
        event_receiver_parser.add_argument(
            "--type",
            dest="type",
            action="store",
            default=None,
            help="Type of the Event Receiver",
        )
        event_receiver_parser.add_argument(
            "--version",
            dest="version",
            action="store",
            default=None,
            help="Version of the Event Receiver",
        )
        event_receiver_parser.add_argument(
            "--description",
            dest="description",
            action="store",
            default=None,
            help="Description of the Event Receiver",
        )
        event_receiver_parser.add_argument(
            "--schema",
            dest="schema",
            action="store",
            default=None,
            help="Schema of the Event Receiver",
        )
        event_receiver_parser.add_argument(
            "--fields",
            dest="fields",
            action="store",
            default=None,
            help="Fields to return of the Event Receiver (comma separated list)",
        )
        event_receiver_group_parser = subparsers.add_parser(
            "event-receiver-group", help="Event Receiver Group related options"
        )
        event_receiver_group_parser.add_argument(
            "--id",
            dest="id",
            action="store",
            default=None,
            help="ID of the Event Receiver Group",
        )
        event_receiver_group_parser.add_argument(
            "--name",
            dest="name",
            action="store",
            default=None,
            help="Name of the Event Receiver Group",
        )
        event_receiver_group_parser.add_argument(
            "--type",
            dest="type",
            action="store",
            default=None,
            help="Type of the Event Receiver Group",
        )
        event_receiver_group_parser.add_argument(
            "--version",
            dest="version",
            action="store",
            default=None,
            help="Version of the Event Receiver Group",
        )
        event_receiver_group_parser.add_argument(
            "--description",
            dest="description",
            action="store",
            default=None,
            help="Description of the Event Receiver Group",
        )
        event_receiver_group_parser.add_argument(
            "--event-receiver-ids",
            dest="event_receiver_ids",
            action="store",
            default=None,
            help="Event Receiver IDs of the Event Receiver Group",
        )
        event_receiver_group_parser.add_argument(
            "--enabled",
            dest="enabled",
            action="store",
            default=None,
            help="Enabled value of the Event Receiver Group",
        )
        event_receiver_group_parser.add_argument(
            "--fields",
            dest="fields",
            action="store",
            default=None,
            help="Fields to return of the Event Receiver Group (comma separated list)",
        )
        args = vars(parser.parse_args(sys.argv[2:]))
        url = args["epr_url"]
        token = args["epr_api_token"]
        cfg = Config(url=url, token=token)
        fields = [x.strip() for x in args["fields"].split(",") if x] if args["fields"] else None

        cfg.debug = args["debug"]
        if args["subparser_name"] == "event":
            event = Event()
            event.id = args["id"]
            event.name = args["name"]
            event.version = args["version"]
            event.release = args["release"]
            event.platform_id = args["platform_id"]
            event.package = args["package"]
            event.description = args["description"]
            event.payload = args["payload"]
            event.success = args["success"]
            event.event_receiver_id = args["event_receiver_id"]
            cfg.events.append(event)
            cfg.event_fields = fields
        elif args["subparser_name"] == "event-receiver":
            event_receiver = EventReceiver()
            event_receiver.id = args["id"]
            event_receiver.name = args["name"]
            event_receiver.type = args["type"]
            event_receiver.version = args["version"]
            event_receiver.description = args["description"]
            event_receiver.schema = args["schema"]
            cfg.event_receivers.append(event_receiver)
            cfg.event_receiver_fields = fields
        elif args["subparser_name"] == "event-receiver-group":
            event_receiver_group = EventReceiverGroup()
            event_receiver_group.id = args["id"]
            event_receiver_group.name = args["name"]
            event_receiver_group.type = args["type"]
            event_receiver_group.version = args["version"]
            event_receiver_group.description = args["description"]
            event_receiver_group.event_receiver_ids = args["event_receiver_ids"]
            cfg.event_receiver_groups.append(event_receiver_group)
            cfg.event_receiver_group_fields = fields
        return search.search(cfg)

    def version(self):
        """
        Prints version of eprcli
        """
        print(constants.info())


def main():
    CmdLine()


if __name__ == "__main__":
    sys.exit(main())
