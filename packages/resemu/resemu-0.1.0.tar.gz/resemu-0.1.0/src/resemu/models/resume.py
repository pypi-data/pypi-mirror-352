from typing import List
from datetime import date

from pydantic import BaseModel, HttpUrl, EmailStr, Field


class Contact(BaseModel):
    """Personal contact information and links."""

    name: str = Field(..., description="Full name")
    email: EmailStr = Field(..., description="Email address")
    portfolio: HttpUrl | None = Field(None, description="Portfolio website URL")
    github: HttpUrl | None = Field(None, description="GitHub profile URL")


class SkillCategory(BaseModel):
    """Professional work experience entry."""

    category: str = Field(
        ..., description="Skill category name (e.g., 'Programming Languages', 'Frameworks')"
    )
    skills: List[str] = Field(..., description="List of skills in this category")


class Experience(BaseModel):
    """Professional work experience entry."""

    title: str = Field(..., description="Job title")
    company: str = Field(..., description="Company name")
    location: str = Field(..., description="Job location (city, state/country)")
    start_date: date = Field(..., description="Start date (YYYY-MM-DD format)")
    end_date: date | None = Field(
        None, description="End date (YYYY-MM-DD format) - leave empty for current position"
    )
    bullets: List[str] = Field(
        ..., description="List of achievements, responsibilities, and key accomplishments"
    )


class Project(BaseModel):
    """Notable project to showcase."""

    title: str = Field(..., description="Project name")
    url: HttpUrl | None = Field(None, description="Project URL (GitHub, demo, etc.)")
    bullets: List[str] = Field(
        ..., description="List of project highlights, technologies used, and outcomes"
    )


class Education(BaseModel):
    """Educational background entry."""

    school: str = Field(..., description="School or university name")
    degree: str = Field(
        ..., description="Degree type (e.g., 'Bachelor of Science', 'Master of Arts')"
    )
    field: str = Field(
        ..., description="Field of study (e.g., 'Computer Science', 'Business Administration')"
    )
    graduation_date: date = Field(..., description="Graduation date (YYYY-MM-DD format)")


class Resume(BaseModel):
    """Complete resume data structure for generating resumes."""

    contact: Contact = Field(..., description="Personal contact information")
    summary: str | None = Field(None, description="Brief professional summary or career objective")
    skills: List[SkillCategory] = Field(
        ..., description="Categorized list of technical and professional skills"
    )
    experience: List[Experience] = Field(
        ..., description="Professional work experience in reverse chronological order"
    )
    projects: List[Project] = Field(
        ..., description="Notable projects that demonstrate skills and experience"
    )
    education: List[Education] = Field(
        ..., description="Educational background in reverse chronological order"
    )
