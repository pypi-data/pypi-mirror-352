#!/usr/bin/env python3

# Standard libraries
from argparse import (
    _ArgumentGroup,
    _MutuallyExclusiveGroup,
    ArgumentParser,
    Namespace,
    RawTextHelpFormatter,
)
from os import environ
from shutil import get_terminal_size
from sys import exit as sys_exit

# Components
from ..package.bundle import Bundle
from ..package.settings import Settings
from ..package.updates import Updates
from ..package.version import Version
from ..prints.colors import Colors
from ..system.platform import Platform
from ..types.environments import Environments
from ..types.gitlab import (
    MergeRequestsMethod,
    MergeRequestsPipelines,
    MergeRequestsResolved,
    MergeRequestsSkipped,
    MergeRequestsSquash,
    ProtectionLevels,
    RolesCreateProjects,
    RolesCreateSubgroups,
)
from .entrypoint import Entrypoint

# Constants
HELP_POSITION: int = 39

# Exception
def exception(error: BaseException) -> None:
    raise error

# Main, pylint: disable=too-many-branches,too-many-statements
def main() -> None:

    # Variables
    environments: Environments
    group: _ArgumentGroup
    result: Entrypoint.Result = Entrypoint.Result.ERROR
    subgroup: _MutuallyExclusiveGroup

    # Configure environment variables
    environments = Environments()
    environments.group = 'environment variables'
    environments.add(
        'gitlab_token',
        Bundle.ENV_GITLAB_TOKEN,
        'GitLab API token environment variable',
    )
    environments.add(
        'ci_job_token',
        Bundle.ENV_CI_JOB_TOKEN,
        'GitLab CI job token environment variable (CI only)',
    )

    # Arguments creation
    parser: ArgumentParser = ArgumentParser(
        prog=Bundle.NAME,
        description=f'{Bundle.NAME}: {Bundle.DESCRIPTION}',
        epilog=environments.help(HELP_POSITION),
        add_help=False,
        formatter_class=lambda prog: RawTextHelpFormatter(
            prog,
            max_help_position=HELP_POSITION,
            width=min(
                120,
                get_terminal_size().columns - 2,
            ),
        ),
    )

    # Arguments internal definitions
    group = parser.add_argument_group('internal arguments')
    group.add_argument(
        '-h',
        '--help',
        dest='help',
        action='store_true',
        help='Show this help message',
    )
    group.add_argument(
        '--version',
        dest='version',
        action='store_true',
        help='Show the current version',
    )
    group.add_argument(
        '--no-color',
        dest='no_color',
        action='store_true',
        help=f'Disable colors outputs with \'{Bundle.ENV_NO_COLOR}=1\'\n'
        '(or default settings: [themes] > no_color)',
    )
    group.add_argument(
        '--update-check',
        dest='update_check',
        action='store_true',
        help='Check for newer package updates',
    )
    group.add_argument(
        '--settings',
        dest='settings',
        action='store_true',
        help='Show the current settings path and contents',
    )
    group.add_argument(
        '--set',
        dest='set',
        action='store',
        metavar=('GROUP', 'KEY', 'VAL'),
        nargs=3,
        help='Set settings specific \'VAL\' value to [GROUP] > KEY\n' \
             'or unset by using \'UNSET\' as \'VAL\'',
    )

    # Arguments credentials definitions
    group = parser.add_argument_group('credentials arguments')
    group.add_argument(
        '-c',
        '--config',
        dest='configs',
        action='append',
        metavar='FILES',
        help=f'Python GitLab configuration files'
        f' (default: {Bundle.ENV_PYTHON_GITLAB_CFG} environment)',
    )

    # Arguments common settings definitions
    group = parser.add_argument_group('common settings arguments')
    group.add_argument(
        '--confirm',
        dest='confirm',
        action='store_true',
        help='Automatically confirm all removal and contents warnings',
    )
    group.add_argument(
        '--dry-run',
        dest='dry_run',
        action='store_true',
        help='Enable dry run mode to check without saving',
    )
    group.add_argument(
        '--dump',
        dest='dump',
        action='store_true',
        help='Dump Python objects of groups and projects',
    )
    group.add_argument(
        '--exclude-group',
        dest='exclude_group',
        action='store_true',
        help='Exclude parent group settings',
    )
    group.add_argument(
        '--exclude-subgroups',
        dest='exclude_subgroups',
        action='store_true',
        help='Exclude children subgroups settings',
    )
    group.add_argument(
        '--exclude-projects',
        dest='exclude_projects',
        action='store_true',
        help='Exclude children projects settings',
    )

    # Arguments general settings definitions
    group = parser.add_argument_group('general settings arguments')
    group.add_argument(
        '--available-features',
        dest='available_features',
        action='store_true',
        help='List the available GitLab project features known by the tool',
    )
    group.add_argument(
        '--reset-features',
        dest='reset_features',
        action='store',
        metavar='KEEP_FEATURES',
        nargs='?',
        const='',
        help='Reset features of GitLab projects based on usage\n'
        '(Optionally keep features separated by ",")',
    )
    group.add_argument(
        '--disable-features',
        dest='disable_features',
        metavar='FEATURES',
        help='List of features to disable separated by ","',
    )
    group.add_argument(
        '--enable-features',
        dest='enable_features',
        metavar='FEATURES',
        help='List of features to enable separated by ","',
    )
    group.add_argument(
        '--reset-members',
        dest='reset_members',
        action='store_true',
        help='Reset members of GitLab projects and groups',
    )
    group.add_argument(
        '--set-avatar',
        dest='set_avatar',
        action='store',
        metavar='FILE',
        help='Set avatar of GitLab projects and groups',
    )
    group.add_argument(
        '--set-description',
        dest='set_description',
        action='store',
        metavar='TEXT',
        help='Set description of GitLab projects and groups',
    )
    group.add_argument(
        '--update-descriptions',
        dest='update_description',
        action='store_true',
        help='Update description of GitLab projects and groups automatically',
    )

    # Arguments group settings definitions
    group = parser.add_argument_group('group settings arguments')
    group.add_argument(
        '--set-roles-create-projects',
        dest='set_roles_create_projects',
        action='store',
        metavar='ROLE',
        nargs='?',
        const=RolesCreateProjects.default(),
        help=
        f'Set roles allowed to create projects [{",".join(RolesCreateProjects.names())}]'
        ' (default: %(const)s)',
    )
    group.add_argument(
        '--set-roles-create-subgroups',
        dest='set_roles_create_subgroups',
        action='store',
        metavar='ROLE',
        nargs='?',
        const=RolesCreateSubgroups.default(),
        help=
        f'Set roles allowed to create subgroups [{",".join(RolesCreateSubgroups.names())}]'
        ' (default: %(const)s)',
    )

    # Arguments advanced settings definitions
    group = parser.add_argument_group('advanced settings arguments')
    subgroup = group.add_mutually_exclusive_group()
    subgroup.add_argument(
        '--run-housekeeping',
        dest='run_housekeeping',
        action='store_true',
        help='Run housekeeping of GitLab project or projects in groups',
    )
    subgroup.add_argument(
        '--prune-unreachable-objects',
        dest='prune_unreachable_objects',
        action='store_true',
        help='Prune unreachable objects of GitLab project or projects in groups',
    )
    subgroup = group.add_mutually_exclusive_group()
    subgroup.add_argument(
        '--archive-projects',
        dest='archive_project',
        action='store_true',
        help='Archive project or projects in GitLab groups',
    )
    subgroup.add_argument(
        '--unarchive-projects',
        dest='unarchive_project',
        action='store_true',
        help='Unarchive project or projects in GitLab groups',
    )
    group.add_argument(
        '--delete-groups',
        dest='delete_group',
        action='store_true',
        help='Delete group or groups in GitLab groups',
    )
    group.add_argument(
        '--delete-projects',
        dest='delete_project',
        action='store_true',
        help='Delete project or projects in GitLab groups',
    )

    # Arguments repository settings definitions
    group = parser.add_argument_group('repository settings arguments')
    group.add_argument(
        '--protect-branches',
        dest='protect_branches',
        action='store_true',
        help='Protect branches with default master/main, develop and staging',
    )
    group.add_argument(
        '--protect-tags',
        dest='protect_tags',
        action='store',
        metavar='LEVEL',
        nargs='?',
        const=ProtectionLevels.default(),
        help=f'Protect tags at level [{",".join(ProtectionLevels.names())}]'
        ' (default: %(const)s)',
    )

    # Arguments merge requests settings definitions
    group = parser.add_argument_group('merge requests settings arguments')
    group.add_argument(
        '--set-merge-method',
        dest='set_merge_method',
        metavar='METHOD',
        nargs='?',
        type=lambda value: (
            value if value in MergeRequestsMethod.VALUES # Keys
            else
            [key for key, _val in MergeRequestsMethod.VALUES.items() if _val == value][0]
            if value in MergeRequestsMethod.VALUES.values() # Values
            else exception(ValueError(value)) # Unknown
        ),
        const=MergeRequestsMethod.DEFAULT,
        help='Set project merge requests method'
        f' ({", ".join(MergeRequestsMethod.VALUES.keys())}, default: %(const)s)',
    )
    group.add_argument(
        '--set-merge-squash',
        dest='set_merge_squash',
        metavar='SQUASH',
        nargs='?',
        type=lambda value: (
            value if value in MergeRequestsSquash.VALUES # Keys
            else
            [key for key, _val in MergeRequestsSquash.VALUES.items() if _val == value][0]
            if value in MergeRequestsSquash.VALUES.values() # Values
            else exception(ValueError(value)) # Unknown
        ),
        const=MergeRequestsSquash.DEFAULT,
        help='Set project merge requests squashing'
        f' ({", ".join(MergeRequestsSquash.VALUES.keys())}, default: %(const)s)',
    )
    group.add_argument(
        '--set-merge-pipelines',
        dest='set_merge_pipelines',
        metavar='CHECK',
        nargs='?',
        type=lambda x: (str(x).lower() in ('true', 't', 'yes', 'y', 'on', '1')),
        const=MergeRequestsPipelines.DEFAULT,
        help='Set project merge requests check for successful pipelines'
        ' (true, false, default: %(const)s)',
    )
    group.add_argument(
        '--set-merge-skipped',
        dest='set_merge_skipped',
        metavar='CHECK',
        nargs='?',
        type=lambda x: (str(x).lower() in ('true', 't', 'yes', 'y', 'on', '1')),
        const=MergeRequestsSkipped.DEFAULT,
        help='Set project merge requests check for skipped pipelines'
        ' (true, false, default: %(const)s)',
    )
    group.add_argument(
        '--set-merge-resolved',
        dest='set_merge_resolved',
        metavar='CHECK',
        nargs='?',
        type=lambda x: (str(x).lower() in ('true', 't', 'yes', 'y', 'on', '1')),
        const=MergeRequestsResolved.DEFAULT,
        help='Set project merge requests check for resolved threads'
        ' (true, false, default: %(const)s)',
    )

    # Arguments CI/CD settings definitions
    group = parser.add_argument_group('ci/cd settings arguments')
    group.add_argument(
        '--add-jobs-token-allowlist',
        dest='add_jobs_token_allowlist',
        action='store',
        metavar='PATH',
        help='Add a group or project to CI/CD job token allowlist',
    )
    group.add_argument(
        '--remove-jobs-token-allowlist',
        dest='remove_jobs_token_allowlist',
        action='store',
        metavar='PATH',
        help='Remove a group or project from CI/CD job token allowlist',
    )
    subgroup = group.add_mutually_exclusive_group()
    subgroup.add_argument(
        '--erase-jobs-artifacts',
        dest='erase_jobs_artifacts',
        action='store_true',
        help='Erase all CI/CD jobs artifacts',
    )
    subgroup.add_argument(
        '--erase-jobs-contents',
        dest='erase_jobs_contents',
        action='store_true',
        help='Erase all CI/CD jobs artifacts and traces',
    )

    # Arguments issues definitions
    group = parser.add_argument_group('issues arguments')
    group.add_argument(
        '--get-project-issues-boards',
        dest='get_project_issues_boards',
        action='store_true',
        help='Get the GitLab project issues boards in JSON format',
    )
    group.add_argument(
        '--set-project-issues-boards',
        dest='set_project_issues_boards',
        metavar='JSON',
        help='Set the GitLab project issues boards from JSON format',
    )

    # Arguments labels definitions
    group = parser.add_argument_group('labels arguments')
    subgroup = group.add_mutually_exclusive_group()
    subgroup.add_argument(
        '--get-group-labels',
        dest='get_group_labels',
        action='store_true',
        help='Get the GitLab group labels in JSON format',
    )
    subgroup.add_argument(
        '--set-group-labels',
        dest='set_group_labels',
        metavar='JSON',
        help='Set the GitLab group labels from JSON format',
    )
    subgroup = group.add_mutually_exclusive_group()
    subgroup.add_argument(
        '--get-project-labels',
        dest='get_project_labels',
        action='store_true',
        help='Get the GitLab project labels in JSON format',
    )
    subgroup.add_argument(
        '--set-project-labels',
        dest='set_project_labels',
        metavar='JSON',
        help='Set the GitLab project labels from JSON format',
    )

    # Arguments positional definitions
    group = parser.add_argument_group('positional arguments')
    group.add_argument(
        '--',
        dest='double_dash',
        action='store_true',
        help='Positional arguments separator (recommended)',
    )
    group.add_argument(
        dest='url_path',
        action='store',
        nargs='?',
        help='GitLab group or project path URL',
    )

    # Arguments parser
    options: Namespace = parser.parse_args()

    # Help informations
    if options.help:
        print(' ')
        parser.print_help()
        print(' ')
        Platform.flush()
        sys_exit(0)

    # Instantiate settings
    settings: Settings = Settings(name=Bundle.NAME)

    # Prepare no_color
    if not options.no_color:
        if settings.has('themes', 'no_color'):
            options.no_color = settings.get_bool('themes', 'no_color')
        else:
            options.no_color = False
            settings.set_bool('themes', 'no_color', options.no_color)

    # Configure no_color
    if options.no_color:
        environ[Bundle.ENV_FORCE_COLOR] = '0'
        environ[Bundle.ENV_NO_COLOR] = '1'

    # Prepare colors
    Colors.prepare()

    # Settings setter
    if options.set:
        settings.set(options.set[0], options.set[1], options.set[2])
        settings.show()
        sys_exit(0)

    # Settings informations
    if options.settings:
        settings.show()
        sys_exit(0)

    # Instantiate updates
    updates: Updates = Updates(
        name=Bundle.PACKAGE,
        settings=settings,
    )

    # Version informations
    if options.version:
        print(
            f'{Bundle.NAME} {Version.get()} from {Version.path()} (python {Version.python()})'
        )
        Platform.flush()
        sys_exit(0)

    # Check for current updates
    if options.update_check:
        if not updates.check():
            updates.check(older=True)
        sys_exit(0)

    # Arguments validation
    if not options.url_path:
        result = Entrypoint.Result.CRITICAL

    # Header
    print(' ')
    Platform.flush()

    # Tool identifier
    if result != Entrypoint.Result.CRITICAL:
        print(f'{Colors.BOLD} {Bundle.NAME}'
              f'{Colors.YELLOW_LIGHT} ({Version.get()})'
              f'{Colors.RESET}')
        Platform.flush()

    # CLI entrypoint
    if result != Entrypoint.Result.CRITICAL:
        result = Entrypoint.cli(
            options,
            environments,
        )

    # CLI helper
    else:
        parser.print_help()

    # Footer
    print(' ')
    Platform.flush()

    # Check for daily updates
    if updates.enabled and updates.daily:
        updates.check()

    # Result
    if result in [
            Entrypoint.Result.SUCCESS,
            Entrypoint.Result.FINALIZE,
    ]:
        sys_exit(0)
    else:
        sys_exit(1)

# Entrypoint
if __name__ == '__main__': # pragma: no cover
    main()
