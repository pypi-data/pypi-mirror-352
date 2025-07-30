# GitHub Analysis Tool

A powerful tool for analyzing Git repositories using LLM-powered insights. This tool provides detailed analysis of repository patterns, milestones, technical challenges, team dynamics, and more.

## Installation

```bash
pip install githubanalysis
```

## Usage

### Basic Analysis

```bash
githubanalysis https://github.com/username/repo.git --format markdown
```

### Analysis with Date Range

```bash
githubanalysis https://github.com/username/repo.git \
    --start-date 2023-01-01 \
    --end-date 2024-03-20 \
    --format markdown
```

### OpenAI API Key Configuration

You can provide your OpenAI API key in three ways:

1. Command line argument:
```bash
githubanalysis https://github.com/username/repo.git --openai-key your-api-key
```

2. Environment variable:
```bash
export OPENAI_API_KEY=your-api-key
githubanalysis https://github.com/username/repo.git
```

3. .env file:
Create a `.env` file in your working directory:
```
OPENAI_API_KEY=your-api-key
```

### Custom Prompts

You can customize the analysis prompts by providing a JSON file:

```bash
githubanalysis https://github.com/username/repo.git \
    --custom-prompts path/to/prompts.json
```

Example prompts.json:
```json
{
    "system_prompt": "Your system prompt that defines the role and task of the AI analyst",
    "analysis_prompts": {
        "technical_challenges": "Your prompt for analyzing technical challenges. Should include structure for:\n- Challenge description\n- Technical difficulties\n- Solution attempts\n- Current status",
        "technical_context": "Your prompt for technical context. Should include sections for:\n- Project Overview\n- Technical Infrastructure\n- Development Approach",
        "implementation_details": "Your prompt for implementation details. Should include sections for:\n- Code architecture\n- Technical implementations\n- Performance and security measures"
    }
}
```

### Advanced Options

```bash
githubanalysis https://github.com/username/repo.git \
    --start-date 2023-01-01 \
    --end-date 2024-03-20 \
    --format markdown \
    --output-dir custom_reports \
    --openai-key your-api-key \
    --model gpt-4 \
    --custom-prompts path/to/prompts.json
```

## Output

The tool generates a comprehensive report in either JSON or Markdown format, including:

- Repository overview
- Development patterns
- Key milestones
- Technical achievements
- Challenges and solutions
- Team dynamics
- Code quality assessment
- Recommendations

Reports are saved in the specified output directory (default: `reports/`).

## Requirements

- Python 3.7+
- Git
- OpenAI API key (for LLM analysis)

## Dependencies

- gitpython
- openai
- python-dotenv
- argparse
- tqdm
- markdown
- pandas
- matplotlib
- seaborn
- scikit-learn
- numpy
- nltk
- requests
- tiktoken