# 🏎️ MCP Server F1Analisys

<img src="./content/example.gif">

A Model Context Protocol (MCP) server for interacting with F1Analisys through LLM interfaces like Claude.

## Getting Started
To use `mcp-f1analisys` server in claude can be configured by adding the following to your configuration file.
- Windows: `%APPDATA%/Claude/claude_desktop_config.json`
- Linux: `~/Library/Application Support/Claude/claude_desktop_config.json`

Add the F1Analisys MCP server configuration:
```json
{
  "mcpServers": {
    "mcp-f1analisys": {
      "command": "python",
      "args": [ "-m", "mcp-f1analisys" ]
    }
  }
}
```

## Tools 
- Track dominance ![Sesión Oficial](https://img.shields.io/badge/-Official-blue) ![Sesión Oficial](https://img.shields.io/badge/-Pretesting-red)
- Top speed ![Sesión Oficial](https://img.shields.io/badge/-Official-blue) ![Sesión Oficial](https://img.shields.io/badge/-Pretesting-red)
- Lap time average ![Sesión Oficial](https://img.shields.io/badge/-Official-blue) ![Sesión Oficial](https://img.shields.io/badge/-Pretesting-red)
- Lap time distribution ![Sesión Oficial](https://img.shields.io/badge/-Official-blue)
- Team performance ![Sesión Oficial](https://img.shields.io/badge/-Official-blue) ![Sesión Oficial](https://img.shields.io/badge/-Pretesting-red)
- Fastest laps ![Sesión Oficial](https://img.shields.io/badge/-Official-blue) ![Sesión Oficial](https://img.shields.io/badge/-Pretesting-red)
- Race position evolution ![Sesión Oficial](https://img.shields.io/badge/-Races-orange) ![Sesión Oficial](https://img.shields.io/badge/-Sprints-yellow)
- Fatest drivers each compound ![Sesión Oficial](https://img.shields.io/badge/-Official-blue) ![Sesión Oficial](https://img.shields.io/badge/-Pretesting-red)
- Comparative lap time ![Sesión Oficial](https://img.shields.io/badge/-Official-blue) ![Sesión Oficial](https://img.shields.io/badge/-Pretesting-red)
- Throttle usage ![Sesión Oficial](https://img.shields.io/badge/-Official-blue) ![Sesión Oficial](https://img.shields.io/badge/-Pretesting-red)
- Braking usage ![Sesión Oficial](https://img.shields.io/badge/-Official-blue) ![Sesión Oficial](https://img.shields.io/badge/-Pretesting-red)
- Long runs ![Sesión Oficial](https://img.shields.io/badge/-Official-blue) ![Sesión Oficial](https://img.shields.io/badge/-Pretesting-red)

## Instalation
Active the virtual environment and install the requirements using:
```commandline
.\.venv\Scripts\activate
```

Install the mcp server in Claude using the following command:
```commandline
mcp install .\server.py
```

## Requirements
The requirementes used to build this MCP server are:
- `mcp[cli]`
- `httpx`

## Testing 
You can test the server using the MCP Inspector:
```commandline
mcp dev .\server.py
```

## License
This project is licensed under the MIT <a href="https://github.com/Maxbleu/mcp-f1analisys/blob/master/LICENSE">LICENSE</a> - see the details.