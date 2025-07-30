from . import server
# import server
import asyncio
import os


def main():
    """Main entry point for the package."""
    asyncio.run(server.main())


# Optionally expose other important items at package level
main()
# os.environ["API_KEY"] = "HyENsa3tNVoIAb0HBLJTcVSAb2fdsN7l"
# os.environ["ASSISTANT_ID"] = "ay9y3OW4Pjkddd"
# os.environ["TOOL_DESC"] = "chat with yuanqi agent"
# os.environ["TOOL_NAME"] = "chat"
# arguments = {
#     "userID": "123",
#     "userPrompt":"你是谁"
# }
# server.yuanqi_chat(arguments)