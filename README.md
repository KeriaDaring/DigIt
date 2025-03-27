# DigIt: An MCP-Enabled Agent with Dora Dataflow and MOFA Framework

## Introduction

**DigIt** is an agent that implements the **Model Context Protocol [MCP](https://github.com/modelcontextprotocol/servers)** to facilitate interaction and context management within dataflows. This project integrates an MCP functional agent within the **[Dora](https://dora-rs.ai/)** dataflow framework and leverages the **[MOFA](https://github.com/moxin-org/mofa)** Python framework for its development, providing a structured and efficient way to manage context in complex processing pipelines.
## Installation

Follow these steps to set up and run DigIt:

### 1. Install Conda Environment

1.  Download and install Conda from the official website: [Need official download link here]
2.  Create a new conda environment:
    ```bash
    conda create -n mofa python=3.10
    ```
3.  Activate the newly created environment:
    ```bash
    conda activate mofa
    ```
    All subsequent commands should be executed within this activated conda environment.

### 2. Install Rust

1.  Install Rust using the following command:
    ```bash
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
    ```
    Follow the on-screen instructions to complete the installation.

### 3. Install Dora

1.  Install the Dora command-line interface (CLI) using Cargo:
    ```bash
    cargo install dora-cli
    ```
    Ensure that Rust's Cargo package manager is installed and configured correctly.

### 4. Install MOFA Environment

1.  Clone the MOFA repository:
    ```bash
    git clone https://github.com/moxin-org/mofa.git
    ```
2.  Navigate to the Python directory within the MOFA repository:
    ```bash
    cd mofa/python
    ```
3.  Install MOFA in editable mode:
    ```bash
    pip install -e .
    ```
4.  Go back to the root of the MOFA repository:
    ```bash
    cd ..
    ```

### 5. Clone This Project

1.  Clone the DigIt repository:
    ```bash
    git clone https://github.com/KeriaDaring/DigIt.git
    ```
2.  Navigate to the DigIt project directory:
    ```bash
    cd DigIt
    ```
3.  Install the project dependencies:
    ```bash
    pip install -r requirement.txt
    ```

### 6. Configure API Keys

1.  Edit the API key in the following configuration files:
    * `./agent/mcp-llm/mcp_llm/configs/chat_session.yml`
    * `./configs/beaufy-context.yml`
    Replace the placeholder API key with your actual API key in both files.

### 7. Configure MCP Server

1.  Edit the MCP server configuration file: `./agent/mcp-llm/mcp_llm/configs/servers_config.json`

    **MCP Server Configuration:** Modify the `servers_config.json` file to match your local setup:

    ```json
    {
        "mcpServers": {
            "markdown_processor": {
                "command": "/path/to/your/uv",
                "args": [
                    "--directory",
                    "/path/to/your/project/mcp_servers",
                    "run",
                    "markdown_processor.py"
                ]
            }
        }
    }
    ```

    * Replace `/path/to/your/uv` with the actual path to your `uv` executable. You can find this path using the command `which uv`.
    * Replace `/path/to/your/project/mcp_servers` with the absolute path to the `mcp_servers` directory within your project.

### 8. Start the Project

1.  Destroy any existing Dora sessions:
    ```bash
    dora destroy
    ```
2.  Build and start the DigIt dataflow:
    ```bash
    dora up && dora build digit_dataflow.yml && dora start digit_dataflow.yml
    ```
3.  Open another terminal window.
4.  Activate the MOFA conda environment:
    ```bash
    conda activate mofa
    ```
5.  In this new terminal, you can now input your prompt to start using DigIt.

    ```bash
    # Example:
    Send You Task : 告诉我关于mofa框架的相关细节
    ```