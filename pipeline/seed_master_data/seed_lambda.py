
from extract_transform import validate_match_master_data
from load_master import load_master_data


def lambda_handler(event, context):

    try:
        cleaned_metadata = validate_match_master_data(event)

        result = load_master_data(cleaned_metadata)

        return {
            "status": "success",
            "details": result
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
