from pathlib import Path
from subprocess import Popen, PIPE


class Diff:
    def __init__(self, new_hash: str, old_hash: str) -> None:
        self._new_hash = new_hash
        self._old_hash = old_hash

    def _generate_diff(self) -> str:
        process = Popen(["git", "diff", self._old_hash, self._new_hash], stdout=PIPE)
        stdout, stderr = process.communicate()
        if stderr:
            raise IOError(
                f"`git diff {self._old_hash} {self._new_hash}` failed. "
                f"Reason: {stderr.decode()}"
            )

        return stdout.decode()

    def place_diff_to_directory(self, directory: Path, pr_id: int) -> None:
        if not directory.is_dir():
            # this should be checked in the config schema
            raise FileNotFoundError(f"{directory} is not a directory.")

        with open(directory / f"{pr_id}.patch", "w") as patch_file:
            patch_file.write(self._generate_diff())
