# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Common Development Commands

### Setup and Installation
```bash
# Clone and install for development
git clone --depth 1 https://github.com/EleutherAI/lm-evaluation-harness
cd lm-evaluation-harness
pip install -e .

# Install development dependencies
pip install -e ".[dev]"

# Setup pre-commit hooks
pre-commit install
```

### Testing
```bash
# Run unit tests
python -m pytest --showlocals -s -vv -n=auto --ignore=tests/models/test_neuralmagic.py --ignore=tests/models/test_openvino.py

# Run tests with coverage
python -m pytest --cov=lm_eval

# Run a specific test file
python -m pytest tests/test_evaluator.py

# Run tests in parallel (using pytest-xdist)
python -m pytest -n auto
```

### Linting and Code Quality
```bash
# Run all pre-commit hooks
pre-commit run --all-files

# Run ruff linter/formatter only
ruff check .
ruff format .

# Check spelling
codespell

# Type checking (mypy is configured but currently ignores most modules)
mypy lm_eval
```

### Running Evaluations
```bash
# Basic evaluation example
lm_eval --model hf \
    --model_args pretrained=EleutherAI/gpt-j-6B \
    --tasks hellaswag \
    --device cuda:0 \
    --batch_size 8

# List available tasks
lm_eval --tasks list

# Run with automatic batch size detection
lm_eval --model hf \
    --model_args pretrained=EleutherAI/pythia-160m \
    --tasks lambada_openai \
    --device cuda:0 \
    --batch_size auto
```

## High-Level Architecture

### Core Components

1. **Model System** (`lm_eval/models/`)
   - Base class: `lm_eval.api.model.LM` - All models must implement this interface
   - Models register via `@register_model` decorator
   - Key methods: `loglikelihood()`, `generate_until()`, `loglikelihood_rolling()`
   - Supports HuggingFace, OpenAI, Anthropic, VLLM, and many other backends

2. **Task System** (`lm_eval/tasks/`)
   - Tasks defined via YAML configuration files
   - `TaskManager` discovers and indexes all tasks
   - Base class: `lm_eval.api.task.Task` with `ConfigurableTask` for YAML tasks
   - Tasks can be individual benchmarks, groups, or tagged collections
   - Task output types: `loglikelihood`, `multiple_choice`, `generate_until`, `loglikelihood_rolling`

3. **Evaluation Pipeline** (`lm_eval/evaluator.py`)
   - Entry points: `simple_evaluate()` (high-level) and `evaluate()` (low-level)
   - Flow: Initialize → Build Requests → Batch Process → Calculate Metrics → Output Results
   - Supports distributed evaluation across multiple GPUs
   - Built-in caching and result logging

4. **Request Processing**
   - `Instance`: Single evaluation example with request and response
   - Requests grouped by type for efficient batching
   - Handles few-shot examples, chat templates, and system instructions

5. **Metrics and Filters** (`lm_eval/api/metrics.py`, `lm_eval/filters/`)
   - Pluggable metric system with registry
   - Filters transform model outputs before metric calculation
   - Built-in metrics: accuracy, perplexity, BLEU, etc.

### Key Design Patterns

- **Registry Pattern**: Models and tasks self-register for easy extension
- **Configuration as Code**: YAML files define tasks without Python changes
- **Separation of Concerns**: Clear boundaries between models, tasks, and evaluation logic
- **Batching Strategy**: Efficient request batching for optimal GPU utilization

### Adding New Components

**New Model Backend:**
1. Create new file in `lm_eval/models/`
2. Inherit from `lm_eval.api.model.LM`
3. Implement required methods
4. Add `@register_model("your-model-name")` decorator

**New Task:**
1. Create YAML file in `lm_eval/tasks/your_task/`
2. Define task configuration following existing patterns
3. Place dataset loading and processing in YAML config
4. No Python code needed for most tasks

**New Metric:**
1. Add function to `lm_eval/api/metrics.py`
2. Register with `@register_metric` decorator
3. Use in task YAML via `metric_list`

### Important Files and Directories

- `lm_eval/__main__.py` - CLI entry point
- `lm_eval/evaluator.py` - Main evaluation logic
- `lm_eval/api/` - Core interfaces and base classes
- `lm_eval/models/` - Model implementations
- `lm_eval/tasks/` - Task definitions (YAML files)
- `lm_eval/filters/` - Output processing filters
- `tests/` - Unit tests

### Development Tips

1. **Before Running Tests**: The test suite expects certain model files to be present. Some tests may fail if you haven't downloaded the required models.

2. **Task Development**: Start by copying an existing similar task YAML and modifying it. The YAML schema is well-documented in `lm_eval/api/task.py`.

3. **Debugging**: Use `--limit 10` to test on a small subset of examples first.

4. **Performance**: Use `--batch_size auto` for automatic batch size detection, especially with VLLM backend.

5. **Caching**: Use `--use_cache <DIR>` to cache results and speed up repeated evaluations.

## CI/CD

- GitHub Actions runs tests and linting on PRs
- Pre-commit hooks enforce code quality locally
- Tests run with pytest in parallel mode
- Coverage reports generated but not enforced

## External Integrations

The harness integrates with:
- Weights & Biases for experiment tracking (`--wandb_args`)
- HuggingFace Hub for result uploading (`--hf_hub_log_args`)
- Zeno for result visualization
- Various inference servers (OpenAI API compatible)