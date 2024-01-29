"""
File for longer messages or messages which often repeats.
"""

# Long messages
# TODO: provide link
CONFIG_FILE_NOT_FOUND_DEFAULT_LOCATION = (
    "Forgit config file not found in ~/.config directory. Please create a "
    "`forgit.yaml` file and specify your configuration there. More information about "
    "config file on TODO: link"
)
DIFF_STORAGE_CONFIG_ERROR = (
    "Diffs must be stored somewhere. Please specify a path, where to store generated "
    "diffs, enable `make_pr_comments` or disable `make_diffs` to not make diffs at all."
)
DIFF_NOT_ENABLED_ERROR = (
    "{enabled_options} {grammar} enabled, but you disabled making diffs. Please set "
    "`make_diffs` to true in the config file or disable the {enabled_options}."
)


# Repeated messages
USE_SUBCLASS = "Use subclass instead."
NOT_IMPLEMENTED = "This function/method is not yet implemented."

# PR templates
OPENED_PR_AS_ISSUE_TITLE = "[forgit] Filling in a blank issue for an opened PR#{pr_id}"
HEADER_TEMPLATE = (
    "Original {what}: {link}\n" "Opened: {date}\n" "Opened by: {user}\n --- \n"
)
OPENED_PR_HEADER_TEMPLATE = (
    HEADER_TEMPLATE + "This PR was filled with blank issue to preserve ID."
)
