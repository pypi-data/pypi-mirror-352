import random
from pathlib import Path

import git


def add_to_gitignore(file_path: str | Path) -> bool:
    """Add a file path to .gitignore. Creates .gitignore if it doesn't exist.

    Args:
        file_path (str | Path): Path to the file to be added to .gitignore

    Returns:
        bool: True if file was added, False if it was already in .gitignore

    """
    # Convert file_path to Path object if it's not already
    file_path = Path(file_path).resolve()

    # Try to find the git root directory
    try:
        repo = git.Repo(file_path.parent, search_parent_directories=True)
        git_root = Path(repo.git.rev_parse("--show-toplevel"))
    except (git.InvalidGitRepositoryError, git.NoSuchPathError):
        # If not in a git repository, use the parent directory of the file
        git_root = file_path.parent

    # Path to .gitignore
    gitignore_path = git_root / ".gitignore"

    # Get path to add to .gitignore - make it relative to git root
    try:
        # This ensures we get a proper relative path from git root
        relative_path = file_path.relative_to(git_root)
        path_to_add = str(relative_path)
    except ValueError:
        # If the file is not within the git root directory
        # (shouldn't happen in normal cases, but just to be safe)
        path_to_add = str(file_path)

    # Create .gitignore if it doesn't exist
    if not gitignore_path.exists():
        with open(gitignore_path, "w") as f:
            f.write(f"{path_to_add}\n")
        return True

    # Check if the file is already in .gitignore
    with open(gitignore_path) as f:
        lines = [line.strip() for line in f.readlines()]

    # If the path is already in .gitignore, do nothing
    if path_to_add in lines:
        return False

    # Otherwise, add the path to .gitignore
    with open(gitignore_path, "a") as f:
        f.write(f"{path_to_add}\n")

    return True


def get_default_branch(repo_path: Path) -> str:
    """Get the default branch name of a Git repository if possible.

    Args:
        repo_path (Path): Path to the Git repository.

    Returns:
        str: The default branch name.

    """
    try:
        repo = git.Repo(repo_path, search_parent_directories=True)
        default_branch = repo.remotes.origin.refs["HEAD"].reference.remote_head
        return default_branch
    except Exception:
        return "main"  # Fallback to main if unable to determine


def generate_name():
    """Generate a random name consisting of an adjective, a noun, and a number."""
    adj = random.choice(adjectives)
    noun = random.choice(nouns)
    num = random.randint(1, 99)
    return f"{adj}_{noun}_{num}"


adjectives = [
    "adventurous",
    "agile",
    "alert",
    "amazing",
    "ambitious",
    "ancient",
    "angry",
    "anxious",
    "awesome",
    "brave",
    "bright",
    "calm",
    "careful",
    "charming",
    "cheerful",
    "clever",
    "colorful",
    "courageous",
    "creative",
    "curious",
    "daring",
    "dazzling",
    "delicate",
    "determined",
    "diligent",
    "dreamy",
    "eager",
    "elegant",
    "energetic",
    "enthusiastic",
    "fearless",
    "fierce",
    "flexible",
    "friendly",
    "funny",
    "gentle",
    "gifted",
    "graceful",
    "happy",
    "helpful",
    "honest",
    "humble",
    "imaginative",
    "independent",
    "innovative",
    "intelligent",
    "joyful",
    "kind",
    "lively",
    "lucky",
    "magical",
    "mysterious",
    "noble",
    "optimistic",
    "peaceful",
    "playful",
    "powerful",
    "quick",
    "quiet",
    "radiant",
    "rapid",
    "reliable",
    "resilient",
    "resourceful",
    "respectful",
    "robust",
    "romantic",
    "sharp",
    "shiny",
    "silent",
    "sincere",
    "skillful",
    "smart",
    "speedy",
    "strong",
    "stunning",
    "swift",
    "talented",
    "thoughtful",
    "tough",
    "trustworthy",
    "unique",
    "vibrant",
    "wise",
    "witty",
    "youthful",
    "zealous",
]

nouns = [
    "adventurer",
    "albatross",
    "anchor",
    "angel",
    "antelope",
    "artist",
    "astronaut",
    "badger",
    "bandit",
    "beacon",
    "bear",
    "beetle",
    "bison",
    "blossom",
    "breeze",
    "buffalo",
    "butterfly",
    "captain",
    "caravan",
    "cat",
    "champion",
    "cheetah",
    "cloud",
    "comet",
    "coral",
    "cougar",
    "crane",
    "crystal",
    "dancer",
    "dawn",
    "deer",
    "diamond",
    "dolphin",
    "dragon",
    "dreamer",
    "eagle",
    "ember",
    "falcon",
    "firebrand",
    "firefly",
    "flame",
    "fox",
    "gazelle",
    "gem",
    "giant",
    "glider",
    "glow",
    "griffin",
    "hawk",
    "hero",
    "horizon",
    "hurricane",
    "jaguar",
    "jewel",
    "kingfisher",
    "knight",
    "koala",
    "lion",
    "lizard",
    "lynx",
    "mammoth",
    "mariner",
    "mermaid",
    "meteor",
    "mirage",
    "monkey",
    "mountain",
    "mustang",
    "nebula",
    "nightingale",
    "ninja",
    "octopus",
    "onyx",
    "oracle",
    "otter",
    "owl",
    "panther",
    "parrot",
    "pegasus",
    "penguin",
    "phoenix",
    "pilot",
    "pirate",
    "plume",
    "puma",
    "quasar",
    "quokka",
    "raccoon",
    "ranger",
    "raven",
    "river",
    "robin",
    "rocket",
    "rose",
    "saber",
    "sailor",
    "sage",
    "scout",
    "shadow",
    "shark",
    "siren",
    "skipper",
    "sky",
    "sparrow",
    "spirit",
    "sprite",
    "star",
    "storm",
    "sunbeam",
    "swallow",
    "swift",
    "tiger",
    "traveler",
    "turtle",
    "unicorn",
    "viper",
    "voyager",
    "warrior",
    "wave",
    "whale",
    "willow",
    "wind",
    "wolf",
    "wombat",
    "zephyr",
]
