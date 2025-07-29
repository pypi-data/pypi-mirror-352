#!/usr/bin/env python3

# Standard libraries
from argparse import Namespace
from enum import Enum
import json
from typing import Dict, List, Optional, Union
import urllib.parse

# Modules libraries
from gitlab.config import ConfigError, GitlabConfigParser
from gitlab.exceptions import GitlabGetError
from gitlab.v4.objects import (
    Group as GitLabGroup,
    Project as GitLabProject,
    User as GitLabUser,
)
import questionary

# Components
from ..features.gitlab import GitLabFeature
from ..prints.colors import Colors
from ..prints.themes import Themes
from ..system.platform import Platform
from ..types.environments import Environments
from ..types.gitlab import (
    MergeRequestsMethod,
    MergeRequestsPipelines,
    MergeRequestsResolved,
    MergeRequestsSkipped,
    MergeRequestsSquash,
    ProjectFeatures,
)
from ..types.namespaces import Namespaces

# Entrypoint class, pylint: disable=too-few-public-methods
class Entrypoint:

    # Enumerations
    Result = Enum('Result', [
        'SUCCESS',
        'FINALIZE',
        'ERROR',
        'CRITICAL',
    ])

    # CLI, pylint: disable=too-many-branches,too-many-locals,too-many-statements
    @staticmethod
    def cli(
        options: Namespace,
        environments: Environments,
    ) -> Result:

        # Variables
        group: Optional[GitLabGroup] = None
        project: Optional[GitLabProject] = None
        result: Entrypoint.Result
        user: Optional[GitLabUser] = None

        # Header
        print(' ')

        # Parse URL variables
        gitlab_splits: urllib.parse.SplitResult = urllib.parse.urlsplit(options.url_path)
        gitlab_id: str = f'{gitlab_splits.netloc}'
        gitlab_url: str = f'{gitlab_splits.scheme}://{gitlab_splits.netloc}'
        gitlab_path: str = gitlab_splits.path.lstrip('/')

        # Prepare credentials
        private_token: str = environments.value('gitlab_token')
        job_token: str = environments.value('ci_job_token')
        ssl_verify: Union[bool, str] = True

        # Parse configuration files
        try:
            config: GitlabConfigParser
            if not private_token:
                config = GitlabConfigParser(gitlab_id, options.configs)
                private_token = str(config.private_token)
                if ssl_verify and (not config.ssl_verify
                                   or isinstance(config.ssl_verify, str)):
                    ssl_verify = config.ssl_verify
        except ConfigError as e:
            print(str(e))

        # GitLab client
        gitlab = GitLabFeature(
            url=gitlab_url,
            private_token=private_token,
            job_token=job_token,
            ssl_verify=ssl_verify,
            dry_run=options.dry_run,
        )
        print(f'{Colors.BOLD} - GitLab host: '
              f'{Colors.GREEN}{gitlab.url}'
              f'{Colors.CYAN} ({gitlab.username})'
              f'{Colors.RESET}')
        Platform.flush()

        # GitLab path
        try:
            group = gitlab.group(gitlab_path)
            print(f'{Colors.BOLD} - GitLab group: '
                  f'{Colors.GREEN}{group.full_path}'
                  f'{Colors.CYAN} # {group.description if group.description else "/"}'
                  f'{Colors.RESET}')
            print(' ')
            Platform.flush()
        except GitlabGetError as exception:
            try:
                if '/' in gitlab_path:
                    raise TypeError from exception
                user = gitlab.user(gitlab_path)
                namespace = gitlab.namespace(gitlab_path)
                print(f'{Colors.BOLD} - GitLab user namespace: '
                      f'{Colors.GREEN}{namespace.full_path}'
                      f'{Colors.CYAN} ({namespace.name})'
                      f'{Colors.RESET}')
                print(' ')
                Platform.flush()
            except (GitlabGetError, TypeError):
                project = gitlab.project(gitlab_path)
                print(
                    f'{Colors.BOLD} - GitLab project: '
                    f'{Colors.GREEN}{project.path_with_namespace}'
                    f'{Colors.CYAN} # {project.description if project.description else "/"}'
                    f'{Colors.RESET}')
                print(' ')
                Platform.flush()

        # Handle available features
        if options.available_features:
            print(f'{Colors.BOLD} - GitLab project:'
                  f'{Colors.RESET}')
            print(f'{Colors.BOLD}   - Available features: '
                  f'{Colors.CYAN}\'{", ".join(ProjectFeatures.names())}\''
                  f'{Colors.RESET}')
            Platform.flush()
            return Entrypoint.Result.FINALIZE

        # Handle single project
        if project:
            Entrypoint.project(
                options,
                gitlab,
                project.path_with_namespace,
            )

        # Handle group recursively
        elif group:

            # Handle group
            if not options.exclude_group:
                result = Entrypoint.group(
                    options,
                    gitlab,
                    group.full_path,
                )
                if result in [
                        Entrypoint.Result.FINALIZE,
                        Entrypoint.Result.ERROR,
                ]:
                    return result

            # Iterate through subgroups
            if not options.exclude_subgroups:
                for group_subgroup in sorted(
                        group.descendant_groups.list(
                            get_all=True,
                            include_subgroups=True,
                            order_by='path',
                            sort='asc',
                        ),
                        key=lambda item: item.full_path,
                ):
                    result = Entrypoint.group(
                        options,
                        gitlab,
                        group_subgroup.full_path,
                        True,
                    )
                    if result in [
                            Entrypoint.Result.FINALIZE,
                            Entrypoint.Result.ERROR,
                    ]:
                        return result

            # Iterate through projects
            if not options.exclude_projects:
                for group_project in sorted(
                        group.projects.list(
                            get_all=True,
                            with_shared=False,
                            include_subgroups=not options.exclude_subgroups,
                            order_by='path',
                            sort='asc',
                        ),
                        key=lambda item: item.path_with_namespace,
                ):
                    result = Entrypoint.project(
                        options,
                        gitlab,
                        group_project.path_with_namespace,
                    )
                    if result in [
                            Entrypoint.Result.FINALIZE,
                            Entrypoint.Result.ERROR,
                    ]:
                        return result

        # Handle user recursively
        elif user:

            # Iterate through projects
            if not options.exclude_projects:
                for user_project in sorted(
                        user.projects.list(
                            get_all=True,
                            order_by='path',
                            sort='asc',
                        ),
                        key=lambda item: item.path_with_namespace,
                ):
                    result = Entrypoint.project(
                        options,
                        gitlab,
                        user_project.path_with_namespace,
                    )
                    if result in [
                            Entrypoint.Result.FINALIZE,
                            Entrypoint.Result.ERROR,
                    ]:
                        return result

        # Result
        return Entrypoint.Result.SUCCESS

    # Confirm
    @staticmethod
    def confirm(
        description: str,
        text: str = '',
        interactive: bool = True,
        action: str = '',
        indent: str = '   ',
    ) -> bool:

        # Header
        print(
            f'{Colors.BOLD}{indent}- {description}{": " if description else ""}Confirm \''
            f'{Colors.RED}{text}'
            f'{Colors.BOLD}\' {action}:'
            f'{Colors.RESET}', end='')
        Platform.flush()

        # Confirm without user interaction
        if not interactive:
            print(f'{Colors.RED} Confirmed by parameters'
                  f'{Colors.RESET}')
            Platform.flush()
            return True

        # Get user configuration
        answer: bool = questionary.confirm(
            message='',
            default=False,
            qmark='',
            style=Themes.confirmation_style(),
            auto_enter=True,
        ).ask()

        # Result
        return answer

    # Group, pylint: disable=too-many-locals
    @staticmethod
    def group(
        options: Namespace,
        gitlab: GitLabFeature,
        criteria: str,
        subgroup: bool = False,
    ) -> Result:

        # Variables
        changed: bool

        # Acquire group
        group = gitlab.group(criteria)

        # Acquire parent group
        parent_group: Optional[GitLabGroup] = None
        if group.parent_id:
            parent_group = gitlab.group(group.parent_id)

        # Get parent description
        parent_description: str = ''
        parent_name: str = ''
        if parent_group:
            parent_description = parent_group.description
            parent_name = parent_group.name

        # Show group details
        group_type = 'subgroup' if subgroup else 'group'
        print(f'{Colors.BOLD} - GitLab {group_type}: '
              f'{Colors.YELLOW_LIGHT}{group.full_path}'
              f'{Colors.CYAN} # {group.description if group.description else "/"}'
              f'{Colors.RESET}')
        Platform.flush()

        # Delete group after validation
        if options.delete_group:
            if not Entrypoint.confirm(
                    f'Delete {group_type}',
                    group.full_path,
                    not options.confirm,
                    'deletion',
            ):
                print(' ')
                Platform.flush()
                return Entrypoint.Result.SUCCESS

            # Delete group
            gitlab.group_delete(criteria)
            print(f'{Colors.BOLD}   - Delete {group_type}: '
                  f'{Colors.GREEN}Success'
                  f'{Colors.RESET}')
            print(' ')
            Platform.flush()
            return Entrypoint.Result.SUCCESS if subgroup else Entrypoint.Result.FINALIZE

        # Set group description
        if options.set_description:
            changed = gitlab.group_set_description(
                criteria,
                options.set_description,
            )
            print(f'{Colors.BOLD}   - Set description: '
                  f'{Colors.CYAN if changed else Colors.GREEN}{options.set_description}'
                  f'{Colors.RESET}')
            Platform.flush()

        # Update group description
        elif options.update_description:
            parent_description_text: str = ''
            if parent_name:
                parent_description_text = ' - ' + Namespaces.describe(
                    name=parent_name,
                    description=parent_description,
                )
            if not group.description or subgroup and ( \
                        not parent_description_text or \
                        not group.description.endswith(f'{parent_description_text}') \
                    ):
                description = f'{Namespaces.describe(name=group.name)}' \
                              f'{parent_description_text}'
                changed = gitlab.group_set_description(
                    criteria,
                    description,
                )
                print(f'{Colors.BOLD}   - Updated description: '
                      f'{Colors.CYAN if changed else Colors.GREEN}{description}'
                      f'{Colors.RESET}')
                Platform.flush()
            else:
                print(f'{Colors.BOLD}   - Kept description: '
                      f'{Colors.GREEN}{group.description}'
                      f'{Colors.RESET}')
                Platform.flush()

        # Reset group members
        if options.reset_members:
            gitlab.group_reset_members(criteria)
            print(f'{Colors.BOLD}   - Reset members: '
                  f'{Colors.GREEN}Success'
                  f'{Colors.RESET}')
            Platform.flush()

        # Set group avatar
        if options.set_avatar:
            gitlab.group_set_avatar(
                criteria,
                options.set_avatar,
            )
            print(f'{Colors.BOLD}   - Set avatar: '
                  f'{Colors.CYAN}{options.set_avatar}'
                  f'{Colors.RESET}')
            Platform.flush()

        # Set group roles create projects
        if options.set_roles_create_projects:
            changed = gitlab.group_set_roles_create_projects(
                criteria,
                options.set_roles_create_projects,
            )
            print(
                f'{Colors.BOLD}   - Set roles allowed to create projects: '
                f'{Colors.CYAN if changed else Colors.GREEN}{options.set_roles_create_projects}'
                f'{Colors.RESET}')
            Platform.flush()

        # Set group roles create subgroups
        if options.set_roles_create_subgroups:
            changed = gitlab.group_set_roles_create_subgroups(
                criteria,
                options.set_roles_create_subgroups,
            )
            print(
                f'{Colors.BOLD}   - Set roles allowed to create subgroups: '
                f'{Colors.CYAN if changed else Colors.GREEN}{options.set_roles_create_subgroups}'
                f'{Colors.RESET}')
            Platform.flush()

        # Get group labels
        if options.get_group_labels:
            labels_objects = gitlab.group_get_labels(criteria)
            if labels_objects:
                print(f'{Colors.BOLD}   - Get labels to JSON: '
                      f'{Colors.RESET}', end='')
                labels_list: List[Dict[str, str]] = []
                for label in labels_objects:
                    labels_list += [{
                        'name': label.name,
                        'description': label.description,
                        'text_color': label.text_color,
                        'color': label.color,
                    }]
                print(json.dumps(labels_list))
                Platform.flush()

        # Set group labels
        elif options.set_group_labels:
            print(f'{Colors.BOLD}   - Set labels from JSON: '
                  f'{Colors.RESET}', end='')
            labels_names: List[str] = []
            labels_json = json.loads(options.set_group_labels)
            for label_json in labels_json:
                label_set = gitlab.group_set_label(
                    criteria,
                    name=label_json['name'],
                    description=label_json['description'],
                    text_color=label_json['text_color'],
                    color=label_json['color'],
                )
                labels_names += [label_set.name]
            print(f'{Colors.CYAN}{", ".join(labels_names)}'
                  f'{Colors.RESET}')
            Platform.flush()

        # Dump group object
        if options.dump:
            print(' ')
            print(group.to_json())

        # Footer
        print(' ')
        Platform.flush()

        # Result
        return Entrypoint.Result.SUCCESS

    # Project, pylint: disable=too-many-branches,too-many-locals,too-many-statements
    @staticmethod
    def project(
        options: Namespace,
        gitlab: GitLabFeature,
        criteria: str,
    ) -> Result:

        # Variables
        changed: Optional[bool]

        # Acquire project
        project = gitlab.project(criteria)

        # Show project details
        print(f'{Colors.BOLD} - GitLab project: '
              f'{Colors.YELLOW_LIGHT}{project.path_with_namespace}'
              f'{Colors.CYAN} # {project.description if project.description else "/"}'
              f'{Colors.RESET}')
        Platform.flush()

        # Delete project after validation
        if options.delete_project:
            if not Entrypoint.confirm(
                    'Delete project',
                    project.path_with_namespace,
                    not options.confirm,
                    'deletion',
            ):
                print(' ')
                Platform.flush()
                return Entrypoint.Result.SUCCESS

            # Delete project
            gitlab.project_delete(criteria)
            print(f'{Colors.BOLD}   - Delete project: '
                  f'{Colors.GREEN}Success'
                  f'{Colors.RESET}')
            print(' ')
            Platform.flush()
            return Entrypoint.Result.SUCCESS

        # Set project description
        if options.set_description:
            changed = gitlab.project_set_description(
                criteria,
                options.set_description,
            )
            print(f'{Colors.BOLD}   - Set description: '
                  f'{Colors.CYAN if changed else Colors.GREEN}{options.set_description}'
                  f'{Colors.RESET}')
            Platform.flush()

        # Update project description
        elif options.update_description:
            namespace_description: str
            if project.namespace['kind'] == 'user':
                namespace = gitlab.namespace(project.namespace['id'])
                namespace_description = namespace.name
            else:
                group = gitlab.group(project.namespace['id'])
                namespace_description = Namespaces.describe(
                    name=group.name,
                    description=group.description,
                )
            if not project.description or \
                    not project.description.endswith(f' - {namespace_description}'):
                description = f'{Namespaces.describe(name=project.name)}' \
                              f' - {namespace_description}'
                changed = gitlab.project_set_description(
                    criteria,
                    description,
                )
                print(f'{Colors.BOLD}   - Updated description: '
                      f'{Colors.CYAN if changed else Colors.GREEN}{description}'
                      f'{Colors.RESET}')
                Platform.flush()
            else:
                print(f'{Colors.BOLD}   - Kept description: '
                      f'{Colors.GREEN}{project.description}'
                      f'{Colors.RESET}')
                Platform.flush()

        # Reset project features
        if options.reset_features is not None:
            features = ', '.join(
                gitlab.project_features_reset(
                    criteria,
                    GitLabFeature.project_features_parse(options.reset_features),
                ))
            if features:
                print(f'{Colors.BOLD}   - Reset features: '
                      f'{Colors.CYAN}{features}'
                      f'{Colors.RESET}')
                Platform.flush()
            else:
                print(f'{Colors.BOLD}   - Reset features: '
                      f'{Colors.GREEN}Already done'
                      f'{Colors.RESET}')
                Platform.flush()

        # Disable project features
        if options.disable_features:
            features = ', '.join(
                gitlab.project_features_disable(
                    criteria,
                    GitLabFeature.project_features_parse(options.disable_features),
                ))
            if features:
                print(f'{Colors.BOLD}   - Disable features: '
                      f'{Colors.CYAN}{features}'
                      f'{Colors.RESET}')
                Platform.flush()
            else:
                print(f'{Colors.BOLD}   - Disable features: '
                      f'{Colors.GREEN}Already done'
                      f'{Colors.RESET}')
                Platform.flush()

        # Enable project features
        if options.enable_features:
            features = ', '.join(
                gitlab.project_features_enable(
                    criteria,
                    GitLabFeature.project_features_parse(options.enable_features),
                ))
            if features:
                print(f'{Colors.BOLD}   - Enable features: '
                      f'{Colors.CYAN}{features}'
                      f'{Colors.RESET}')
                Platform.flush()
            else:
                print(f'{Colors.BOLD}   - Enable features: '
                      f'{Colors.GREEN}Already done'
                      f'{Colors.RESET}')
                Platform.flush()

        # Reset project members
        if options.reset_members:
            gitlab.project_reset_members(criteria)
            print(f'{Colors.BOLD}   - Reset members: '
                  f'{Colors.GREEN}Success'
                  f'{Colors.RESET}')
            Platform.flush()

        # Set project avatar
        if options.set_avatar:
            gitlab.project_set_avatar(
                criteria,
                options.set_avatar,
            )
            print(f'{Colors.BOLD}   - Set avatar: '
                  f'{Colors.CYAN}{options.set_avatar}'
                  f'{Colors.RESET}')
            Platform.flush()

        # Run project housekeeping
        if options.run_housekeeping:
            gitlab.project_run_housekeeping(criteria)
            print(f'{Colors.BOLD}   - Ran housekeeping: '
                  f'{Colors.GREEN}Success'
                  f'{Colors.RESET}')
            Platform.flush()

        # Prune project unreachable objects
        if options.prune_unreachable_objects:
            gitlab.project_prune_unreachable_objects(criteria)
            print(f'{Colors.BOLD}   - Pruned unreachable objects: '
                  f'{Colors.GREEN}Success'
                  f'{Colors.RESET}')
            Platform.flush()

        # Archive project
        if options.archive_project:
            changed = gitlab.project_set_archive(
                criteria,
                True,
            )
            print(f'{Colors.BOLD}   - Archive project: '
                  f'{Colors.CYAN if changed else Colors.GREEN}'
                  f'{"Success" if changed else "Already done"}'
                  f'{Colors.RESET}')
            Platform.flush()

        # Unarchive project
        elif options.unarchive_project:
            changed = gitlab.project_set_archive(
                criteria,
                False,
            )
            print(f'{Colors.BOLD}   - Unarchive project: '
                  f'{Colors.CYAN if changed else Colors.GREEN}'
                  f'{"Success" if changed else "Already done"}'
                  f'{Colors.RESET}')
            Platform.flush()

        # Protect project branches
        if options.protect_branches:
            branches = ', '.join(gitlab.project_protect_branches(criteria))
            if branches:
                print(f'{Colors.BOLD}   - Protecting branches: '
                      f'{Colors.CYAN}{branches}'
                      f'{Colors.RESET}')
                Platform.flush()
            else:
                print(f'{Colors.BOLD}   - Protecting branches: '
                      f'{Colors.GREEN}Already done'
                      f'{Colors.RESET}')
                Platform.flush()

        # Protect project tags
        if options.protect_tags:
            tags = ', '.join(gitlab.project_protect_tags(criteria, options.protect_tags))
            if tags:
                print(f'{Colors.BOLD}   - Protecting tags: '
                      f'{Colors.CYAN}{tags}'
                      f'{Colors.GREEN} (level: {options.protect_tags})'
                      f'{Colors.RESET}')
                Platform.flush()
            else:
                print(f'{Colors.BOLD}   - Protecting tags: '
                      f'{Colors.GREEN}Already done'
                      f'{Colors.RESET}')
                Platform.flush()

        # Set project merge method
        if options.set_merge_method is not None:
            changed = gitlab.project_set_attribute(
                criteria,
                MergeRequestsMethod.ATTRIBUTE,
                MergeRequestsMethod.VALUES[options.set_merge_method],
            )
            if changed is None:
                print(f'{Colors.BOLD}   - Set merge method: '
                      f'{Colors.RED}Unknown feature'
                      f'{Colors.RESET}')
            else:
                print(f'{Colors.BOLD}   - Set merge method: '
                      f'{Colors.CYAN if changed else Colors.GREEN}'
                      f'{options.set_merge_method}'
                      f'{Colors.RESET}')
            Platform.flush()

        # Set project merge squash
        if options.set_merge_squash is not None:
            changed = gitlab.project_set_attribute(
                criteria,
                MergeRequestsSquash.ATTRIBUTE,
                MergeRequestsSquash.VALUES[options.set_merge_squash],
            )
            if changed is None:
                print(f'{Colors.BOLD}   - Set merge squash: '
                      f'{Colors.RED}Unknown feature'
                      f'{Colors.RESET}')
            else:
                print(f'{Colors.BOLD}   - Set merge squash: '
                      f'{Colors.CYAN if changed else Colors.GREEN}'
                      f'{options.set_merge_squash}'
                      f'{Colors.RESET}')
            Platform.flush()

        # Set project merge pipelines
        if options.set_merge_pipelines is not None:
            changed = gitlab.project_set_attribute(
                criteria,
                MergeRequestsPipelines.ATTRIBUTE,
                options.set_merge_pipelines,
            )
            if changed is None:
                print(f'{Colors.BOLD}   - Set merge pipelines: '
                      f'{Colors.RED}Unknown feature'
                      f'{Colors.RESET}')
            else:
                print(f'{Colors.BOLD}   - Set merge pipelines: '
                      f'{Colors.CYAN if changed else Colors.GREEN}'
                      f'{str(options.set_merge_pipelines).lower()}'
                      f'{Colors.RESET}')
            Platform.flush()

        # Set project merge skipped
        if options.set_merge_skipped is not None:
            changed = gitlab.project_set_attribute(
                criteria,
                MergeRequestsSkipped.ATTRIBUTE,
                options.set_merge_skipped,
            )
            if changed is None:
                print(f'{Colors.BOLD}   - Set merge skipped: '
                      f'{Colors.RED}Unknown feature'
                      f'{Colors.RESET}')
            else:
                print(f'{Colors.BOLD}   - Set merge skipped: '
                      f'{Colors.CYAN if changed else Colors.GREEN}'
                      f'{str(options.set_merge_skipped).lower()}'
                      f'{Colors.RESET}')
            Platform.flush()

        # Set project merge resolved
        if options.set_merge_resolved is not None:
            changed = gitlab.project_set_attribute(
                criteria,
                MergeRequestsResolved.ATTRIBUTE,
                options.set_merge_resolved,
            )
            if changed is None:
                print(f'{Colors.BOLD}   - Set merge method: '
                      f'{Colors.RED}Unknown feature'
                      f'{Colors.RESET}')
            else:
                print(f'{Colors.BOLD}   - Set merge method: '
                      f'{Colors.CYAN if changed else Colors.GREEN}'
                      f'{str(options.set_merge_resolved).lower()}'
                      f'{Colors.RESET}')
            Platform.flush()

        # Add path to CI/CD job token allowlist
        if options.add_jobs_token_allowlist:
            gitlab.project_job_allowlist_add(
                criteria,
                options.add_jobs_token_allowlist,
            )
            print(f'{Colors.BOLD}   - Added to CI/CD job token allowlist: '
                  f'{Colors.CYAN}{options.add_jobs_token_allowlist}'
                  f'{Colors.RESET}')
            Platform.flush()

        # Remove path from CI/CD job token allowlist
        if options.remove_jobs_token_allowlist:
            gitlab.project_job_allowlist_remove(
                criteria,
                options.remove_jobs_token_allowlist,
            )
            print(f'{Colors.BOLD}   - Removed from CI/CD job token allowlist: '
                  f'{Colors.CYAN}{options.remove_jobs_token_allowlist}'
                  f'{Colors.RESET}')
            Platform.flush()

        # Erase project jobs artifacts and traces
        if options.erase_jobs_contents:
            gitlab.project_erase_jobs_contents(criteria)
            print(f'{Colors.BOLD}   - Erased CI/CD jobs artifacts and traces: '
                  f'{Colors.GREEN}Success'
                  f'{Colors.RESET}')
            Platform.flush()

        # Erase project jobs artifacts
        elif options.erase_jobs_artifacts:
            gitlab.project_erase_jobs_artifacts(criteria)
            print(f'{Colors.BOLD}   - Erased CI/CD jobs artifacts: '
                  f'{Colors.GREEN}Success'
                  f'{Colors.RESET}')
            Platform.flush()

        # Get project issues boards
        if options.get_project_issues_boards:
            issues_boards_objects = gitlab.project_get_issues_boards(criteria)
            if issues_boards_objects:
                print(f'{Colors.BOLD}   - Get issues boards to JSON: '
                      f'{Colors.RESET}', end='')
                issues_boards_list: List[Dict[str, Union[bool, str, List[Dict[str, str]],
                                                         None]]] = []
                for board in issues_boards_objects:
                    board_lists: List[Dict[str, str]] = []
                    for board_list in board.lists.list(get_all=True):
                        board_lists += [{
                            'label': board_list.label['name'],
                            'position': board_list.position,
                        }]
                    issues_boards_list += [{
                        'name': board.name,
                        'hide_backlog_list': board.hide_backlog_list,
                        'hide_closed_list': board.hide_closed_list,
                        'lists': board_lists,
                    }]
                print(json.dumps(issues_boards_list))
                Platform.flush()

        # Set project issues boards
        elif options.set_project_issues_boards:
            print(f'{Colors.BOLD}   - Set issues boards from JSON: '
                  f'{Colors.RESET}', end='')
            if not project.archived:
                issues_boards_names: List[str] = []
                issues_boards_json = json.loads(options.set_project_issues_boards)
                for board_json in issues_boards_json:
                    board_set = gitlab.project_set_issues_board(
                        criteria, name=board_json['name'],
                        hide_backlog_list=board_json['hide_backlog_list'],
                        hide_closed_list=board_json['hide_closed_list'], lists=[{
                            'label': board_list['label'],
                            'position': board_list['position'],
                        } for board_list in board_json['lists']])
                    issues_boards_names += [board_set.name]
                print(f'{Colors.CYAN}{", ".join(issues_boards_names)}'
                      f'{Colors.RESET}')
            else:
                print(f'{Colors.RED}Archived project are read-only'
                      f'{Colors.RESET}')
            Platform.flush()

        # Get project labels
        if options.get_project_labels:
            labels_objects = gitlab.project_get_labels(criteria)
            if labels_objects:
                print(f'{Colors.BOLD}   - Get labels to JSON: '
                      f'{Colors.RESET}', end='')
                labels_list: List[Dict[str, Union[str, None]]] = []
                for label in labels_objects:
                    labels_list += [{
                        'name': label.name,
                        'description': label.description,
                        'text_color': label.text_color,
                        'color': label.color,
                        'priority': label.priority,
                    }]
                print(json.dumps(labels_list))
                Platform.flush()

        # Set project labels
        elif options.set_project_labels:
            print(f'{Colors.BOLD}   - Set labels from JSON: '
                  f'{Colors.RESET}', end='')
            if not project.archived:
                labels_names: List[str] = []
                labels_json = json.loads(options.set_project_labels)
                for label_json in labels_json:
                    label_set = gitlab.project_set_label(
                        criteria,
                        name=label_json['name'],
                        description=label_json['description'],
                        text_color=label_json['text_color'],
                        color=label_json['color'],
                        priority=label_json['priority'],
                    )
                    labels_names += [label_set.name]
                print(f'{Colors.CYAN}{", ".join(labels_names)}'
                      f'{Colors.RESET}')
            else:
                print(f'{Colors.RED}Archived project are read-only'
                      f'{Colors.RESET}')
            Platform.flush()

        # Dump project object
        if options.dump:
            print(' ')
            print(project.to_json())

        # Footer
        print(' ')
        Platform.flush()

        # Result
        return Entrypoint.Result.SUCCESS
