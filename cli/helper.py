def print_pydantic_error(data):
    for err in data["detail"]:
        field_name = err["loc"][-1]
        message = err["msg"]
        print(f"'{field_name}': {message}")
