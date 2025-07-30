# Typical Phrase Splitter

A Python package that splits sentences into typical segments using OpenAI API.

## Installation

To install this package, run:

```bash
pip install typical-phrase-splitter

python -m spacy download en_core_web_sm

```

## Command-Line Usage

After installation, you can use the split-phrase command to split sentences into typical segments. The syntax is as follows:

```bash
split-phrase "[sentence]" "[your-openai-api-key]"
```

Optional Flags: 
-n, --num_queries (Number of times to query the API. Default is 1; if greater than 1, majority voting will be used to determine the typical segments.)

-f, --format (Output format, "json" for structured output with last_atypical_phrase, "list" for a plain list assuming no last_atypical_phrase. Default is "json")