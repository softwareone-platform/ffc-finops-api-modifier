from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class AddCloudAccount(BaseModel):
    name: str
    type: str
    config: dict[str, Any]
    auto_import: bool = Field(default=True)
    process_recommendations: bool = Field(default=True)
    org_id: str
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "AWS HQ",
                    "type": "aws_cnr",
                    "config": {
                        "bucket_name": "opt_bucket",
                        "access_key_id": "key_id",
                        "secret_access_key": "secret",
                    },
                    "auto_import": False,
                    "process_recommendations": False,
                }
            ]
        }
    }


class AddCloudAccountResponse(BaseModel):
    name: str
    type: str
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "AWS HQ",
                    "type": "aws_cnr",
                    "config": {
                        "bucket_name": "opt_bucket",
                        "access_key_id": "key_id",
                        "secret_access_key": "secret",
                    },
                    "auto_import": True,
                    "process_recommendations": True,
                }
            ]
        }
    }
