import json
import re
from typing import Optional, cast, Any
from openai import AsyncOpenAI
from rich.live import Live
from rich.markdown import Markdown

from config import settings
from core.tools import TOOL_SCHEMAS, WRITE_TOOLS, execute_tool
from core.context import build_context, trim_history, compress_workflow_in_history
from core.prompt import build_system_prompt
from core.validator import validate_workflow
from packages.cli.display import (
    show_spinner,
    show_tool_call,
    confirm,
    show_error,
    show_success,
    stream_text,
)
from packages.cli.session import save_turn, get_session_id
from storage import log_workflow


nim_api_key = settings.NIM_API_KEY.strip()
client = AsyncOpenAI(
    api_key=nim_api_key or settings.OPENAI_API_KEY,
    base_url=settings.NIM_BASE_URL if nim_api_key else None,
)


def extract_workflow_json(text: str) -> Optional[dict]:
    pattern = r"```json\s*([\s\S]*?)```"
    match = re.search(pattern, text)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass
    pattern2 = r'\{[\s\S]*"nodes"[\s\S]*\}'
    match2 = re.search(pattern2, text)
    if match2:
        try:
            return json.loads(match2.group())
        except json.JSONDecodeError:
            pass
    return None


async def run_agent(
    user_message: str,
    messages: list,
    workflow_context: Optional[str] = None,
    dry_run: bool = False,
):
    session_id = get_session_id()
    max_retries = 3

    context = await build_context(user_message)
    system_prompt = await build_system_prompt(
        user_message,
        context.get("relevant_nodes", []),
        context.get("credentials", []),
        context.get("memory", {}),
        workflow_context,
    )

    messages.insert(0, {"role": "system", "content": system_prompt})
    messages = await trim_history(messages)

    for attempt in range(max_retries):
        with show_spinner("Thinking..."):
            response = await client.chat.completions.create(
                model=settings.MODEL,
                messages=messages,
                tools=cast(Any, TOOL_SCHEMAS),
                tool_choice="auto",
                stream=False,
            )

        choice = response.choices[0]
        assistant_msg = choice.message

        if assistant_msg.tool_calls:
            messages.append(
                {
                    "role": "assistant",
                    "content": assistant_msg.content or "",
                    "tool_calls": [tc.model_dump() for tc in assistant_msg.tool_calls],
                }
            )
            save_turn(
                "assistant",
                assistant_msg.content or "",
                tool_calls=[tc.model_dump() for tc in assistant_msg.tool_calls],
            )

            for tc in assistant_msg.tool_calls:
                tool_name = tc.function.name
                try:
                    args = json.loads(tc.function.arguments)
                except json.JSONDecodeError:
                    args = {}

                show_tool_call(tool_name, args)

                if tool_name in WRITE_TOOLS and not dry_run:
                    if tool_name == "delete_workflow":
                        wf_name = args.get("workflow_name", "unknown")
                        if not confirm(
                            f"Delete workflow '{wf_name}'? Type the name to confirm:"
                        ):
                            tool_result = "User cancelled deletion"
                            messages.append(
                                {
                                    "role": "tool",
                                    "tool_call_id": tc.id,
                                    "content": tool_result,
                                }
                            )
                            save_turn(
                                "tool",
                                tool_result,
                                tool_results=[
                                    {"tool_call_id": tc.id, "content": tool_result}
                                ],
                            )
                            continue
                    elif tool_name in ("create_workflow", "update_workflow"):
                        wf_json_str = args.get("workflow_json", "{}")
                        try:
                            wf_json = json.loads(wf_json_str)
                        except json.JSONDecodeError:
                            wf_json = {}
                        if not confirm(f"Apply workflow changes?"):
                            tool_result = "User cancelled"
                            messages.append(
                                {
                                    "role": "tool",
                                    "tool_call_id": tc.id,
                                    "content": tool_result,
                                }
                            )
                            save_turn(
                                "tool",
                                tool_result,
                                tool_results=[
                                    {"tool_call_id": tc.id, "content": tool_result}
                                ],
                            )
                            continue

                    with show_spinner(f"Executing {tool_name}..."):
                        tool_result = await execute_tool(tool_name, args)
                else:
                    with show_spinner(f"Executing {tool_name}..."):
                        tool_result = await execute_tool(tool_name, args)

                messages.append(
                    {"role": "tool", "tool_call_id": tc.id, "content": str(tool_result)}
                )
                save_turn(
                    "tool",
                    str(tool_result),
                    tool_results=[{"tool_call_id": tc.id, "content": str(tool_result)}],
                )

                if tool_name in ("create_workflow", "update_workflow"):
                    try:
                        wf_result = (
                            json.loads(tool_result)
                            if isinstance(tool_result, str)
                            else tool_result
                        )
                        wf_id = wf_result.get("id", "")
                        wf_name = wf_result.get("name", "")
                        await log_workflow(
                            wf_id,
                            wf_name,
                            "created" if tool_name == "create_workflow" else "updated",
                            user_message,
                            session_id,
                        )
                    except:
                        pass

            messages = compress_workflow_in_history(messages)
            continue

        final_text = assistant_msg.content or ""
        messages.append({"role": "assistant", "content": final_text})
        save_turn("assistant", final_text)

        wf_json = extract_workflow_json(final_text)
        if wf_json and not dry_run:
            error = await validate_workflow(wf_json)
            if error:
                messages.append(
                    {
                        "role": "user",
                        "content": f"Validation error: {error}. Fix the JSON and retry.",
                    }
                )
                continue

        with Live(Markdown(""), console=None, refresh_per_second=10) as live:
            stream_text(final_text)

        return final_text

    return "Failed to generate valid response after 3 attempts"
