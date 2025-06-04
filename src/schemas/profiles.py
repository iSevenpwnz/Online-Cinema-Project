from datetime import date

from fastapi import UploadFile, Form, File, HTTPException
from pydantic import BaseModel, field_validator, HttpUrl

from validation import (
    validate_name,
    validate_image,
    validate_gender,
    validate_birth_date
)


class ProfileCreateSchema(BaseModel):
    first_name: str
    last_name: str
    gender: str
    date_of_birth: date
    info: str
    avatar: UploadFile

    @classmethod
    def from_form(
            cls,
            first_name: str = Form(...),
            last_name: str = Form(...),
            gender: str = Form(...),
            date_of_birth: date = Form(...),
            info: str = Form(...),
            avatar: UploadFile = File(...)
    ) -> "ProfileCreateSchema":
        """
            Creates a ProfileCreateSchema instance from form data and an uploaded avatar file.
            
            Intended for use with FastAPI endpoints that accept multipart form data for profile creation.
            """
            return cls(
            first_name=first_name,
            last_name=last_name,
            gender=gender,
            date_of_birth=date_of_birth,
            info=info,
            avatar=avatar
        )

    @field_validator("first_name", "last_name")
    @classmethod
    def validate_name_field(cls, name: str) -> str:
        """
        Validates a name field and returns it in lowercase.
        
        Raises an HTTP 422 exception with detailed error information if the name is invalid.
        """
        try:
            validate_name(name)
            return name.lower()
        except ValueError as e:
            raise HTTPException(
                status_code=422,
                detail=[{
                    "type": "value_error",
                    "loc": ["first_name" if "first_name" in name else "last_name"],
                    "msg": str(e),
                    "input": name
                }]
            )

    @field_validator("avatar")
    @classmethod
    def validate_avatar(cls, avatar: UploadFile) -> UploadFile:
        """
        Validates the uploaded avatar image file.
        
        Raises:
            HTTPException: If the avatar file fails image validation, with status code 422 and error details.
        
        Returns:
            The validated avatar file.
        """
        try:
            validate_image(avatar)
            return avatar
        except ValueError as e:
            raise HTTPException(
                status_code=422,
                detail=[{
                    "type": "value_error",
                    "loc": ["avatar"],
                    "msg": str(e),
                    "input": avatar.filename
                }]
            )

    @field_validator("gender")
    @classmethod
    def validate_gender(cls, gender: str) -> str:
        """
        Validates the gender field and raises an HTTP 422 error if invalid.
        
        Returns:
            The validated gender string.
        
        Raises:
            HTTPException: If the gender value is invalid, with details about the error.
        """
        try:
            validate_gender(gender)
            return gender
        except ValueError as e:
            raise HTTPException(
                status_code=422,
                detail=[{
                    "type": "value_error",
                    "loc": ["gender"],
                    "msg": str(e),
                    "input": gender
                }]
            )

    @field_validator("date_of_birth")
    @classmethod
    def validate_date_of_birth(cls, date_of_birth: date) -> date:
        """
        Validates the date of birth field using an external birth date validator.
        
        Raises:
            HTTPException: If the date of birth is invalid, with status code 422 and error details.
        
        Returns:
            The validated date of birth.
        """
        try:
            validate_birth_date(date_of_birth)
            return date_of_birth
        except ValueError as e:
            raise HTTPException(
                status_code=422,
                detail=[{
                    "type": "value_error",
                    "loc": ["date_of_birth"],
                    "msg": str(e),
                    "input": str(date_of_birth)
                }]
            )

    @field_validator("info")
    @classmethod
    def validate_info(cls, info: str) -> str:
        """
        Validates and cleans the 'info' field by removing leading and trailing whitespace.
        
        Raises an HTTP 422 error if the resulting string is empty or contains only spaces.
        
        Args:
            info: The input string for the 'info' field.
        
        Returns:
            The trimmed 'info' string if valid.
        """
        cleaned_info = info.strip()
        if not cleaned_info:
            raise HTTPException(
                status_code=422,
                detail=[{
                    "type": "value_error",
                    "loc": ["info"],
                    "msg": "Info field cannot be empty or contain only spaces.",
                    "input": info
                }]
            )
        return cleaned_info


class ProfileResponseSchema(BaseModel):
    id: int
    user_id: int
    first_name: str
    last_name: str
    gender: str
    date_of_birth: date
    info: str
    avatar: HttpUrl
