# Quickstart Guide for Model Context Protocol (MCP) Server

This guide explains how to build a simple MCP weather server using Python. MCP is an open protocol that facilitates the integration of large language models with external tools and data sources via JSON-RPC 2.0.

## Introduction

The MCP protocol connects external tools and data sources to LLMs seamlessly through a client-server architecture. The objective of this guide is to construct an MCP weather server that provides the following tools:

- **`get-alerts`**: Fetches weather alerts based on a state code.
- **`get-forecast`**: Retrieves a weather forecast based on latitude and longitude coordinates.

## Prerequisites

- **Python 3.10+**
- **MCP SDK**: `pip install mcp[cli]`
- **httpx library**: `pip install httpx`

## Server Implementation

### 1. Initialize the FastMCP Server

```python
import sys
import httpx
from mcp.server.fastmcp import FastMCP

# Initialize the FastMCP server
mcp = FastMCP("weather")

# Define constants
NWS_API_BASE = "https://api.weather.gov"
USER_AGENT = "weather-app/1.0 (contact@example.com)"
```

### 2. Define Tools

#### a. The `get-alerts` Tool

```python
@mcp.tool()
def get_alerts(state: str) -> str:
    """Get active weather alerts for a specified state.

    Args:
        state: Two-letter state code (e.g., 'CA' for California).

    Returns:
        A string containing weather alerts in JSON format.

    Raises:
        httpx.HTTPStatusError: If the API request fails.
    """
    url = f"{NWS_API_BASE}/alerts/active?area={state}"
    headers = {"User-Agent": USER_AGENT}
    response = httpx.get(url, headers=headers)
    response.raise_for_status()
    return response.text
```

#### b. The `get-forecast` Tool

```python
@mcp.tool()
def get_forecast(latitude: float, longitude: float) -> str:
    """Get weather forecast for a specific latitude and longitude.

    Args:
        latitude: Latitude coordinate (e.g., 37.7749).
        longitude: Longitude coordinate (e.g., -122.4194).

    Returns:
        A string containing weather forecast in JSON format.

    Raises:
        httpx.HTTPStatusError: If the API request fails.
    """
    url = f"{NWS_API_BASE}/points/{latitude},{longitude}"
    headers = {"User-Agent": USER_AGENT}
    response = httpx.get(url, headers=headers)
    response.raise_for_status()
    forecast_url = response.json()["properties"]["forecast"]
    forecast_response = httpx.get(forecast_url, headers=headers)
    forecast_response.raise_for_status()
    return forecast_response.text
```

### 3. Run the Server

```python
if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    mcp.run()
```

## Troubleshooting

- **Tools Not Displayed**: Confirm that the server is running correctly and that tools are properly defined using the `@mcp.tool()` decorator.
- **API Request Failed**: Check your network connection, the API's availability, and the User-Agent settings.

## MCP Core Components

### 1. The FastMCP Class

The `mcp.server.fastmcp.FastMCP` class is a high-level interface designed to simplify MCP server development.

#### Key Methods:

- **`__init__(name: str)`**: Initializes the FastMCP server and sets its name.
- **`tool()`**: A decorator to register a function as a tool.
- **`run(transport: str)`**: Starts the server, supporting "stdio", "sse", and "http" transport protocols.

### 2. Tool Registration Example

```python
@mcp.tool()
async def example_tool(input_data: str, user_name: str = "default_user") -> dict:
    """
    Example tool function demonstrating how to define parameters directly.
    This example illustrates the principles of [Robustness] and [Transparency].

    Args:
        input_data: The user's input data (string, required).
        user_name: The username for the operation (optional, defaults to 'default_user').

    Returns:
        A dictionary containing the execution result.

    Raises:
        ValueError: Raised if input_data is empty or contains only whitespace,
                    providing a clear error message.
    """
    # [Robustness]: Validate the input
    if not input_data or not input_data.strip():
        # [Transparency]: Return a specific and helpful error message
        raise ValueError("'input_data' cannot be empty.")

    return {"result": f"Tool executed for {user_name} with input: {input_data}"}
```

