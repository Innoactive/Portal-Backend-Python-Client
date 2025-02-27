import json
from argparse import ArgumentParser
from urllib.parse import urljoin

import requests

from portal_client.defaults import get_portal_backend_endpoint
from portal_client.organization import organization_parser
from portal_client.pagination import pagination_parser
from portal_client.portal_chunked_upload import ChunkedUploader
from portal_client.utils import get_authorization_header


def list_applications(**filters):
    applications_url = urljoin(get_portal_backend_endpoint(), "/api/v2/applications/")
    response = requests.get(
        applications_url,
        headers={"Authorization": get_authorization_header()},
        params=filters,
    )

    if not response.ok:
        print(response.json())
    response.raise_for_status()

    return response.json()


def list_applications_cli(args):
    applications_response = list_applications(
        organization=args.organization,
        page=args.page,
        page_size=args.page_size,
        fulltext_search=args.search,
    )

    print(json.dumps(applications_response))


def upload_application_build(application_archive, **application_build_data):
    application_url = urljoin(
        get_portal_backend_endpoint(), "/api/v2/application-builds/"
    )

    authorization_header = get_authorization_header()

    # upload chunked application
    uploader = ChunkedUploader(
        base_url=application_url, authorization_header=authorization_header
    )
    application_zip_url = uploader.upload_chunked_file(file_path=application_archive)
    application_build_data["application_archive"] = application_zip_url

    # publish application build data
    response = requests.post(
        application_url,
        headers={"Authorization": authorization_header},
        json=application_build_data,
    )
    if not response.ok:
        print(response.json())
    response.raise_for_status()

    return response.json()


def upload_application_build_cli(args):
    build_data = vars(args)
    del build_data["func"]
    application_build_upload_response = upload_application_build(**build_data)
    print(json.dumps(application_build_upload_response))


def configure_applications_v2_parser(parser: ArgumentParser):
    application_parser = parser.add_subparsers(
        description="List and manage applications on Portal"
    )

    applications_list_parser = application_parser.add_parser(
        "list",
        help="Returns a paginated list of applications on Portal",
        parents=[pagination_parser, organization_parser],
    )

    filters_group = applications_list_parser.add_argument_group(
        "filters", "Filtering Applications"
    )
    filters_group.add_argument(
        "--search",
        help="A search term (e.g. application name) to filter results by",
    )
    applications_list_parser.set_defaults(func=list_applications_cli)

    applications_upload_build_parser = application_parser.add_parser(
        "upload-build", help="Upload a build to an application"
    )
    applications_upload_build_parser.add_argument(
        "application_archive",
        help="Path to the application archive / package to be uploaded.",
    )
    applications_upload_build_parser.add_argument(
        "--app-id",
        "--application-id",
        help="ID of the application to upload the build to.",
        required=True,
        dest="application",
    )
    applications_upload_build_parser.add_argument(
        "--version", help="Semantic application build version.", required=True
    )
    applications_upload_build_parser.add_argument(
        "--target-platform",
        help="Target platform. ",
        default="windows",
        choices=["windows", "android"],
    )
    applications_upload_build_parser.add_argument(
        "--executable-path", help="Path to the applications executable."
    )
    applications_upload_build_parser.add_argument(
        "--package-name", help="Package name."
    )
    applications_upload_build_parser.add_argument(
        "--xr-platform",
        "--supported-xr-platform",
        help="XR Platforms supported by the application.",
        nargs="+",
        default=[],
        choices=["win-vr", "win-non-vr", "quest", "wave", "pico"],
        dest="supported_xr_platforms",
        action="extend",
    )
    applications_upload_build_parser.add_argument(
        "--supports-arbitrary-cli-args",
        help="Whether or not the build supports arbitary cli args. Disable this to not send Portal's default args to the app.",
        default=True,
    )
    applications_upload_build_parser.add_argument(
        "--launch-args",
        "--launch-arguments",
        help="Launch arguments to be passed to the application.",
        dest="launch_args",
        default="",
    )
    applications_upload_build_parser.add_argument(
        "--changelog",
        help="Changelog for the build. Supports markdown",
        dest="changelog",
        default="",
    )
    applications_upload_build_parser.set_defaults(func=upload_application_build_cli)

    return application_parser
