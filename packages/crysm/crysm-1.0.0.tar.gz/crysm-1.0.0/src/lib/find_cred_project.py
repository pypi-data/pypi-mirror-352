from pathlib import Path


class NoProjectFound(Exception):
    pass


def is_cred_project(pathy: Path) -> bool:
    if (pathy / "cRED_log.txt").exists():
        return True
    return False


def find_cred_recursive(initial_guess: Path) -> Path:
    if is_cred_project(initial_guess):
        return initial_guess
    elif initial_guess.parent == initial_guess:
        # Root directory only
        raise NoProjectFound

    return find_cred_recursive(initial_guess.parent)


def find_cred_project(initial_guess: Path = Path()) -> Path:
    try:
        found_path = find_cred_recursive(initial_guess.absolute())
        print(f"Using cred project {found_path}")
        return found_path
    except NoProjectFound:
        pass  # If we reraise here the error call stack is long bcs of recursion
    raise NoProjectFound(
        f"{initial_guess.absolute()} not detected as a cRED project. Did you delete the cRED_log.txt file?"
    )
