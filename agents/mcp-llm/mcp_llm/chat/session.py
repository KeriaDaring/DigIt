import logging

import colorama


from mcp_llm.mcp_server.server import Server
from mcp_llm.llm.llm import OpenAIClient
from mofa.agent_build.base.base_agent import MofaAgent
import asyncio
from collections import deque
import json
# Configure logging
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)

SYSTEM_MESSAGE = (
    """
You are an efficient and reliable assistant with access to the following tools:

{}

Based on the user's query, select the appropriate tool.

IMPORTANT: First you need to break the work into many steps and each steps is correspondent to one tool.When you need to use a tool, reply ONLY with a JSON object in the exact format below (without any extra text):
IMPORTANT: 必须保证这个列表的格式，才能保证程序正常运行
---
RETURN TYPE:
```json
[
    "tool": "tool-1-name",
    "arguments": {{
        "argument-name": "value you prefer"
    }},
    "tool": "tool-2-name",
    "arguments": {{
        "argument-name": "value you prefer"
    }},
    "tool": "tool-3-name",
    "arguments": {{
        "argument-name": "value you prefer"
    }},
    "tool": "tool-4-name",
    "arguments": {{
        "argument-name": "value you prefer"
    }},
]
```
RETURN TYPE END
---
After receiving a tool's response, process the information by:
1. Delivering a concise and clear summary.
2. Integrating only the most relevant details into a natural response.
3. Avoiding repetition of raw data.

Use only the tools defined above.
"""
)


