import asyncio
import json
import os
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client
from openai import AsyncOpenAI


# Start server.py with the same Python environment as this client
server_params = StdioServerParameters(
    command=sys.executable,
    args=[str(Path(__file__).resolve().with_name("server.py"))],
)


def required_env(name):
    """Read a required environment variable."""
    value = os.getenv(name)

    if not value or not value.strip():
        raise ValueError(f"Missing environment variable: {name}")

    return value.strip()


def convert_to_llm_tool(tool):
    """Convert an MCP tool to the Chat Completions tool format."""
    return {
        "type": "function",
        "function": {
            "name": tool.name,
            "description": tool.description or "",
            "parameters": tool.inputSchema,
        },
    }


async def call_llm(client, model, messages, llm_tools):
    """Send the conversation and available tools to the model."""
    options = {}

    if llm_tools:
        options["tools"] = llm_tools

    return await client.chat.completions.create(
        model=model,
        messages=messages,
        max_completion_tokens=1000,
        **options,
    )


async def run():
    # OpenAI configuration
    api_key = required_env("OPENAI_API_KEY")
    model = required_env("OPENAI_MODEL")

    # Launch the MCP server and open communication
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # List available prompts
            print("\nLISTING PROMPTS")
            prompts = await session.list_prompts()

            for prompt in prompts.prompts:
                print("Prompt:", prompt.name)

            # Preview a prompt without executing its instructions
            if any(p.name == "explain_addition" for p in prompts.prompts):
                prompt_result = await session.get_prompt(
                    "explain_addition",
                    arguments={"a": "5", "b": "3"},
                )

                print("\nPROMPT PREVIEW")

                for message in prompt_result.messages:
                    if isinstance(message.content, types.TextContent):
                        print(message.content.text)

            # List resources with fixed URIs
            print("\nLISTING RESOURCES")
            resources = await session.list_resources()

            for resource in resources.resources:
                print("Resource:", resource.name)
                print("URI:", resource.uri)

            # List resource templates
            print("\nLISTING RESOURCE TEMPLATES")
            templates = await session.list_resource_templates()

            for template in templates.resourceTemplates:
                print("Template:", template.name)
                print("URI template:", template.uriTemplate)

            # Read the greeting resource if available
            if any(
                template.uriTemplate == "greeting://{name}"
                for template in templates.resourceTemplates
            ):
                print("\nREADING RESOURCE")
                greeting = await session.read_resource("greeting://Rayan")

                for item in greeting.contents:
                    if isinstance(item, types.TextResourceContents):
                        print(item.text)

            # Discover tools and convert their definitions
            print("\nLISTING TOOLS")
            tools_result = await session.list_tools()

            available_names = {
                tool.name for tool in tools_result.tools
            }

            llm_tools = [
                convert_to_llm_tool(tool)
                for tool in tools_result.tools
            ]

            for tool in tools_result.tools:
                print("Tool:", tool.name)
                print("Description:", tool.description)
                print("Inputs:", tool.inputSchema.get("properties", {}))

            # Ask the user a question
            question = await asyncio.to_thread(
                input,
                "\nYour question (Enter for 'Add 2 to 20'): ",
            )
            question = question.strip() or "Add 2 to 20"

            messages = [
                {
                    "role": "system",
                    "content": (
                        "You are a calculator assistant. "
                        "Accept arithmetic requests written as expressions or in natural language. "
                        "Use the available tools to perform calculations. "
                        "If an operation has no suitable tool, explain that it is not supported yet. "
                        "If information is missing, ask for clarification. "
                        "For unrelated requests, explain that you only handle arithmetic. "
                        "Never invent tool results. Keep answers brief."
                    ),
                },
                {
                    "role": "user",
                    "content": question,
                },
            ]

            # Connect directly to OpenAI, not Azure
            async with AsyncOpenAI(
                api_key=api_key,
                base_url="https://api.openai.com/v1",
            ) as llm_client:

                # Allow several tool rounds, with a fixed limit
                for _ in range(6):
                    print("\nCALLING LLM")

                    response = await call_llm(
                        llm_client,
                        model,
                        messages,
                        llm_tools,
                    )

                    message = response.choices[0].message

                    # No tool calls: display the model's answer
                    if not message.tool_calls:
                        print(
                            "\nASSISTANT:",
                            message.content or "(No text returned.)",
                        )
                        return

                    # Keep the assistant's tool requests in the history
                    messages.append(
                        {
                            "role": "assistant",
                            "content": message.content,
                            "tool_calls": [
                                {
                                    "id": call.id,
                                    "type": "function",
                                    "function": {
                                        "name": call.function.name,
                                        "arguments": call.function.arguments,
                                    },
                                }
                                for call in message.tool_calls
                            ],
                        }
                    )

                    # Execute the requested tools through MCP
                    for call in message.tool_calls:
                        name = call.function.name

                        try:
                            if name not in available_names:
                                raise ValueError(
                                    f"Unknown tool requested: {name}"
                                )

                            arguments = json.loads(
                                call.function.arguments
                            )

                            if not isinstance(arguments, dict):
                                raise ValueError(
                                    "Tool arguments must be a JSON object."
                                )

                        except (ValueError, TypeError) as error:
                            tool_output = json.dumps(
                                {
                                    "isError": True,
                                    "error": str(error),
                                }
                            )
                            print("INVALID TOOL REQUEST:", error)

                        else:
                            print(
                                f"CALLING TOOL: {name}({arguments})"
                            )

                            result = await session.call_tool(
                                name,
                                arguments=arguments,
                            )

                            tool_output = result.model_dump_json(
                                exclude_none=True
                            )

                            print(
                                "TOOL ERROR:"
                                if result.isError
                                else "TOOL RESULT:"
                            )

                            for item in result.content:
                                if isinstance(item, types.TextContent):
                                    print(item.text)

                        # Match each result to its original tool call
                        messages.append(
                            {
                                "role": "tool",
                                "tool_call_id": call.id,
                                "content": tool_output,
                            }
                        )

                print(
                    "\nStopped: maximum number of model calls reached."
                )


if __name__ == "__main__":
    asyncio.run(run())