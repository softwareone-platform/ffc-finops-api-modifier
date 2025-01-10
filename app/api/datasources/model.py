from pydantic import BaseModel


class CreateDatasource(BaseModel):
    name: str
    type: str
    config: dict[str, str]
    auto_import: bool
    process_recommendations: bool
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


class DatasourceResponse(BaseModel):
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