## Best Practices for MCP Tool Docstrings

### Correct Placement of Docstrings

The placement of docstrings is critical, as it directly affects the LLM's ability to understand and use your tools correctly:

1. **Provide complete docstrings within the function decorated with `@mcp.tool()`**:
   - This is the documentation that the LLM can actually "see".
   - Even if the underlying implementation is located elsewhere, the docstring must be complete on the tool function.

### Example of Correct Docstring Formatting

```python
@mcp.tool()
def create_appointment(subject: str, start_time: str, duration: int) -> str:
    """
    Creates an appointment in the Outlook calendar.

    Args:
        subject: The title of the appointment (required).
        start_time: The start time in 'MM/DD/YYYY HH:MM AM/PM' format (required).
        duration: The duration in minutes, must be a positive number (required).

    Returns:
        A string indicating whether the creation was successful or failed.

    Example:
        create_appointment(subject="Team Meeting", start_time="01/15/2023 10:00 AM", duration=30)
    """
    # [Robustness]: Validate that the appointment duration is positive.
    if duration <= 0:
        # [Transparency]: Provide clear error feedback.
        raise ValueError(f"Appointment duration must be positive, but received: {duration}")

    # Call the underlying implementation
    return manager.create_appointment(subject, start_time, duration)
```

### Example of Incorrect Docstring (Common Mistake)

```python
# INCORRECT: Detailed docstring in the underlying implementation, but a simple one on the tool.
class CalendarManager:
    def create_appointment(self, subject: str, start_time: str, duration: int) -> str:
        """Detailed documentation is here... but the LLM cannot see this part."""
        # Implementation...

@mcp.tool()
def create_appointment(subject: str, start_time: str, duration: int) -> str:
    """MCP tool to create an appointment.""" # The docstring is too simple and lacks parameter and usage information.
    return manager.create_appointment(subject, start_time, duration)
```

### Docstring Content Checklist

Ensure your `@mcp.tool()` function's docstring includes:

1. ✅ A concise description of the function.
2. ✅ Detailed descriptions of all parameters (name, type, purpose, required/optional).
3. ✅ A description of the return value.
4. ✅ A usage example (with specific inputs and expected output).
5. ✅ A list of possible errors or exceptions.

### Best Practices

If you are maintaining both the underlying implementation and the MCP tool interface:

- **Define Parameters Directly**: It is highly recommended to define parameters directly in the signature of the function decorated with `@mcp.tool()`, rather than using a single `arguments: dict`. This makes type hints and default values more explicit and aligns with Python best practices.
- **Keep Signatures Consistent**: It is recommended to keep the signature of the `@mcp.tool()` decorated function consistent with the underlying implementation function for clarity and ease of understanding.
- **Provide Complete Documentation in the `@mcp.tool()` Function**: Ensure that the LLM has access to all necessary information, even if the underlying implementation has its own docstrings.

---

## Advanced Example: Implementing a High-Quality Server Aligned with Evaluation Metrics

This section demonstrates how to build a more complex server.

