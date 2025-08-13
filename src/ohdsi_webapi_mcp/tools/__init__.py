"""MCP tools package."""

# Vocabulary tools (client.vocabulary service)
# Cohort tools (client.cohorts service)
from .cohorts import (
    add_inclusion_rule,
    define_primary_criteria,
    estimate_cohort_size,
    validate_cohort_definition,
)

# Concept set tools (client.concept_sets service)
from .concept_sets import (
    create_concept_set,
    create_concept_set_from_search,
    get_concept_set_details,
    list_concept_sets,
)

# Info tools (client.info service)
from .info import (
    check_webapi_health,
    get_webapi_info,
    get_webapi_version,
)

# Jobs tools (client.jobs service)
from .jobs import (
    cancel_job,
    get_job_status,
    list_recent_jobs,
    monitor_job_progress,
)

# Persistence tools (MCP-specific functionality)
from .persistence import (
    clone_cohort,
    compare_cohorts,
    list_cohorts,
    load_existing_cohort,
    save_cohort_definition,
)

# Sources tools (client.sources service)
from .sources import (
    get_default_source,
    get_source_details,
    list_data_sources,
)
from .vocabulary import (
    browse_concept_hierarchy,
    get_concept_details,
    list_domains,
    list_vocabularies,
    search_concepts,
)

__all__ = [
    # Vocabulary tools
    "search_concepts",
    "get_concept_details",
    "browse_concept_hierarchy",
    "list_domains",
    "list_vocabularies",
    # Concept set tools
    "create_concept_set",
    "create_concept_set_from_search",
    "list_concept_sets",
    "get_concept_set_details",
    # Cohort tools
    "define_primary_criteria",
    "add_inclusion_rule",
    "validate_cohort_definition",
    "estimate_cohort_size",
    # Info tools
    "get_webapi_info",
    "get_webapi_version",
    "check_webapi_health",
    # Sources tools
    "list_data_sources",
    "get_source_details",
    "get_default_source",
    # Jobs tools
    "get_job_status",
    "list_recent_jobs",
    "cancel_job",
    "monitor_job_progress",
    # Persistence tools
    "save_cohort_definition",
    "load_existing_cohort",
    "list_cohorts",
    "compare_cohorts",
    "clone_cohort",
]
