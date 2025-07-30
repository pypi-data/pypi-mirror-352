from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from resemu.models.resume import Resume
from resemu.models.utils import clean_url_display, extract_github_username, escape_latex


def generate_latex(resume: Resume, template_name: str = "engineering") -> str:
    template_dir = Path(__file__).parent.parent / "templates"

    env = Environment(
        loader=FileSystemLoader(template_dir),
        trim_blocks=True,
        lstrip_blocks=True,
        variable_start_string="<<",
        variable_end_string=">>",
        block_start_string="<%",
        block_end_string="%>",
        comment_start_string="<#",
        comment_end_string="#>",
        finalize=escape_latex,
    )

    env.filters["github_username"] = extract_github_username
    env.filters["clean_url"] = clean_url_display

    template = env.get_template(f"{template_name}.tex.j2")

    return template.render(
        contact=resume.contact,
        summary=resume.summary,
        skills=resume.skills,
        experience=resume.experience,
        projects=resume.projects,
        education=resume.education,
    )
