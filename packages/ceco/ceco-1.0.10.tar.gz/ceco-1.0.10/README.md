  # CECO

  ## Overview
  The CECO is a benchmarking framework designed to evaluate and compare optimization algorithms. It includes implementations of various optimization algorithms and test functions, as well as tools for analyzing and visualizing results.

  ## Project Structure

  - **ceco/**: Core library for benchmarking.
    - `benchmark.py`: Main script for running benchmarks.
    - `cec/`: Test functions for benchmarking from CEC.
    - `coco/`: Test functions for benchmarking from COCO.

  - **docs/**: Documentation for the project.
    - `Makefile`, `make.bat`: Scripts for building the documentation.

  - **test/**: Unit tests for the project.
    - `run_test.py`: Test scripts for benchmarking functionality.

  ## Getting Started

  ### Prerequisites
  - Python 3.6 or later
  - Required Python packages (install using `pip`):
    - `numpy >= 1.19.0`

  ### Installation
  #### From PyPI
  ```bash
  pip install ceco
  ```
  #### From Github
  ```bash
  pip install git+https://github.com/haniframadhani/cecopy
  ```
  #### From Source Code
  ```bash
  git clone https://github.com/haniframadhani/cecopy

  cd cecopy

  pip install -r requirements.txt
        
  pip setup.py install
  ```

  ### Running Tests
  To run the unit tests, navigate to the `test/` directory and execute:
  ```bash
  python .\test\run_test.py
  ```

  ## Contributing
  Contributions are welcome! Please follow these steps:
  1. Fork the repository.
  2. Create a new branch for your feature or bugfix.
  3. Submit a pull request with a clear description of your changes.

  ## License
  This project is licensed under the terms of the MIT License. See the `LICENSE` file for details.