# Template Documentation Tools

This project includes tools for testing and documenting Jinja2 templates used in the FastAPI application. Sort of accidentally created these in the course of another project, because I was frustrated by the lack of tooling to enforce that the context variables expected by Jinja2 templates matched the variables actually being passed in.

## Features

1. **Syntax Validation**: Tests that all templates have valid Jinja2 syntax.
2. **Hardcoded Route Detection**: Ensures that all routes in templates use `url_for()` instead of hardcoded paths.
3. **Variable Extraction**: Identifies all required context variables for each template.
4. **Documentation Generation**: Creates a comprehensive markdown file documenting the required variables for each template.

## Running the Tests

To run the template tests:

```bash
uv run pytest tests/test_templates.py
```

## Generating Documentation

To generate documentation for all templates:

```bash
uv run python scripts/generate_template_docs.py [output_file]
```

By default, this will create a file named `template_variables.md` in the project root.

## Understanding the Documentation

The generated documentation is organized by directory and includes:

- A table of contents for easy navigation
- A section for each template directory
- For each template:
  - The template path
  - A list of required context variables

This documentation is valuable for developers who need to work with the templates, as it clearly shows what variables need to be provided when rendering each template.

## How It Works

The template analysis works by:

1. Using Jinja2's AST parser to extract undeclared variables from each template
2. Checking template syntax by attempting to parse each template
3. Using regular expressions to detect hardcoded routes
4. Organizing the extracted information into a readable markdown format

## Extending the Documentation

To add descriptions for the variables in the documentation:

1. Edit the `generate_template_documentation` function in `tests/test_templates.py`
2. Add a dictionary mapping variable names to descriptions
3. Use these descriptions when generating the markdown table

## Future Improvements

Potential improvements to the template testing and documentation:

1. Add a way to test template rendering with mock data
2. Integrate with FastAPI's route documentation
3. Add type information for each variable
4. Generate HTML documentation with interactive features 