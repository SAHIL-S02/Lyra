from app.tools.system_tools import (
    GetCurrentTimeTool,
    GetSystemInfoTool,
)


def main() -> None:
    print("=== Lyra System Tools Test ===")

    time_tool = GetCurrentTimeTool()

    print("\n1. Current time")

    time_result = time_tool.execute({})

    print("Success:", time_result.success)
    print("Data   :", time_result.data)
    print("Error  :", time_result.error)

    assert time_result.success is True
    assert "formatted" in time_result.data

    system_tool = GetSystemInfoTool()

    print("\n2. System information")

    system_result = system_tool.execute({})

    print("Success:", system_result.success)
    print("Data   :", system_result.data)
    print("Error  :", system_result.error)

    assert system_result.success is True
    assert "system" in system_result.data
    assert "python_version" in system_result.data

    print("\nSystem tools test passed.")


if __name__ == "__main__":
    main()
