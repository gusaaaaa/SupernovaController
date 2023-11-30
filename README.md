# SupernovaController
Manages communications with the Supernova host-adapter USB HID device.

## Introduction
SupernovaController is a Python-based tool designed to interface with the Supernova host-adapter USB HID device. Offering a blocking API, it simplifies command sequences and interactions in the context of asynchronous operation environments like the one offered by the Supernova host-adapter. This approach enhances usability and efficiency, providing a streamlined experience for developers working with the Supernova device.

## Features
- **Blocking API:** A streamlined approach to interact with the Supernova device, minimizing the complexity of handling asynchronous callbacks.
- **Communication** Seamlessly manages command responses and notifications, facilitating easier and more intuitive command sequencing.
- **Examples:** Comprehensive examples demonstrating the practical application of the blocking API.

## Installation

---
### For Binho Developers (REMOVE WHEN PACKAGE IS READY)

To install the SupernovaController package, follow these steps:

1. Clone the repository to your local machine:
    ```sh
    git clone https://github.com/yourusername/SupernovaController.git
    ```

2. Navigate to the project root directory:
    ```sh
    cd SupernovaController
    ```

3. Create and activate a virtual environment (optional but recommended):

- On Unix-like systems:
  ```sh
  python3 -m venv .venv
  source .venv/bin/activate
  ```
- On Windows:
  ```sh
  python -m venv .venv
  .venv\Scripts\activate
  ```

4. Before installation, you need to set the `GH_TOKEN` environment variable, which is used for authentication with GitHub to pull a dependency. Generate a personal access token on GitHub with the necessary permissions and set the `GH_TOKEN`:

   - On Unix-like systems:
     ```bash
     export GH_TOKEN=your_github_personal_access_token
     ```
   - On Windows (Command Prompt):
     ```bash
     set GH_TOKEN=your_github_personal_access_token
     ```
   - On Windows (PowerShell):
     ```bash
     $env:GH_TOKEN="your_github_personal_access_token"
     ```

   Replace `your_github_personal_access_token` with your actual GitHub token.

   **Note:** This step is temporary and will not be necessary after `transfer_controller` version 0.3.0 is approved. Once the new version is available, you can install it directly from the package index without needing to use a GitHub token.

5. Install the package:
    ```sh
    pip install -e .
    ```

    The -e flag will install the package in editable mode, which is helpful during development as it allows you to make changes to your code and have those changes immediately reflected without reinstalling the package.

---

## Usage
After installation, you can run the example scripts to see how the SupernovaController works with the Supernova host-adapter. To run an example, use the following command from the project root directory:

```sh
python -m examples.<example_script_name>
```

Replace `<example_script_name>` with the name of the example you wish to run. For instance, to run the `basic_i2c_example.py` script, you would use:

```sh
python -m examples.basic_i2c_example
```

This ensures that the example runs with the correct package context, resolving the import of the `supernovacontroller` package correctly.

## License
[TO DO]

## Contact
[TO DO]
