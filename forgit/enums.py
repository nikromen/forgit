from enum import Enum


class TargetTypes(Enum):
    issue = 1
    pr = 2
    release = 3


# TODO: better name
class PostType(str, Enum):
    pr = "PR"
    issue = "issue"
