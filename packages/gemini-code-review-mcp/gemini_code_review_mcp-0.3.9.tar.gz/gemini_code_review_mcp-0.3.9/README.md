# Gemini Code Review MCP

[![PyPI version](https://badge.fury.io/py/gemini-code-review-mcp.svg)](https://badge.fury.io/py/gemini-code-review-mcp)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue)](https://www.python.org)
[![MCP](https://img.shields.io/badge/MCP-Compatible-green)](https://github.com/anthropics/mcp)
[![Gemini](https://img.shields.io/badge/Gemini-API-orange)](https://ai.google.dev)

![Gemini Code Review MCP](gemini-code-review-mcp.jpg)

> 🚀 **AI-powered code reviews that understand your project's context and development progress**

Transform your git diffs into actionable insights with contextual awareness of your project guidelines, task progress, and coding standards.

## 📚 Table of Contents

- [Why Use This?](#why-use-this)
- [Quick Start](#-quick-start)
- [Available MCP Tools](#-available-mcp-tools)
- [Configuration](#️-configuration)
- [Key Features](#-key-features)
- [CLI Usage](#️-cli-usage)
- [Troubleshooting](#-troubleshooting)
- [Development](#-development)

## Why Use This?

- **🎯 Context-Aware Reviews**: Automatically includes your CLAUDE.md guidelines and project standards
- **📊 Progress Tracking**: Understands your task lists and development phases
- **🤖 AI Agent Integration**: Seamless MCP integration with Claude Code and Cursor
- **🔄 Flexible Workflows**: GitHub PR reviews, project analysis, or custom scopes
- **⚡ Smart Defaults**: Auto-detects what to review based on your project state

## 🚀 Quick Start

```bash
# 1. Get your Gemini API key
# Visit: https://ai.google.dev/gemini-api/docs/api-key

# 2. Add to Claude Code
claude mcp add gemini-reviewer \
  -e GEMINI_API_KEY=your_key_here \
  -- uvx gemini-code-review-mcp

# 3. Use in your AI agent
# "Generate a code review for my project"
```

### Optional: GitHub PR Reviews

```bash
# Add GitHub token for PR analysis
claude mcp add gemini-reviewer \
  -e GEMINI_API_KEY=your_key_here \
  -e GITHUB_TOKEN=your_github_token \
  -- uvx gemini-code-review-mcp
```

## 📋 Available MCP Tools

| Tool | Purpose | Key Options |
|------|---------|-------------|
| **`generate_ai_code_review`** | Complete AI code review | `project_path`, `model`, `scope` |
| **`generate_pr_review`** | GitHub PR analysis | `github_pr_url`, `project_path` |
| **`generate_code_review_context`** | Build review context | `project_path`, `scope`, `enable_gemini_review` |
| **`generate_meta_prompt`** | Create contextual prompts | `project_path`, `text_output` |

<details>
<summary>📖 Detailed Tool Examples</summary>

### AI Code Review
```javascript
// Quick project review
{
  tool_name: "generate_ai_code_review",
  arguments: {
    project_path: "/path/to/project",
    model: "gemini-2.5-pro"  // Optional: use advanced model
  }
}
```

### GitHub PR Review
```javascript
// Analyze GitHub pull request
{
  tool_name: "generate_pr_review",
  arguments: {
    github_pr_url: "https://github.com/owner/repo/pull/123"
  }
}
```

</details>

### Common Workflows

#### Quick Project Review
```
Human: Generate a code review for my project

Claude: I'll analyze your project and generate a comprehensive review.

[Uses generate_ai_code_review with project_path]
```

#### GitHub PR Review
```
Human: Review this PR: https://github.com/owner/repo/pull/123

Claude: I'll fetch the PR and analyze the changes.

[Uses generate_pr_review with github_pr_url]
```

#### Custom Model Review
```
Human: Generate a detailed review using Gemini 2.5 Pro

Claude: I'll use Gemini 2.5 Pro for a more detailed analysis.

[Uses generate_ai_code_review with model="gemini-2.5-pro"]
```

## ⚙️ Configuration

### Environment Variables

| Variable | Required | Default | Description |
|:---------|:--------:|:-------:|:------------|
| `GEMINI_API_KEY` | ✅ | - | Your [Gemini API key](https://ai.google.dev/gemini-api/docs/api-key) |
| `GITHUB_TOKEN` | ⬜ | - | GitHub token for PR reviews ([create one](https://github.com/settings/tokens)) |
| `GEMINI_MODEL` | ⬜ | `gemini-2.0-flash` | AI model selection |
| `GEMINI_TEMPERATURE` | ⬜ | `0.5` | Creativity (0.0-2.0) |

### Automatic Configuration Discovery

The tool automatically discovers and includes:
- 📁 **CLAUDE.md** files at project/user/enterprise levels
- 📝 **Cursor rules** (`.cursorrules`, `.cursor/rules/*.mdc`)
- 🔗 **Import syntax** (`@path/to/file.md`) for modular configs

## ✨ Key Features

- 🤖 **Smart Context** - Automatically includes CLAUDE.md, task lists, and project structure
- 🎯 **Flexible Scopes** - Review PRs, recent changes, or entire projects
- ⚡ **Model Selection** - Choose between Gemini 2.0 Flash (speed) or 2.5 Pro (depth)
- 🔄 **GitHub Integration** - Direct PR analysis with full context
- 📊 **Progress Aware** - Understands development phases and task completion

## 🖥️ CLI Usage

Alternative: Command-line interface for development/testing

### Installation

```bash
# Quick start with uvx (no install needed)
uvx gemini-code-review-mcp /path/to/project

# Or install globally
pip install gemini-code-review-mcp
```

### Commands

```bash
# Basic review
generate-code-review /path/to/project

# Advanced options
generate-code-review . \
  --scope full_project \
  --model gemini-2.5-pro

# Meta-prompt only
generate-meta-prompt --project-path . --stream
```

### Supported File Formats

- 📋 **Task Lists**: `/tasks/tasks-*.md` - Track development phases
- 📄 **PRDs**: `/tasks/prd-*.md` - Project requirements
- 📦 **Configs**: `CLAUDE.md`, `.cursorrules` - Coding standards

## 🆘 Troubleshooting

- **Missing API key?** → Get one at [ai.google.dev](https://ai.google.dev/gemini-api/docs/api-key)
- **MCP not working?** → Run `claude mcp list` to verify installation
- **Old version cached?** → Run `uv cache clean`

## 📦 Development

```bash
# Setup
git clone https://github.com/yourusername/gemini-code-review-mcp
cd gemini-code-review-mcp
pip install -e ".[dev]"

# Test
pytest              # Run tests
make lint          # Check code style
make test-cli      # Test CLI commands
```

## 📏 License

MIT License - see [LICENSE](LICENSE) file for details.

## 👥 Credits

Built with ❤️ by [Nico Bailon](https://github.com/nicobailon).