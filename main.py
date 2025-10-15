import logging
from pydantic import BaseModel
from typing import Literal
import yaml
from pathlib import Path

# Initialize logger for robust error reporting
logger = logging.getLogger(__name__)

PLATFORM = Literal["zulip", "email", "github", "linkedin"]
DATA_FOLDER = Path("data")
ROLE = Literal["steering", "moderator", "project-parcels"]


def get_social_icon(platform: PLATFORM) -> str:
    """
    Returns the Font Awesome icon class for a given social platform.
    Provides a default icon if the platform is not recognized.
    """
    icons = {
        "zulip": "fa-brands fa-zulip",
        "email": "fa-solid fa-envelope",
        "github": "fa-brands fa-github",
        "linkedin": "fa-brands fa-linkedin",
    }
    return icons.get(platform, "fa-solid fa-user")


class SocialAccount(BaseModel):
    """
    Represents a social media account with its platform and URL.
    """
    platform: PLATFORM
    url: str

    def get_markdown(self) -> str:
        """
        Generates a Markdown link for the social account.
        """
        return f"[{self.platform}]({self.url})"


class Person(BaseModel):
    """
    Represents a person with their name, roles, social accounts, and preferred contact method.
    """
    name: str
    roles: list[ROLE]
    socials: list[SocialAccount]
    preferred_method_of_contact: str

    def to_card(self) -> str:
        """
        Renders the person's information into a Markdown card format.
        Social links are only displayed if they exist.
        """
        social_links = ", ".join(social.get_markdown() for social in self.socials)
        
        # Prepare the middle block with social links or just spacing if no links exist
        if social_links:
            # If social links are present, format them with parentheses and surrounding newlines
            middle_block = f"\n\n({social_links})\n"
        else:
            # If no social links, maintain consistent vertical spacing with two newlines
            middle_block = "\n\n"

        return f"""   - **{self.name}**
    
    ---
{middle_block}    Preferred contact: {self.preferred_method_of_contact}
    """


def render_people_to_grid(people: list[Person]) -> str:
    """
    Renders a list of Person objects into a Markdown grid of cards,
    sorted alphabetically by person's name (case-insensitively).
    """
    # Sort people case-insensitively by name as per the plan.
    sorted_people = sorted(people, key=lambda p: p.name.lower())
    cards = "\n".join(person.to_card() for person in sorted_people)
    return f'<div class="grid cards" markdown>\n\n{cards}\n\n</div>'


def get_people() -> list[Person]:
    """
    Loads person data from the people.yaml file, handling potential errors robustly.
    Returns a list of Person objects. In case of errors, logs the issue and returns
    an empty list to prevent site generation from failing entirely.
    """
    people_yaml_path = DATA_FOLDER / "people.yaml"
    people_list: list[Person] = []
    try:
        # Use explicit utf-8 encoding for reliable file reading
        with open(people_yaml_path, "r", encoding="utf-8") as f:
            people_data = yaml.safe_load(f)

        # Validate the overall structure of the YAML data
        if not isinstance(people_data, dict) or "person" not in people_data or not isinstance(people_data["person"], list):
            logger.error(
                f"Invalid people.yaml format: Expected a dictionary with a 'person' key containing a list. "
                f"Path: {people_yaml_path}"
            )
            return []

        # Iterate through each item and attempt to parse it as a Person
        for item in people_data["person"]:
            if not isinstance(item, dict):
                logger.warning(f"Skipping non-dictionary item found in people.yaml: {item}. Path: {people_yaml_path}")
                continue
            try:
                people_list.append(Person(**item))
            except Exception as e:
                # Catch Pydantic ValidationErrors and any other issues during object creation
                logger.error(f"Error parsing person data item in {people_yaml_path}: {item}. Error: {e}")
        return people_list

    except FileNotFoundError:
        logger.error(f"People data file not found: {people_yaml_path}")
        return []
    except yaml.YAMLError as e:
        logger.error(f"Error parsing YAML file {people_yaml_path}: {e}")
        return []
    except Exception as e:
        # Catch any other unexpected errors during file processing or initial data load
        logger.error(f"An unexpected error occurred while loading people data from {people_yaml_path}: {e}")
        return []


# Load people data once globally when the module is imported.
# This ensures data is loaded and parsed only once, and handles errors gracefully.
PEOPLE = get_people()


def define_env(env):
    """
    Mkdocs hook for registering variables, macros, and filters.
    """

    @env.macro
    def render_role_grid(role: ROLE) -> str:
        """
        Renders a Markdown grid of people associated with a specific role.
        """
        # Filter people based on their assigned roles
        people_with_role = [person for person in PEOPLE if role in person.roles]
        return render_people_to_grid(people_with_role)