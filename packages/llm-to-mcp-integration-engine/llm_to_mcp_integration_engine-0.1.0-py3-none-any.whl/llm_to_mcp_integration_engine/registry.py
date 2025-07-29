class MockRegistry:
    def __init__(self):
        self.tools = {
            "tool1": [{"name": "param1", "type": "str", "required": True}, {"name": "param2", "type": "int", "required": False}],
            "tool2": [{"name": "param3", "type": "bool", "required": True}]
        }

    def get_tool(self, tool_name: str):
        return self.tools.get(tool_name)

mock_registry = MockRegistry()