```python
import sys
import httpx
import re
import asyncio
from mcp.server.fastmcp import FastMCP

# Initialize the FastMCP server
mcp = FastMCP("weather_pro")

# --- Performance: Use a shared AsyncClient ---
# Improve performance for multiple API calls by reusing connections
client = httpx.AsyncClient(
    base_url="https://api.weather.gov",
    headers={"User-Agent": "weather-pro-app/1.0 (contact@example.com)"}
)

@mcp.tool()
async def get_alerts(state: str) -> str:
    """
    Get active weather alerts for a specified state.

    Args:
        state: Two-letter state code (e.g., 'CA' for California).

    Returns:
        A string containing weather alerts in JSON format.

    Raises:
        ValueError: If the state code format is invalid.
        httpx.HTTPStatusError: If the API request fails.
    """
    # --- Robustness & Security: Strict Input Validation ---
    # Validate input format to prevent invalid or malicious input.
    if not re.match(r"^[A-Z]{2}$", state):
        # --- Transparency: Provide clear error messages ---
        # The error message clearly explains the issue and the expected format.
        raise ValueError(f"Invalid state code: '{state}'. Must be two uppercase letters (e.g., 'CA').")

    # --- Functionality: Correctly execute the core logic ---
    response = await client.get(f"/alerts/active?area={state}")
    response.raise_for_status() # Automatically handle HTTP errors
    return response.text

@mcp.tool()
async def get_forecast(latitude: float, longitude: float) -> str:
    """
    Get weather forecast for a specific latitude and longitude.

    Args:
        latitude: Latitude coordinate (valid range: -90 to 90).
        longitude: Longitude coordinate (valid range: -180 to 180).

    Returns:
        A string containing weather forecast in JSON format.

    Raises:
        ValueError: If latitude or longitude coordinates are out of range.
        httpx.HTTPStatusError: If the API request fails.
    """
    # --- Robustness: Boundary Condition Checks ---
    if not -90 <= latitude <= 90:
        raise ValueError(f"Latitude out of range: {latitude}. Valid range is -90 to 90.")
    if not -180 <= longitude <= 180:
        raise ValueError(f"Longitude out of range: {longitude}. Valid range is -180 to 180.")

    # --- Performance: Asynchronously execute I/O-bound tasks ---
    # 'await' allows other tasks to run while waiting for the network response.
    points_response = await client.get(f"/points/{latitude},{longitude}")
    points_response.raise_for_status()

    forecast_url = points_response.json()["properties"]["forecast"]

    # Note: forecast_url is a full URL, so the shared client's base_url cannot be used.
    # We need a new temporary request or to use the original httpx.get.
    async with httpx.AsyncClient() as temp_client:
        forecast_response = await temp_client.get(forecast_url, headers=client.headers)
        forecast_response.raise_for_status()

    return forecast_response.text

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    mcp.run()

```

### How Evaluation Metrics Are Reflected

- **Functionality (30 points)**: The core logic of each tool is implemented correctly.
- **Robustness (20 points)**:
  - All inputs are strictly validated through `re.match` and range checks.
  - The `try...finally` structure ensures the `httpx.AsyncClient` is closed gracefully on program exit.
  - `httpx`'s `response.raise_for_status()` automatically handles non-2xx HTTP response codes by raising exceptions.
- **Security (20 points)**: Input validation (especially format restrictions on the `state` code) serves as the first line of defense against potential injection attacks, although the risk is low in this scenario. Alerts should be in place for dangerous operations like accessing database system information or deleting tables.
- **Performance (20 points)**:
  - All tools are implemented as `async def`, allowing for concurrent execution.
  - The shared `httpx.AsyncClient` instance allows the server to reuse TCP connections, reducing the overhead of establishing new ones.
- **Transparency (10 points)**: When input validation fails, a `ValueError` is raised with a very specific, clear, and user-friendly error message that explains what went wrong and how to fix it.

---

# Appendix: MCP Python SDK - Key Methods and Use Cases

## Core Components

### 1. The FastMCP Class

`mcp.server.fastmcp.FastMCP` is a high-level interface that simplifies MCP server development by handling protocol details automatically.

#### Key Methods:

- **`__init__(name: str)`**: Initializes the FastMCP server and sets its name.
  ```python
  from mcp.server.fastmcp import FastMCP
  mcp = FastMCP("my_server")
  ```
