#!/usr/bin/env python3

# Standard libraries
from typing import Dict, List, NamedTuple

# Modules libraries
from gitlab import Gitlab
from gitlab.exceptions import GitlabGetError, GitlabHttpError, GitlabListError
from gitlab.v4.objects import Project

# AccessLevels class, pylint: disable=too-few-public-methods
class AccessLevels:
    DISABLED: str = 'disabled'
    PRIVATE: str = 'private'
    ENABLED: str = 'enabled'

# MergeRequestsMethod class
class MergeRequestsMethod:
    ATTRIBUTE: str = 'merge_method'
    DEFAULT: str = 'Fast-forward'
    VALUES: Dict[str, str] = {
        'Merge': 'merge',
        'Semi-linear': 'rebase_merge',
        'Fast-forward': 'ff',
    }

# MergeRequestsPipelines class
class MergeRequestsPipelines:
    ATTRIBUTE: str = 'only_allow_merge_if_pipeline_succeeds'
    DEFAULT: bool = True

# MergeRequestsResolved class
class MergeRequestsResolved:
    ATTRIBUTE: str = 'only_allow_merge_if_all_discussions_are_resolved'
    DEFAULT: bool = True

# MergeRequestsSquash class
class MergeRequestsSquash:
    ATTRIBUTE: str = 'squash_option'
    DEFAULT: str = 'Allow'
    VALUES: Dict[str, str] = {
        'Do not allow': 'never',
        'Allow': 'default_off',
        'Encourage': 'default_on',
        'Require': 'default_on',
    }

# MergeRequestsSkipped class
class MergeRequestsSkipped:
    ATTRIBUTE: str = 'allow_merge_on_skipped_pipeline'
    DEFAULT: bool = True

# ProtectionLevels class
class ProtectionLevels:
    NO_ONE: str = 'no-one'
    ADMINS: str = 'admins'
    MAINTAINERS: str = 'maintainers'
    DEVELOPERS: str = 'developers'

    # Default
    @staticmethod
    def default() -> str:
        return ProtectionLevels.NO_ONE

    # Names
    @staticmethod
    def names() -> List[str]:
        return [
            ProtectionLevels.NO_ONE,
            ProtectionLevels.ADMINS,
            ProtectionLevels.MAINTAINERS,
            ProtectionLevels.DEVELOPERS,
        ]

# RolesCreateProjects class
class RolesCreateProjects:
    NO_ONE: str = 'noone'
    OWNER: str = 'owner'
    MAINTAINER: str = 'maintainer'
    DEVELOPER: str = 'developer'
    ADMINISTRATOR: str = 'administrator'

    # Default
    @staticmethod
    def default() -> str:
        return RolesCreateProjects.DEVELOPER

    # Names
    @staticmethod
    def names() -> List[str]:
        return [
            RolesCreateProjects.NO_ONE,
            RolesCreateProjects.OWNER,
            RolesCreateProjects.MAINTAINER,
            RolesCreateProjects.DEVELOPER,
            RolesCreateProjects.ADMINISTRATOR,
        ]

# RolesCreateSubgroups class
class RolesCreateSubgroups:
    OWNER: str = 'owner'
    MAINTAINER: str = 'maintainer'

    # Default
    @staticmethod
    def default() -> str:
        return RolesCreateSubgroups.MAINTAINER

    # Names
    @staticmethod
    def names() -> List[str]:
        return [
            RolesCreateSubgroups.OWNER,
            RolesCreateSubgroups.MAINTAINER,
        ]

# Visibility class, pylint: disable=too-few-public-methods
class Visibility:
    PRIVATE: str = 'private'
    INTERNAL: str = 'internal'
    PUBLIC: str = 'public'

# ProjectFeatureLevel class, pylint: disable=too-few-public-methods
class ProjectFeatureLevel(NamedTuple):
    key: str
    settings: Dict[str, str] = {
        Visibility.PRIVATE: AccessLevels.PRIVATE,
        Visibility.INTERNAL: AccessLevels.ENABLED,
        Visibility.PUBLIC: AccessLevels.ENABLED,
    }

