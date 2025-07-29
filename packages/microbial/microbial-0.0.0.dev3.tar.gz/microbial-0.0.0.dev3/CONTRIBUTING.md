# CONTRIBUTING.md

**Note**: This document is a work in progress and may not be complete. If you have suggestions for improvements or additional sections, please feel free to submit a pull request or open an issue.

---

Thank you for your interest in contributing to this project! We welcome contributions from the community and invite developers of all skill levels to participate in its development. This document exists to help you get started.


## General Guidelines

### A Note on Pull Requests, Code Reviews, and Quality Assurance

Making a pull request is the first step in contributing to this project; however, we also want to emphasize that submitting a pull request does not guarantee it will be merged. The project maintainers will review your code and may request changes or improvements before merging. This process is essential for maintaining the rigorous quality standards to which the project aspires, so please be prepared for constructive feedback. Thank you for your understanding and cooperation.

Following these guidelines will help ensure that your contributions are consistent with the project's goals and standards, making it easier for maintainers to review and merge your changes in a timely manner. For more information on the code review process, please refer to the [Code Review Guidelines](#code-review-guidelines) section.


### General Guidelines

#### Code Style

This codebase adheres to the [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html), so please ensure that your code follows these conventions. This includes:

- Using four spaces for indentation.

- Using descriptive variable and function names, with variable names that contain three or more words separated by underscores (e.g., `my_variable_name`).

  - For variable names that contain two words, the underscore may be omitted (e.g., `myvar`, instead of `my_var`). Use your best judgment to determine whether a given variable name is sufficiently readable without an underscore. When in doubt, use one.

- Using double quotes for strings (e.g., `"my string"`).

- Using parentheses for line continuations.

- Breaking lines before, rather than after, binary operators.

- Using spaces around operators and after commas.

- Avoiding explicit comparisons to `None` (e.g., use `if my_var:` instead of `if my_var is not None:`).

- Observing the 80-character line length limit, except for docstrings and comments, which may only extend to 72 characters.

  - When a line exceeds 80 characters, break it into multiple lines using Python's implicit line continuation inside parentheses, brackets, or braces. Alternatively, you can use a backslash (`\`) to explicitly break the line, but this is less preferred.

- Placing imports at the top of the file, grouped by standard library imports, third-party imports, and local imports.

- Avoiding the use of `from module import *` to prevent namespace pollution.

- Avoiding the use of `print` statements for debugging; instead, use the `logging` module for logging messages.

  - Note that it is still acceptable to use `print` statements for debugging during development, but they should be removed before submitting a pull request.

  - Additionally, if your code needs to output information to the user, using `print` is an acceptable solution, as long as it is specifically intended for user interaction and not for debugging purposes.

- Avoiding the use of `assert` statements for runtime checks; instead, use exceptions to handle errors.

- Avoiding mutable global variables, as they can lead to unexpected behavior and make the code harder to understand and maintain. As a rule of thumb, prefer using function parameters and return values to pass data between functions. If you need to maintain state, consider using classes or data structures that encapsulate the state and provide methods for accessing and modifying it.

  - At the same time, since "we are all consenting adults here," we do not enforce these rules strictly. (This is also why our public API eschews strict enforcement mechanisms in favor of trusting end users to tread undocumented territory responsibly: we recognize that exceptions to the rules may be necessary in some cases.)
