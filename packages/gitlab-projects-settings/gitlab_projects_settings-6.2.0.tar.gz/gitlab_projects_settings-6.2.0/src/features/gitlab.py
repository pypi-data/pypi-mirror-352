#!/usr/bin/env python3

# Standard libraries
from time import sleep
from typing import cast, Dict, List, Optional, Union

# Modules libraries
from gitlab import Gitlab
from gitlab.base import RESTObject, RESTObjectList
from gitlab.const import AccessLevel as GitLabAccessLevel
from gitlab.exceptions import (
    GitlabDeleteError,
    GitlabGetError,
    GitlabJobEraseError,
    GitlabListError,
)
from gitlab.v4.objects import (
    Group,
    GroupLabel,
    Namespace,
    Project,
    ProjectBoard,
    ProjectBoardList,
    ProjectLabel,
    User,
)

# Components
from ..types.gitlab import (
    AccessLevels,
    ProjectFeatures,
    ProtectionLevels,
    RolesCreateProjects,
    RolesCreateSubgroups,
)

# GitLabFeature class, pylint: disable=too-many-public-methods
class GitLabFeature:

    # Constants
    TIMEOUT_DELETION: int = 300

    # Members
    __dry_run: bool = False
    __gitlab: Gitlab

    # Constructor, pylint: disable=too-many-arguments,too-many-positional-arguments
    def __init__(
        self,
        url: str,
        private_token: str,
        job_token: str,
        ssl_verify: Union[bool, str] = True,
        dry_run: bool = False,
    ) -> None:

        # Initialize members
        self.__dry_run = dry_run

        # Create GitLab client
        if private_token:
            self.__gitlab = Gitlab(
                url=url,
                private_token=private_token,
                ssl_verify=ssl_verify,
            )
        elif job_token:
            self.__gitlab = Gitlab(
                url=url,
                job_token=job_token,
                ssl_verify=ssl_verify,
            )
        else:
            self.__gitlab = Gitlab(
                url=url,
                ssl_verify=ssl_verify,
            )

        # Authenticate if available
        if self.__gitlab.private_token or self.__gitlab.oauth_token:
            self.__gitlab.auth()

    # Group
    def group(
        self,
        criteria: str,
    ) -> Group:
        return self.__gitlab.groups.get(criteria)

    # Group delete
    def group_delete(
        self,
        criteria: str,
    ) -> None:

        # Delete group
        group = self.group(criteria)
        if not self.__dry_run:
            group.delete()
            sleep(1)
            try:
                group = self.group(criteria)
                group.delete(query_data={
                    'full_path': group.full_path,
                    'permanently_remove': 'true',
                })
            except (GitlabDeleteError, GitlabGetError):
                pass

            # Wait for deletion
            for _ in range(GitLabFeature.TIMEOUT_DELETION):
                sleep(1)
                try:
                    group = self.group(criteria)
                    if group.marked_for_deletion_on:
                        break
                except AttributeError:
                    pass
                except GitlabGetError:
                    break

        # Delay for deletion
        sleep(3)

    # Group get labels
    def group_get_labels(
        self,
        criteria: str,
    ) -> Union[RESTObjectList, List[RESTObject]]:

        # Get group labels
        group = self.group(criteria)
        return group.labels.list(get_all=True)

    # Group reset members
    def group_reset_members(
        self,
        criteria: str,
    ) -> None:

        # Remove group members
        group = self.group(criteria)
        for member in sorted(
                group.members.list(get_all=True),
                key=lambda item: item.access_level,
        ):
            if not self.__dry_run:
                try:
                    group.members.delete(member.id)
                except GitlabDeleteError as exception:
                    if member.access_level == GitLabAccessLevel.OWNER \
                            and len(group.members.list(get_all=True)) == 1:
                        continue
                    raise exception

        # Save group
        if not self.__dry_run:
            group.save()

    # Group set avatar
    def group_set_avatar(
        self,
        criteria: str,
        file: str,
    ) -> None:

        # Set group avatar
        group = self.group(criteria)
        if not self.__dry_run:
            with open(file, 'rb') as avatar:
                group.avatar = avatar

                # Save group
                group.save()

    # Group set description
    def group_set_description(
        self,
        criteria: str,
        description: str,
    ) -> bool:

        # Variables
        changed: bool = False

        # Set group description
        group = self.group(criteria)
        if not self.__dry_run and group.description != description:
            group.description = description
            changed = True

            # Save group
            group.save()

        # Result
        return changed

    # Group set label, pylint: disable=too-many-arguments,too-many-positional-arguments
    def group_set_label(
        self,
        criteria: str,
        name: str,
        description: str,
        text_color: str,
        color: str,
    ) -> GroupLabel:

        # Create group label
        group = self.group(criteria)
        label: GroupLabel
        try:
            label = group.labels.get(name, include_ancestor_groups=False)
        except GitlabGetError:
            group.labels.create({
                'name': name,
                'description': description,
                'text_color': text_color,
                'color': color,
            })
            label = group.labels.get(name, include_ancestor_groups=False)

        # Update group label
        label.description = description
        label.text_color = text_color
        label.color = color
        label.save()

        # Result
        return label

    # Group set roles create projects
    def group_set_roles_create_projects(
        self,
        criteria: str,
        level: str,
    ) -> bool:

        # Variables
        changed: bool = False

        # Validate level
        if level not in RolesCreateProjects.names():
            raise SyntaxError(
                f'Unknown role level: {level} ({",".join(RolesCreateProjects.names())})')

        # Set roles allowed to create projects
        group = self.group(criteria)
        if not self.__dry_run and group.project_creation_level != level:
            group.project_creation_level = level
            changed = True

            # Save group
            group.save()

        # Result
        return changed

    # Group set roles create subgroups
    def group_set_roles_create_subgroups(
        self,
        criteria: str,
        level: str,
    ) -> bool:

        # Variables
        changed: bool = False

        # Validate level
        if level not in RolesCreateSubgroups.names():
            raise SyntaxError(
                f'Unknown role level: {level} ({",".join(RolesCreateSubgroups.names())})')

        # Set roles allowed to create subgroups
        group = self.group(criteria)
        if not self.__dry_run and group.subgroup_creation_level != level:
            group.subgroup_creation_level = level
            changed = True

            # Save group
            group.save()

        # Result
        return changed

    # Namespace
    def namespace(
        self,
        criteria: str,
    ) -> Namespace:
        return self.__gitlab.namespaces.get(criteria)

    # Project
    def project(
        self,
        criteria: str,
    ) -> Project:
        return self.__gitlab.projects.get(criteria)

    # Project delete
    def project_delete(
        self,
        criteria: str,
    ) -> None:

        # Delete project
        project = self.project(criteria)
        if not self.__dry_run:
            project.delete()
            sleep(1)
            try:
                project = self.project(criteria)
                project.delete(query_data={
                    'full_path': project.path_with_namespace,
                    'permanently_remove': 'true',
                })
            except (GitlabDeleteError, GitlabGetError):
                pass

            # Wait for deletion
            for _ in range(GitLabFeature.TIMEOUT_DELETION):
                sleep(1)
                try:
                    project = self.project(criteria)
                    if project.marked_for_deletion_on:
                        break
                except AttributeError:
                    pass
                except GitlabGetError:
                    break

        # Delay for deletion
        sleep(3)

    # Project erase jobs artifacts
    def project_erase_jobs_artifacts(
        self,
        criteria: str,
    ) -> None:

        # Erase project jobs artifacts
        project = self.project(criteria)
        if not self.__dry_run:
            for job in project.jobs.list():
                if job.artifacts_expire_at is not None:
                    job.delete_artifacts()

    # Project erase jobs artifacts and traces
    def project_erase_jobs_contents(
        self,
        criteria: str,
    ) -> None:

        # Erase project jobs artifacts and traces
        project = self.project(criteria)
        if not self.__dry_run:
            for job in project.jobs.list():
                if job.artifacts_expire_at is not None:
                    try:
                        job.erase()
                    except GitlabJobEraseError:
                        pass

    # Add path to project CI/CD job token allowlist
    def project_job_allowlist_add(
        self,
        criteria: str,
        path: str,
    ) -> None:

        # Add path to project CI/CD job token allowlist
        project = self.project(criteria)
        try:
            path_project = self.project(path)
            if not any(path_project.id == allowlist.get_id()
                       for allowlist in project.job_token_scope.get().allowlist.list() #
                       ) and not self.__dry_run:
                project.job_token_scope.get().allowlist.create({
                    'target_project_id': path_project.id,
                })
        except GitlabGetError:
            path_group = self.group(path)
            if not any(path_group.id == allowlist.get_id() for allowlist in
                       project.job_token_scope.get().groups_allowlist.list() #
                       ) and not self.__dry_run:
                project.job_token_scope.get().groups_allowlist.create({
                    'target_project_id': path_group.id,
                })

    # Remove path from project CI/CD job token allowlist
    def project_job_allowlist_remove(
        self,
        criteria: str,
        path: str,
    ) -> None:

        # Remove path from project CI/CD job token allowlist
        project = self.project(criteria)
        try:
            path_project = self.project(path)
            if any(path_project.id == allowlist.get_id()
                   for allowlist in project.job_token_scope.get().allowlist.list() #
                   ) and not self.__dry_run:
                project.job_token_scope.get().allowlist.delete(path_project.id)
        except GitlabGetError:
            path_group = self.group(path)
            if any(path_group.id == allowlist.get_id() for allowlist in
                   project.job_token_scope.get().groups_allowlist.list() #
                   ) and not self.__dry_run:
                project.job_token_scope.get().groups_allowlist.delete(path_group.id)

    # Project protect branches
    def project_protect_branches(
        self,
        criteria: str,
    ) -> List[str]:

        # Validate project feature
        result: List[str] = []
        project = self.project(criteria)
        try:
            assert project.branches.list(get_all=True)
        except (AssertionError, GitlabListError):
            return result

        # Acquire project, branches and protected branches
        branches = [branch.name for branch in project.branches.list(get_all=True)]
        protectedbranches = [
            protectedbranch.name
            for protectedbranch in project.protectedbranches.list(get_all=True)
        ]

        # Protect main/master
        for branch in ['main', 'master']:
            if branch in branches and branch not in protectedbranches:
                if not self.__dry_run:
                    project.protectedbranches.create({
                        'name': branch,
                        'merge_access_level': 40,
                        'push_access_level': 40,
                        'allow_force_push': False
                    })
                result += [branch]

        # Protect develop
        for branch in ['develop']:
            if branch in branches and branch not in protectedbranches:
                if not self.__dry_run:
                    project.protectedbranches.create({
                        'name': branch,
                        'merge_access_level': 40,
                        'push_access_level': 40,
                        'allow_force_push': True
                    })
                result += [branch]

        # Protect staging
        for branch in ['staging']:
            if branch in branches and branch not in protectedbranches:
                if not self.__dry_run:
                    project.protectedbranches.create({
                        'name': branch,
                        'merge_access_level': 30,
                        'push_access_level': 30,
                        'allow_force_push': True
                    })
                result += [branch]

        # Save project
        if not self.__dry_run:
            project.save()

        # Result
        return result

    # Project parse features
    @staticmethod
    def project_features_parse(input_string: str) -> List[str]:

        # Handle empty input
        if not input_string:
            return []

        # Parse features from input
        return [
            key # Key
            for search in input_string.split(',') # Input features
            for key in ProjectFeatures.keys() # GitLab features
            if ProjectFeatures.get(key).name.lower().startswith(search.strip().lower())
        ]

    # Project disable features
    def project_features_disable(
        self,
        criteria: str,
        features: List[str],
    ) -> List[str]:

        # Variables
        changed: bool
        result: List[str] = []
        project = self.__gitlab.projects.get(criteria, statistics=True)

        # Iterate through features
        for key in features:
            if key in ProjectFeatures.keys():
                changed = False
                feature = ProjectFeatures.get(key)

                # Disable 'access_level' feature
                for level in feature.access_level:
                    if hasattr(project, level.key) \
                            and getattr(project, level.key) != AccessLevels.DISABLED:
                        changed = True
                        setattr(
                            project,
                            level.key,
                            AccessLevels.DISABLED,
                        )

                # Disable 'enabled' feature
                for key in feature.enabled:
                    if hasattr(project, key) \
                            and getattr(project, key):
                        changed = True
                        setattr(
                            project,
                            key,
                            False,
                        )

                # Add changed feature
                if changed:
                    result.append(feature.name)

        # Save project
        if not self.__dry_run:
            project.save()

        # Result
        return result

    # Project enable features
    def project_features_enable(
        self,
        criteria: str,
        features: List[str],
    ) -> List[str]:

        # Variables
        changed: bool
        result: List[str] = []
        project = self.__gitlab.projects.get(criteria, statistics=True)

        # Iterate through features
        for key in features:
            if key in ProjectFeatures.keys():
                changed = False
                feature = ProjectFeatures.get(key)

                # Enable 'access_level' feature
                for level in feature.access_level:
                    if hasattr(project, level.key) \
                            and getattr(project, level.key) == AccessLevels.DISABLED:
                        changed = True
                        setattr(
                            project,
                            level.key,
                            level.settings[project.visibility],
                        )

                # Enable 'enabled' feature
                for key in feature.enabled:
                    if hasattr(project, key) \
                            and not getattr(project, key):
                        changed = True
                        setattr(
                            project,
                            key,
                            True,
                        )

                # Add changed feature
                if changed:
                    result.append(feature.name)

        # Save project
        if not self.__dry_run:
            project.save()

        # Result
        return result

    # Project reset features
    def project_features_reset(
        self,
        criteria: str,
        keep_features: List[str],
    ) -> List[str]:

        # Variables
        changed: bool
        result: List[str] = []
        project = self.__gitlab.projects.get(criteria, statistics=True)

        # Iterate through features
        for key in ProjectFeatures.keys():
            if key not in keep_features:
                changed = False
                feature = ProjectFeatures.get(key)

                # Disable 'access_level' feature
                for level in feature.access_level:
                    if changed or (hasattr(project, level.key) \
                            and getattr(project, level.key) != AccessLevels.DISABLED \
                            and not ProjectFeatures.test(self.__gitlab, project, feature.tests)):
                        changed = True
                        setattr(
                            project,
                            level.key,
                            AccessLevels.DISABLED,
                        )

                # Disable 'enabled' feature
                for key in feature.enabled:
                    if changed or (hasattr(project, key) \
                            and getattr(project, key) \
                            and not ProjectFeatures.test(self.__gitlab, project, feature.tests)):
                        changed = True
                        setattr(
                            project,
                            key,
                            False,
                        )

                # Add changed feature
                if changed:
                    result.append(feature.name)

        # Save project
        if not self.__dry_run:
            project.save()

        # Result
        return result

    # Project get issues boards
    def project_get_issues_boards(
        self,
        criteria: str,
    ) -> Union[RESTObjectList, List[RESTObject]]:

        # Get project issues boards
        project = self.project(criteria)
        return project.boards.list(get_all=True)

    # Project get labels
    def project_get_labels(
        self,
        criteria: str,
    ) -> Union[RESTObjectList, List[RESTObject]]:

        # Get project labels
        project = self.project(criteria)
        return [
            label for label in project.labels.list(get_all=True) if label.is_project_label
        ]

    # Project protect tags, pylint: disable=too-many-branches
    def project_protect_tags(
        self,
        criteria: str,
        protect_level: str,
    ) -> List[str]:

        # Validate project feature
        result: List[str] = []
        project = self.project(criteria)
        try:
            assert project.tags.list(get_all=True)
        except (AssertionError, GitlabListError):
            return result

        # Prepare access level
        access_level: int
        if protect_level == ProtectionLevels.NO_ONE:
            access_level = 0
        elif protect_level == ProtectionLevels.ADMINS:
            access_level = 60
        elif protect_level == ProtectionLevels.MAINTAINERS:
            access_level = 40
        elif protect_level == ProtectionLevels.DEVELOPERS:
            access_level = 30
        else:
            raise SyntaxError(f'Unknown protection level: {protect_level}')

        # Acquire protected tags
        protectedtags = [
            protectedtag.name for protectedtag in project.protectedtags.list(get_all=True)
        ]

        # Update protected tags
        for protectedtag in project.protectedtags.list(get_all=True):
            protectedtag_level = protectedtag.create_access_levels[0]['access_level']
            if protectedtag_level != 0 and (access_level == 0
                                            or protectedtag_level < access_level):
                name = protectedtag.name
                if not self.__dry_run:
                    protectedtag.delete()
                    project.protectedtags.create({
                        'name': name,
                        'create_access_level': access_level
                    })
                result += [name]

        # Protect unprotected tags
        for tag in project.tags.list(get_all=True):
            if tag.name not in protectedtags:
                if not self.__dry_run:
                    project.protectedtags.create({
                        'name': tag.name,
                        'create_access_level': access_level
                    })
                result += [tag.name]

        # Save project
        if not self.__dry_run:
            project.save()

        # Result
        result.sort()
        return result

    # Project prune unreachable objects
    def project_prune_unreachable_objects(
        self,
        criteria: str,
    ) -> None:

        # Prune project unreachable objects
        project = self.project(criteria)
        if not self.__dry_run:
            project.housekeeping(post_data={'task': 'prune'})

    # Project reset members
    def project_reset_members(
        self,
        criteria: str,
    ) -> None:

        # Remove project members
        project = self.project(criteria)
        if not self.__dry_run:
            for member in project.members.list(get_all=True):
                try:
                    project.members.delete(member.id)
                except GitlabDeleteError:
                    pass

            # Save project
            project.save()

    # Project run housekeeping
    def project_run_housekeeping(
        self,
        criteria: str,
    ) -> None:

        # Run project housekeeping
        project = self.project(criteria)
        if not self.__dry_run:
            project.housekeeping()

    # Project set archive
    def project_set_archive(
        self,
        criteria: str,
        enabled: bool,
    ) -> bool:

        # Variables
        changed: bool = False

        # Archive project
        project = self.project(criteria)
        if not self.__dry_run and enabled:
            if not project.archived:
                project.archive()
                changed = True

        # Unarchive project
        elif not self.__dry_run:
            if project.archived:
                project.unarchive()
                changed = True

        # Result
        return changed

    # Project set attribute
    def project_set_attribute(
        self,
        criteria: str,
        name: str,
        value: Union[bool, str],
    ) -> Optional[bool]:

        # Variables
        changed: bool = False

        # Check project attribute
        project = self.project(criteria)
        if not self.__dry_run and not hasattr(project, name):
            return None

        # Set project attribute
        if not self.__dry_run and getattr(project, name) != value:
            setattr(project, name, value)
            changed = True

            # Save project
            project.save()

        # Result
        return changed

    # Project set avatar
    def project_set_avatar(
        self,
        criteria: str,
        file: str,
    ) -> None:

        # Set project avatar
        project = self.project(criteria)
        if not self.__dry_run:
            with open(file, 'rb') as avatar:
                project.avatar = avatar

                # Save project
                project.save()

    # Project set description
    def project_set_description(
        self,
        criteria: str,
        description: str,
    ) -> bool:

        # Variables
        changed: bool = False

        # Set project description
        project = self.project(criteria)
        if not self.__dry_run and project.description != description:
            project.description = description
            changed = True

            # Save project
            project.save()

        # Result
        return changed

    # Project set issues_board, pylint: disable=too-many-arguments,too-many-positional-arguments
    def project_set_issues_board(
        self,
        criteria: str,
        name: str,
        hide_backlog_list: bool,
        hide_closed_list: bool,
        lists: List[Dict[str, str]],
    ) -> ProjectBoard:

        # Create project issues board
        project = self.project(criteria)
        issues_board: ProjectBoard
        try:
            issues_board = next(board for board in project.boards.list(get_all=True)
                                if board.name == name and isinstance(board, ProjectBoard))
        except (GitlabGetError, StopIteration):
            project.boards.create({
                'name': name,
            })
            issues_board = next(board for board in project.boards.list(get_all=True)
                                if board.name == name and isinstance(board, ProjectBoard))

        # Update project issues board
        issues_board.hide_backlog_list = hide_backlog_list
        issues_board.hide_closed_list = hide_closed_list
        issues_board.save()

        # Iterate through issue board lists
        for list_json in lists:

            # Create project issues board list
            board_list: ProjectBoardList
            try:
                board_list = next(board_list
                                  for board_list in issues_board.lists.list(get_all=True)
                                  if board_list.label['name'] == list_json['label']
                                  and isinstance(board_list, ProjectBoardList))
            except (GitlabGetError, IndexError, StopIteration):
                label = project.labels.get(list_json['label'],
                                           include_ancestor_groups=True)
                issues_board.lists.create({
                    'label_id': label.id,
                })
                board_list = next(board_list
                                  for board_list in issues_board.lists.list(get_all=True)
                                  if board_list.label['name'] == list_json['label']
                                  and isinstance(board_list, ProjectBoardList))

            # Update project issues board list
            if board_list.position != list_json['position']:
                board_list.position = list_json['position']
                board_list.save()

        # Prune project issues board lists
        for board_list in [
                board_list for board_list in issues_board.lists.list(get_all=True)
                if isinstance(board_list, ProjectBoardList)
                and board_list.label['name'] not in [item['label'] for item in lists]
        ]:
            board_list.delete()

        # Result
        return issues_board

    # Project set label, pylint: disable=too-many-arguments,too-many-positional-arguments
    def project_set_label(
        self,
        criteria: str,
        name: str,
        description: str,
        text_color: str,
        color: str,
        priority: Union[int, None],
    ) -> ProjectLabel:

        # Create project label
        project = self.project(criteria)
        label: ProjectLabel
        try:
            label = project.labels.get(name, include_ancestor_groups=False)
        except GitlabGetError:
            project.labels.create({
                'name': name,
                'description': description,
                'text_color': text_color,
                'color': color,
                'priority': priority,
            })
            label = project.labels.get(name, include_ancestor_groups=False)

        # Update project label
        label.description = description
        label.text_color = text_color
        label.color = color
        label.priority = priority
        label.save()

        # Result
        return label

    # URL
    @property
    def url(self) -> str:
        return str(self.__gitlab.api_url)

    # User
    def user(
        self,
        criteria: str,
    ) -> User:
        users = self.__gitlab.users.list(all=True, iterator=True, username=criteria)
        for user in users:
            return cast(User, user)
        raise RuntimeError(f'Could not find user {criteria}')

    # User name
    @property
    def username(self) -> str:
        if self.__gitlab.user:
            return str(self.__gitlab.user.username)
        return '/'
