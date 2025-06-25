import json

def sanitize_data(data):
    """
    Sanitize the inventory data to make it serializable.
    Convert Ansible custom types to standard Python types.
    """
    try:
        return json.loads(json.dumps(data))
    except (TypeError, ValueError):
        if isinstance(data, dict):
            return {str(k): sanitize_data(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [sanitize_data(i) for i in data]
        else:
            return str(data)