class ChatSession:
    """Orchestrates the interaction between user, LLM, and tools."""

    def __init__(self, servers: list[Server], llm_client: OpenAIClient):
        self.servers: list[Server] = servers
        # self.inputs = inputs
        self.llm_client = llm_client
        self.messages = []

    async def cleanup_servers(self) -> None:
        """Clean up all servers properly."""
        print("begin to cleanup servers")
        cleanup_tasks = []
        for server in self.servers:
            # cleanup_tasks.append(asyncio.create_task(server.cleanup()))
            await server.cleanup()
        # if cleanup_tasks:
        #     try:
        #         await asyncio.gather(*cleanup_tasks, return_exceptions=False)
        #     except Exception:
        #         pass

    async def process_llm_response(self, llm_response: str) -> str:
        """Process the LLM response and execute tools if needed.

        Args:
            llm_response: The response from the LLM.

        Returns:
            The result of tool execution or the original response.
        """
        tool_calls: deque = deque()
        try:
            tool_calls: deque = deque(json.loads(llm_response))
        except Exception as e:
            pass
        results = []
        count = 0
        while tool_calls:
            next_tool_call = tool_calls.popleft()
            for server in self.servers:
                tools = await server.list_tools()
                if any(tool.name == next_tool_call["tool"] for tool in tools):
                    try:
                        result = await server.execute_tool(
                            next_tool_call["tool"], next_tool_call["arguments"]
                        )
                        if hasattr(result.content[0], "text"):
                            results.append(result.content[0].text)
                        else:
                            results.append(result.content[0][list(result.content.__dict__.values())[1]])
                            
                        count += 1
                        # print(results)
                        if isinstance(result, dict) and "progress" in result:
                            progress = result["progress"]
                            total = result["total"]
                            percentage = (progress / total) * 100
                            logging.info(
                                f"Progress: {progress}/{total} ({percentage:.1f}%)"
                            )

                        logging.info(f"Tool execution result: {result}")

                        break  # 退出循环，避免重复执行同一个工具
                    except Exception as e:
                        error_msg = f"Error executing tool: {str(e)}"
                        logging.error(error_msg)
                        return error_msg
                
            else:
                return f"No server found with tool: {next_tool_call['tool']}"
        return results

    async def initialize(self) -> bool:
        """Initialize servers and prepare the system message.

        Returns:
            bool: True if initialization was successful, False otherwise.
        """
        try:
            for server in self.servers:
                try:
                    print('begin to initialize:', server.name)
                    await server.initialize()
                except Exception as e:
                    logging.error(f"Failed to initialize server: {e}")
                    logging.error(e.__traceback__.tb_lineno)
                    # await self.cleanup_servers()
                    return False

            all_tools = []
            for server in self.servers:
                tools = await server.list_tools()
                all_tools.extend(tools)

            tools_description = "{"+"\n".join([tool.format_for_llm() for tool in all_tools])+"}"
            system_message = SYSTEM_MESSAGE.format(tools_description)
            # self.inputs['backstory'] = system_message
            self.messages = [{"role": "system", "content": system_message}]
            return True
        except Exception as e:
            logging.error(f"Initialization error: {e}")
            logging.error(e.__traceback__.tb_lineno)
            # await self.cleanup_servers()
            return False
    async def run(self, user_prompt: str) -> str:
        """Run a single prompt through the chat session.

        Args:
            user_prompt: The user's prompt to process.

        Returns:
            str: The final response from the assistant.
        """
        self.messages.append({"role": "user", "content": user_prompt})
            # llm_response = run_dspy_or_crewai_agent(self.inputs)
        llm_response = self.llm_client.get_response(self.messages)
        index = llm_response.find("[")
        rindex = llm_response.find("]")
        llm_response = llm_response[index:rindex + 1]
        print(llm_response)
        # print(llm_response)
        results = {}
        count = 0
        try:
            # self.messages.append({"role": "user", "content": user_prompt})
            # message = "".join(f"'role': '{item['role']}', 'content': '{item['content']}'" for item in self.messages)
            # self.inputs['task'] = user_prompt
            
            if llm_response == "[]":
                llm_response = "[{}]"
            while not llm_response == "[{}]":
                result = await self.process_llm_response(llm_response)
                # print(result)
                results[f'question_{count}'] = result
                count += 1
                self.messages.append({"role": "user", "content": f'根据第一次 prompt: {user_prompt}还需要哪些工具, 已经使用了{llm_response}, 如果没有请不要再进行请求，返回[]'})
                print("keeping inquiring tools")
                llm_response = self.llm_client.get_response(self.messages)
                index = llm_response.find("[")
                rindex = llm_response.find("]")
                llm_response = llm_response[index:rindex + 1]
                if llm_response == "[]":
                    llm_response = "[{}]"
                print(llm_response)
            print("no tools left to use!")
            
        except Exception as e:
            error_msg = f"Error processing prompt: {str(e)}"
            print(e.__traceback__.tb_lineno)
            logging.error(error_msg)
            return error_msg
        finally:
            return results
        
    async def start(self) -> None:
        """Main chat session handler."""
        try:
            init_success = await self.initialize()
            if not init_success:
                return

            while True:
                try:
                    user_input = input("input sth:")
                    self.messages.append({"role": "user", "content": user_input})

                    llm_response = await self.llm_client.get_response(self.messages)
                    logging.info(
                        f"\n{colorama.Fore.BLUE}Assistant: {llm_response}"
                        f"{colorama.Style.RESET_ALL}"
                    )


                    result = await self.process_llm_response(llm_response[llm_response.find('{'):llm_response.rfind("}")])

                    if result != llm_response:
                        self.messages.append(
                            {"role": "assistant", "content": llm_response}
                        )
                        self.messages.append({"role": "system", "content": result})

                        final_response = self.llm_client.get_response(self.messages)
                        logging.info(
                            f"\n{colorama.Fore.GREEN}Final response: {final_response}"
                            f"{colorama.Style.RESET_ALL}"
                        )
                        self.messages.append(
                            {"role": "assistant", "content": final_response}
                        )
                    else:
                        self.messages.append(
                            {"role": "assistant", "content": llm_response}
                        )

                except KeyboardInterrupt:
                    logging.info("process user_input error.")
                    break

        finally:
            await self.cleanup_servers()