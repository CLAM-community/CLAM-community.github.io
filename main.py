from pydantic import BaseModel
from typing import Literal
import yaml
from pathlib import Path

ZULIP_COMMUNITY_URL = ...
PLATFORM = Literal["zulip", "email", "github", "linkedin"]
DATA_FOLDER = Path("data")
ROLE = Literal["steering", "moderator"]


def get_social_icon(platform: PLATFORM) -> str:
    icons = {
        "zulip": "fa-brands fa-zulip",
        "email": "fa-solid fa-envelope",
        "github": "fa-brands fa-github",
        "linkedin": "fa-brands fa-linkedin",
    }
    return icons.get(platform, "fa-solid fa-user")


class SocialAccount(BaseModel):
    """A model representing a social media account."""

    platform: PLATFORM
    url: str

    def get_markdown(self) -> str:
        return f"<a class='{get_social_icon(self.platform)}' href='{self.url}'></a>"


class Person(BaseModel):
    """A model representing a person in the community."""

    name: str
    role: ROLE
    socials: list[SocialAccount]
    preferred_method_of_contact: str

    def to_card(self) -> str:
        return (
            f"<div>{self.name} "
            f"({' '.join(social.get_markdown() for social in self.socials)}) "
            f"{self.preferred_method_of_contact}</div>"
        )


def render_people_to_grid(people: list[Person]) -> str:
    cards = "\n".join(person.to_card() for person in people)
    return f'<div class="grid cards">\n\n{cards}\n\n</div>'


def get_people() -> list[Person]:
    """Load people from the YAML file."""
    people_yaml_path = DATA_FOLDER / "people.yaml"
    with open(people_yaml_path, "r") as f:
        people_data = yaml.safe_load(f)
    return [Person(**person) for person in people_data["person"]]


PEOPLE = get_people()


def define_env(env):
    """
    Mkdocs hook for the variables, macros and filters.
    """

    @env.macro
    def render_role_grid(role: ROLE) -> str:
        "Render people with their roles"
        return render_people_to_grid(
            [person for person in PEOPLE if person.role == role]
        )
