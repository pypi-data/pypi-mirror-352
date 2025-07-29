from .types import CriteriaTestCase

GET_WEATHER_TOOL = {
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "Get current weather for a given location.",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "City and country e.g. Bogotá, Colombia",
                },
            },
            "required": ["location"],
            "additionalProperties": False,
        },
        "strict": True,
    },
}

ADD_PRODUCT_TOOL = {
    "type": "function",
    "function": {
        "name": "add_product",
        "description": "Add a new product",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {"description": "Name of the product", "type": "string"},
                "price": {"description": "Price of the product", "type": "number"},
                "inStock": {"description": "Availability status of the product.", "type": "boolean"},
                "tags": {
                    "description": "List of product tags",
                    "type": "array",
                    "items": {"type": "string"},
                },
            },
            "required": ["name", "price", "inStock", "tags"],
            "additionalProperties": False,
        },
        "strict": True,
    },
}

TOOL_CALL_DATA: dict[str, CriteriaTestCase] = {
    "tool_call_get_weather": CriteriaTestCase(
        id="tool_call_get_weather",
        request_data={
            "messages": [
                {
                    "role": "user",
                    "content": "What is the weather in San Francisco?",
                },
            ],
            "tools": [GET_WEATHER_TOOL],
        },
        criteria="tool_call",
        criteria_params={
            "tool_calls": [
                {
                    "function": {
                        "name": "get_weather",
                        "arguments": '{"location":"San Francisco"}',
                    },
                },
            ],
        },
    ),
    "tool_call_get_weather_custom_sp": CriteriaTestCase(
        id="tool_call_get_weather_custom_sp",
        request_data={
            "messages": [
                {
                    "role": "system",
                    "content": "You are a helpful assistant that can get the weather for a given location.",
                },
                {
                    "role": "user",
                    "content": "What is the weather in San Francisco?",
                },
            ],
            "tools": [GET_WEATHER_TOOL],
        },
        criteria="tool_call",
        criteria_params={
            "tool_calls": [
                {
                    "function": {
                        "tool_call_id": "1",
                        "name": "get_weather",
                        "arguments": '{"location":"San Francisco"}',
                    },
                },
            ],
        },
    ),
    "tool_call_add_product_array_params": CriteriaTestCase(
        id="tool_call_add_product_array_params",
        request_data={
            "messages": [
                {
                    "role": "user",
                    "content": "Please add a new product with name 'Widget', price 19.99, in stock, "
                    "and tags ['new', 'sale'] and give me the product id.",
                },
            ],
            "tools": [ADD_PRODUCT_TOOL],
        },
        criteria="tool_call",
        criteria_params={
            "tool_calls": [
                {
                    "function": {
                        "name": "add_product",
                        "arguments": '{"name":"Widget","price":19.99,"inStock":true,"tags":["new","sale"]}',
                    }
                }
            ],
        },
    ),
}
