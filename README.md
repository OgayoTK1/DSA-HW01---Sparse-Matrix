**Sparse Matrix Operations Project:**
Welcome to the Sparse Matrix Operations Project! After cloning the repository, you will find the main project files in the root directory, and example data files within the examples subdirectory.

**📌 Project Overview:**
This project implements an efficient sparse matrix data structure in Python. It prioritizes memory efficiency by only storing non-zero elements, making it ideal for large matrices where most elements are zero.

**Features**
Memory-efficient sparse matrix representation
Multiple indexing strategies for optimized access
Support for addition, subtraction, and multiplication
Interactive and command-line interfaces
Performance benchmarking for operations
Automatic generation of example matrix files
File Structure
DSA-HW01---Sparse-Matrix/
├── sparse_matrix.py      # Main implementation of the SparseMatrix class and core logic
├── README.md             # This documentation file
└── examples/             # Directory for example input/output files
    ├── matrix1.txt       # Example input matrix 1 (generated)
    ├── matrix2.txt       # Example input matrix 2 (generated)
    ├── matrix3.txt       # Example input matrix 3 (generated)
    ├── matrix4.txt       # Example input matrix 4 (generated)
    └── output_addition.txt # Example output file (generated, or can be specified)
 **Implementation Details**
🔑 **Key Data Structures**
elements: A dictionary mapping (row, column) tuples to non-zero values
row_map: Nested dictionary for efficient row-wise access
col_map: Nested dictionary for efficient column-wise access
This multi-index approach enables fast operations across various access patterns.

⏱️ Time & Space Complexity
Operation	Time Complexity	Space Complexity
Storage	O(N)	O(N)
Element Access	O(1)	-
Addition/Subtraction	O(n₁ + n₂)	O(n₁ + n₂)
Multiplication	O(n₁ × n₂ × dim)	O(result)

**Export to Sheets**
N: Number of non-zero elements
n₁ / n₂: Non-zero elements in each matrix
dim: Inner dimension in multiplication
SparseMatrix Class
The core functionality is encapsulated within the SparseMatrix class, providing methods for matrix creation, manipulation, and operations.

__init__(num_rows, num_cols): Initializes an empty sparse matrix with the specified number of rows and columns.
from_file(file_path): A static method to construct a SparseMatrix object by parsing data from a given file.
get_element(r, c): Retrieves the value at a specific row r and column c. Returns 0 if the element is not explicitly stored (i.e., it's a zero value).
set_element(r, c, value): Sets the value at position (r, c). If value is 0, the element is removed from storage for efficiency.
add(other): Returns a new SparseMatrix representing the sum of the current matrix and other.
sub(other): Returns a new SparseMatrix representing the difference between the current matrix and other.
matmul(other): Returns a new SparseMatrix representing the product of the current matrix and other.
to_file(output_path): Writes the sparse matrix content to a specified file in the defined output format.
transpose(): Returns a new SparseMatrix that is the transpose of the matrix.
get_row(row): Returns a dictionary of non-zero values for a specified row, where keys are column indices and values are the elements.
get_col(col): Returns a dictionary of non-zero values for a specified column, where keys are row indices and values are the elements.
density(): Calculates the density of the matrix (percentage of non-zero elements).
🛠️ Getting Started
*** Prerequisites**
Python 3.6 or higher
No external libraries required
📥 Installation
Clone the repository and set up the example directory:

Bash

git clone https://github.com/OgayoTK1/DSA-HW01---Sparse-Matrix.git
cd DSA-HW01---Sparse-Matrix
mkdir examples
💻 Usage
🧾 Command-Line Interface
Bash

python sparse_matrix.py [operation][--matrix1 <file_path>][--matrix2 <file_path>][--output <file_path>][--verbose][--benchmark]
Arguments:

operation: The type of matrix operation to perform. Choose from: add, subtract, multiply, or create-examples.
--matrix1 <file_path>: Path to the first input matrix file (required for add, subtract, multiply).
--matrix2 <file_path>: Path to the second input matrix file (required for add, subtract, multiply).
--output <file_path>, -o <file_path>: (Optional) Specifies the path for the output file. If not provided, the result will be saved to output_{operation}.txt.
--verbose, -v: (Optional) Enables detailed output, including timing information for performance analysis (for add, subtract, multiply).
--benchmark: (Optional) Runs performance benchmarking for the operation (for multiply).
Examples:

**Addition**:
Bash

python sparse_matrix.py add --matrix1 examples/matrix1.txt --matrix2 examples/matrix2.txt --output result.txt --verbose
Subtraction:
Bash

python sparse_matrix.py subtract --matrix1 examples/matrix1.txt --matrix2 examples/matrix2.txt
Multiplication:
Bash

python sparse_matrix.py multiply --matrix1 examples/matrix3.txt --matrix2 examples/matrix4.txt --benchmark
Generate example files:
Bash

python sparse_matrix.py create-examples
🤖 Interactive Mode
Simply run the script with no arguments:

Bash

python sparse_matrix.py
Follow the on-screen prompts to select an operation and specify your input files.

📂 Example Files
The create-examples command-line operation will generate the following sample matrix files in the examples/ directory:

matrix1.txt and matrix2.txt: Designed for addition and subtraction operations.
matrix3.txt and matrix4.txt: Designed for multiplication operations.
📄 File Format
Input Format
Matrix files must adhere to the following structure:

rows=<number_of_rows>
cols=<number_of_columns>
(<row_index>, <column_index>, <value>)
(<row_index>, <column_index>, <value>)
...
Example:

rows=4
cols=5
(0, 0, 2)
(1, 2, 5)
...
Output Format
The output matrix will be saved in the same sparse coordinate format as the input files.

🧪 Testing Strategy
The project's testing strategy focuses on comprehensive validation of matrix operations and error handling:

Addition/Subtraction: Tested with matrices containing both overlapping and non-overlapping non-zero elements to ensure correctness in various scenarios.
Multiplication: Matrices are specifically designed with strategic sparse patterns to thoroughly test the optimized multiplication algorithm.
Edge Cases: Robustly handles and tests for:
Empty matrices
Single-element matrices
Large sparse matrices to verify performance and memory efficiency.
⚙️ Implementation Notes
⚡ Optimization Techniques
Multiple indexing strategies for efficient row/column access
Adaptive algorithms based on matrix density
Zero elimination when values become zero after operations
Benchmarking support for tracking performance
🧯 **Error Handling**
The implementation includes thorough error handling for:

Incorrect file formats
Index out of bounds
Dimension mismatch during operations
🤝 Contributing
This project is part of a Data Structures and Algorithms course assignment. After the deadline, feel free to fork, experiment, and enhance it!

📜**License**
This project is available for academic and educational use.