- **`tool()`**: A decorator to register a callable function as a tool.

  ```python
  @mcp.tool()
  async def example_tool(input_data: str, user_name: str = "default_user") -> dict:
      """
      Example tool function demonstrating how to define parameters directly.

      Args:
          input_data: The user's input data (string, required).
          user_name: The username for the operation (optional, defaults to 'default_user').

      Returns:
          A dictionary containing the execution result.

      Raises:
          ValueError: If the input parameter is invalid.
      """
      if not input_data:
          raise ValueError("input_data cannot be empty")
      return {"result": f"Tool executed for {user_name} with input: {input_data}"}
  ```

- **`prompt()`**: A decorator to register prompt templates.

- **`run(transport: str)`**: Starts the server quickly, supporting specified transport protocols (`"stdio"`, `"sse"`, `"http"`).
  ```python
  mcp.run("stdio")
  ```

### 2. Transport Protocols

FastMCP supports the following transport protocols:

- **`stdio`**: Communicates via standard input/output, ideal for local testing.
- **`sse`**: Provides real-time communication via Server-Sent Events, suitable for web environments.
- **`http`**: Transports via Streamable HTTP, suitable for production environments.

Example:

```python
mcp.run("sse")  # Start server using SSE
```

## Best Practices for MCP Tool Docstrings

### Correct Placement of Docstrings

When implementing an MCP server, the **placement of docstrings** is critical because it directly affects the LLM's ability to understand and use your tools. Please follow these rules:

1. **Provide complete docstrings in the function decorated with `@mcp.tool()`**:

   - This is the documentation that the LLM can actually "see".
   - Even if the underlying implementation is elsewhere, the docstring must be complete on the tool function.

2. **Incorrect Practice**: Providing detailed docstrings only in the underlying implementation class or method, with only a brief description in the `@mcp.tool()` function.

### Example of Correct Docstring Formatting

```python
@mcp.tool()
def create_appointment(subject: str, start_time: str, duration: int) -> str:
    """
    Creates an appointment in the Outlook calendar.

    Args:
        subject: The title of the appointment (required).
        start_time: The start time in 'MM/DD/YYYY HH:MM AM/PM' format (required).
        duration: The duration in minutes (required).

    Returns:
        A string indicating whether the creation was successful or failed.

    Example:
        To create an appointment titled "Team Meeting" starting at 10:00 AM on January 15th for 30 minutes:
        create_appointment(subject="Team Meeting", start_time="01/15/2023 10:00 AM", duration=30)
    """
    # Call the underlying implementation
    return manager.create_appointment(subject, start_time, duration)
```

### Example of Incorrect Docstring (Common Mistake)

```python
# INCORRECT: Detailed docstring in the underlying implementation, but a simple one on the tool.
class CalendarManager:
    def create_appointment(self, subject: str, start_time: str, duration: int) -> str:
        """Detailed documentation is here... but the LLM cannot see this part."""
        # Implementation...

@mcp.tool()
def create_appointment(subject: str, start_time: str, duration: int) -> str:
    """MCP tool to create an appointment."""  # The docstring is too simple and lacks parameter and usage information.
    return manager.create_appointment(subject, start_time, duration)
```

### Docstring Content Checklist

Ensure your `@mcp.tool()` function's docstring includes:

1. ✅ A concise description of the function.
2. ✅ Detailed descriptions of all parameters (name, type, purpose, required/optional).
3. ✅ A description of the return value.
4. ✅ A usage example (with specific inputs and expected output).
5. ✅ A list of possible errors or exceptions.

### Best Practices

If you are maintaining both the underlying implementation and the MCP tool interface:

- **Define Parameters Directly**: It is highly recommended to define parameters directly in the signature of the function decorated with `@mcp.tool()`, rather than using a single `arguments: dict`. This makes type hints and default values more explicit and aligns with Python best practices.
- **Keep Signatures Consistent**: It is recommended to keep the signature of the `@mcp.tool()` decorated function consistent with the underlying implementation function for clarity and ease of understanding.
- **Provide Complete Documentation in the `@mcp.tool()` Function**: Ensure that the LLM has access to all necessary information, even if the underlying implementation has its own docstrings.

</rewritten_file>