# ProjectFeatures class, pylint: disable=too-few-public-methods
class ProjectFeatures:

    # Members
    cache_keys: List[str] = []
    cache_names: List[str] = []

    # Feature
    class Feature(NamedTuple):

        # Variables
        name: str
        access_level: List[ProjectFeatureLevel] = []
        enabled: List[str] = []
        tests: List[str] = []

    # Get
    @staticmethod
    def get(key: str) -> Feature:

        # Get feature object
        feature = getattr(ProjectFeatures, key)
        assert isinstance(feature, ProjectFeatures.Feature)
        return feature

    # Keys
    @staticmethod
    def keys() -> List[str]:

        # Evaluate keys
        if ProjectFeatures.cache_keys:
            return ProjectFeatures.cache_keys

        # Evaluate keys
        ProjectFeatures.cache_keys = [
            key for key in ProjectFeatures.__dict__
            if isinstance(getattr(ProjectFeatures, key), ProjectFeatures.Feature)
        ]
        return ProjectFeatures.cache_keys

    # Names
    @staticmethod
    def names() -> List[str]:

        # Evaluate names
        if ProjectFeatures.cache_names:
            return ProjectFeatures.cache_names

        # Evaluate names
        ProjectFeatures.cache_names = [
            ProjectFeatures.get(key).name for key in ProjectFeatures.__dict__
            if isinstance(getattr(ProjectFeatures, key), ProjectFeatures.Feature)
        ]
        return ProjectFeatures.cache_names

    # Project test feature, pylint: disable=too-many-branches
    @staticmethod
    def test(
        gitlab: Gitlab,
        project: Project,
        tests: List[str],
    ) -> bool:

        # Avoid without tests
        if not tests:
            return False

        # Iterate through tests
        try:
            for test in tests:

                # Handle CI/CD test
                if test == 'CI_CD':
                    test_ci_jobs = project.jobs.list(get_all=False)
                    test_ci_files = any(
                        'name' in item and item['name'] == '.gitlab-ci.yml'
                        for item in project.repository_tree(get_all=True) \
                    )
                    test_ci_token_access: bool = False
                    try:
                        test_ci_token_access = any(
                            'path_with_namespace' in item \
                            and isinstance(item, dict) \
                            and item['path_with_namespace'] != project.path_with_namespace \
                            for item in gitlab.http_get(
                                f'/projects/{project.id}/job_token_scope/allowlist',
                                get_all=True,
                            ) \
                        )
                    except GitlabHttpError:
                        test_ci_token_access = False
                    assert (test_ci_jobs or test_ci_files or test_ci_token_access)

                # Handle commits test
                elif test == 'COMMITS':
                    assert project.commits.list(get_all=False)

                # Handle environments test
                elif test == 'ENVIRONMENTS':
                    assert project.environments.list(get_all=False)

                # Handle forks test
                elif test == 'FORKS':
                    assert project.forks.list(get_all=False)

                # Handle Git LFS test
                elif test == 'GIT_LFS':
                    assert project.statistics['lfs_objects_size'] > 0

                # Handle issues test
                elif test == 'ISSUES':
                    assert project.issues.list(get_all=False)

                # Handle merge requests test
                elif test == 'MERGE_REQUESTS':
                    assert (project.mergerequests.list(get_all=False)
                            or len(project.branches.list(get_all=False)) > 1)

                # Handle packages test
                elif test == 'PACKAGES':
                    assert project.packages.list(get_all=False)

                # Handle pages test
                elif test == 'PAGES':
                    test_pages_jobs = any(
                        job.name == 'pages' for job in project.jobs.list(get_all=True))
                    assert test_pages_jobs

                # Handle releases test
                elif test == 'RELEASES':
                    assert project.releases.list(get_all=False)

                # Handle repositories test
                elif test == 'REPOSITORIES':
                    assert project.repositories.list(get_all=False)

                # Handle snippets test
                elif test == 'SNIPPETS':
                    assert project.snippets.list(get_all=False)

                # Handle wiki test
                elif test == 'WIKI':
                    assert project.wikis.list(get_all=False)

        # Handle failed test
        except (AssertionError, GitlabGetError, GitlabListError):
            return False

        # Result
        return True

    # Issues
    ISSUES = Feature(
        name='Issues',
        access_level=[
            ProjectFeatureLevel('issues_access_level'),
        ],
        enabled=[
            'issues_enabled',
        ],
        tests=[
            'ISSUES',
        ],
    )

    # Merge requests
    MERGE_REQUESTS = Feature(
        name='Merge requests',
        access_level=[
            ProjectFeatureLevel('merge_requests_access_level'),
        ],
        enabled=[
            'merge_requests_enabled',
        ],
        tests=[
            'MERGE_REQUESTS',
        ],
    )

    # Forks
    FORKS = Feature(
        name='Forks',
        access_level=[
            ProjectFeatureLevel('forking_access_level'),
        ],
        tests=[
            'FORKS',
        ],
    )

    # Git LFS
    GIT_LFS = Feature(
        name='Git LFS',
        enabled=[
            'lfs_enabled',
        ],
        tests=[
            'GIT_LFS',
        ],
    )

    # CI/CD
    CI_CD = Feature(
        name='CI/CD',
        access_level=[
            ProjectFeatureLevel('builds_access_level'),
        ],
        enabled=[
            'jobs_enabled',
        ],
        tests=[
            'CI_CD',
        ],
    )

    # Repository
    REPOSITORY = Feature(
        name='Repository',
        access_level=[
            ProjectFeatureLevel(
                'repository_access_level',
                {
                    Visibility.PRIVATE: AccessLevels.ENABLED,
                    Visibility.INTERNAL: AccessLevels.ENABLED,
                    Visibility.PUBLIC: AccessLevels.ENABLED,
                },
            ),
            ProjectFeatureLevel('merge_requests_access_level'),
            ProjectFeatureLevel('forking_access_level'),
            ProjectFeatureLevel('builds_access_level'),
        ],
        enabled=[
            'lfs_enabled',
            'jobs_enabled',
        ],
        tests=[
            'COMMITS',
        ],
    )

    # Container registry
    CONTAINER_REGISTRY = Feature(
        name='Container registry',
        enabled=[
            'container_registry_enabled',
        ],
        access_level=[
            ProjectFeatureLevel('container_registry_access_level'),
        ],
        tests=[
            'REPOSITORIES',
        ],
    )

    # Analytics
    ANALYTICS = Feature(
        name='Analytics',
        access_level=[
            ProjectFeatureLevel('analytics_access_level'),
        ],
        tests=[],
    )

    # Security and Compliance
    SECURITY_AND_COMPLIANCE = Feature(
        name='Security and Compliance',
        access_level=[
            ProjectFeatureLevel(
                'security_and_compliance_access_level', {
                    Visibility.PRIVATE: AccessLevels.PRIVATE,
                    Visibility.INTERNAL: AccessLevels.PRIVATE,
                    Visibility.PUBLIC: AccessLevels.PRIVATE,
                }),
        ],
        tests=[],
    )

    # Wiki
    WIKI = Feature(
        name='Wiki',
        enabled=[
            'wiki_enabled',
        ],
        access_level=[
            ProjectFeatureLevel('wiki_access_level'),
        ],
        tests=[
            'WIKI',
        ],
    )

    # Snippets
    SNIPPETS = Feature(
        name='Snippets',
        enabled=[
            'snippets_enabled',
        ],
        access_level=[
            ProjectFeatureLevel('snippets_access_level'),
        ],
        tests=[
            'SNIPPETS',
        ],
    )

    # Package registry
    PACKAGE_REGISTRY = Feature(
        name='Package registry',
        enabled=[
            'packages_enabled',
        ],
        tests=[
            'PACKAGES',
        ],
    )

    # Model experiments
    MODEL_EXPERIMENTS = Feature(
        name='Model experiments',
        access_level=[
            ProjectFeatureLevel('model_experiments_access_level'),
        ],
        tests=[],
    )

    # Model registry
    MODEL_REGISTRY = Feature(
        name='Model registry',
        access_level=[
            ProjectFeatureLevel('model_registry_access_level'),
        ],
        tests=[],
    )

    # Pages
    PAGES = Feature(
        name='Pages',
        access_level=[
            ProjectFeatureLevel(
                'pages_access_level', {
                    Visibility.PRIVATE: AccessLevels.PRIVATE,
                    Visibility.INTERNAL: AccessLevels.PRIVATE,
                    Visibility.PUBLIC: AccessLevels.ENABLED,
                })
        ],
        tests=[
            'PAGES',
        ],
    )

    # Monitor
    MONITOR = Feature(
        name='Monitor',
        access_level=[
            ProjectFeatureLevel('monitor_access_level'),
        ],
        tests=[],
    )

    # Environments
    ENVIRONMENTS = Feature(
        name='Environments',
        access_level=[
            ProjectFeatureLevel('environments_access_level'),
        ],
        tests=[
            'ENVIRONMENTS',
        ],
    )

    # Feature flags
    FEATURE_FLAGS = Feature(
        name='Feature flags',
        access_level=[
            ProjectFeatureLevel('feature_flags_access_level'),
        ],
        tests=[],
    )

    # Infrastructure
    INFRASTRUCTURE = Feature(
        name='Infrastructure',
        access_level=[
            ProjectFeatureLevel('infrastructure_access_level'),
        ],
        tests=[],
    )

    # Releases
    RELEASES = Feature(
        name='Releases',
        access_level=[
            ProjectFeatureLevel('releases_access_level'),
        ],
        tests=[
            'RELEASES',
        ],
    )

    # Service Desk
    SERVICE_DESK = Feature(
        name='Service Desk',
        enabled=[
            'service_desk_enabled',
        ],
        tests=[],
    )

    # Auto DevOps
    AUTO_DEVOPS = Feature(
        name='Auto DevOps',
        enabled=[
            'auto_devops_enabled',
        ],
        tests=[],
    )
