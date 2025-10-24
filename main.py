from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel

PLATFORM = Literal["zulip", "email", "github", "linkedin"]
DATA_FOLDER = Path("data")
ROLE = Literal["steering", "moderator", "project-parcels"]


def get_social_icon(platform: PLATFORM) -> str:
    icons = {
        "zulip": "fa-brands fa-zulip",
        "email": "fa-solid fa-envelope",
        "github": "fa-brands fa-github",
        "linkedin": "fa-brands fa-linkedin",
    }
    return icons.get(platform, "fa-solid fa-user")


class SocialAccount(BaseModel):
    platform: PLATFORM
    url: str

    def get_markdown(self) -> str:
        return f"[{self.platform}]({self.url})"


class Person(BaseModel):
    name: str
    roles: list[ROLE]
    socials: list[SocialAccount]
    preferred_method_of_contact: str

    def to_card(self) -> str:
        return f"""   - **{self.name}**

    ---

    ({", ".join(social.get_markdown() for social in self.socials)})

    Preferred contact: {self.preferred_method_of_contact}
    """


def render_people_to_grid(people: list[Person]) -> str:
    cards = "\n".join(person.to_card() for person in people)
    return f'<div class="grid cards" markdown>\n\n{cards}\n\n</div>'


def get_people() -> list[Person]:
    people_yaml_path = DATA_FOLDER / "people.yaml"
    with open(people_yaml_path) as f:
        people_data = yaml.safe_load(f)
    return [Person(**person) for person in people_data["person"]]


PEOPLE = get_people()


def define_env(env):
    """
    Mkdocs hook for the variables, macros and filters.
    """

    @env.macro
    def render_role_grid(role: ROLE) -> str:
        """Render people with their roles"""
        return render_people_to_grid(
            [person for person in PEOPLE if role in person.roles]
        )
