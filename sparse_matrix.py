import os
import argparse
from collections import defaultdict
import time

class SparseMatrix:
    """
    An efficient implementation of a sparse matrix using dictionary-based storage.
    Only non-zero elements are stored to minimize memory usage.
    """
    def __init__(self, num_rows, num_cols):
        """
        Initialize a sparse matrix with the given dimensions.
        
        Args:
            num_rows (int): Number of rows in the matrix
            num_cols (int): Number of columns in the matrix
        """
        self.num_rows = num_rows
        self.num_cols = num_cols
        self.data = {}  # {(row, col): value}
        # Add row-wise and column-wise indices for faster access patterns
        self.row_indices = defaultdict(list)  # {row: [(col, value), ...]}
        self.col_indices = defaultdict(list)  # {col: [(row, value), ...]}
    
    def __str__(self):
        """Return a string representation of the matrix."""
        if not self.data:
            return f"Empty sparse matrix ({self.num_rows}x{self.num_cols})"
        
        result = []
        result.append(f"Sparse matrix ({self.num_rows}x{self.num_cols}) with {len(self.data)} non-zero elements:")
        for (r, c), v in sorted(self.data.items()):
            result.append(f"  ({r}, {c}) -> {v}")
        return "\n".join(result)
    
    def density(self):
        """Calculate and return the density of the matrix (proportion of non-zero elements)."""
        total_elements = self.num_rows * self.num_cols
        if total_elements == 0:
            return 0
        return len(self.data) / total_elements

    @staticmethod
    def from_file(file_path):
        """
        Create a sparse matrix from a file.
        
        Args:
            file_path (str): Path to the input file
            
        Returns:
            SparseMatrix: A new sparse matrix created from the file
            
        Raises:
            ValueError: If the file format is invalid
            FileNotFoundError: If the file doesn't exist
        """
        matrix = None
        
        try:
            with open(file_path, 'r') as f:
                lines = [line.strip() for line in f if line.strip()]
                
                # Validate header format
                if len(lines) < 2:
                    raise ValueError("File must contain at least rows and columns specifications")
                
                rows_line = lines[0]
                cols_line = lines[1]
                
                if not rows_line.startswith('rows=') or not cols_line.startswith('cols='):
                    raise ValueError("File must start with 'rows=' and 'cols=' lines")
                
                try:
                    rows = int(rows_line.split('=')[1])
                    cols = int(cols_line.split('=')[1])
                    
                    if rows <= 0 or cols <= 0:
                        raise ValueError("Rows and columns must be positive integers")
                        
                    matrix = SparseMatrix(rows, cols)
                    
                    # Parse matrix elements
                    for i, entry in enumerate(lines[2:], start=3):
                        if not (entry.startswith('(') and entry.endswith(')')):
                            raise ValueError(f"Invalid format at line {i}: {entry}")
                        
                        parts = entry[1:-1].split(',')
                        if len(parts) != 3:
                            raise ValueError(f"Entry at line {i} must have exactly 3 components: {entry}")
                        
                        try:
                            r, c, v = [int(p.strip()) for p in parts]
                            
                            if not (0 <= r < rows and 0 <= c < cols):
                                raise ValueError(f"Indices out of bounds at line {i}: {entry}")
                                
                            if v != 0:  # Only store non-zero values
                                matrix.set_element(r, c, v)
                        except ValueError as e:
                            if "invalid literal for int()" in str(e):
                                raise ValueError(f"All values must be integers at line {i}: {entry}")
                            raise
                except ValueError as e:
                    raise ValueError(f"Invalid file format: {e}")
        except Exception as e:
            if isinstance(e, FileNotFoundError):
                raise
            raise ValueError(f"Error processing file: {e}")
            
        return matrix

    def get_element(self, r, c):
        """
        Get the value at the specified position.
        
        Args:
            r (int): Row index
            c (int): Column index
            
        Returns:
            int: The value at position (r, c), or 0 if not set
        """
        return self.data.get((r, c), 0)

    def set_element(self, r, c, value):
        """
        Set the value at the specified position.
        
        Args:
            r (int): Row index
            c (int): Column index
            value (int): Value to set
            
        Raises:
            IndexError: If indices are out of bounds
        """
        if not (0 <= r < self.num_rows and 0 <= c < self.num_cols):
            raise IndexError(f"Index ({r}, {c}) out of bounds for matrix of size {self.num_rows}x{self.num_cols}")
            
        if value != 0:
            self.data[(r, c)] = value
            
            # Update row and column indices
            # Remove old value from indices if it exists
            if (r, c) in self.data:
                self.row_indices[r] = [(col, val) for col, val in self.row_indices[r] if col != c]
                self.col_indices[c] = [(row, val) for row, val in self.col_indices[c] if row != r]
            
            # Add new value to indices
            self.row_indices[r].append((c, value))
            self.col_indices[c].append((r, value))
        elif (r, c) in self.data:
            # Remove element if setting to zero
            del self.data[(r, c)]
            
            # Update indices
            self.row_indices[r] = [(col, val) for col, val in self.row_indices[r] if col != c]
            self.col_indices[c] = [(row, val) for row, val in self.col_indices[c] if row != r]
            
            # Clean up empty lists
            if not self.row_indices[r]:
                del self.row_indices[r]
            if not self.col_indices[c]:
                del self.col_indices[c]

    def __add__(self, other):
        """
        Add two sparse matrices.
        
        Args:
            other (SparseMatrix): Matrix to add
            
        Returns:
            SparseMatrix: Result of addition
            
        Raises:
            ValueError: If matrix dimensions don't match
        """
        self._validate_shape(other)
        result = SparseMatrix(self.num_rows, self.num_cols)
        
        # Use set union to process all non-zero positions
        keys = set(self.data) | set(other.data)
        for r, c in keys:
            val = self.get_element(r, c) + other.get_element(r, c)
            if val != 0:
                result.set_element(r, c, val)
                
        return result

    def __sub__(self, other):
        """
        Subtract two sparse matrices.
        
        Args:
            other (SparseMatrix): Matrix to subtract
            
        Returns:
            SparseMatrix: Result of subtraction
            
        Raises:
            ValueError: If matrix dimensions don't match
        """
        self._validate_shape(other)
        result = SparseMatrix(self.num_rows, self.num_cols)
        
        # Use set union to process all non-zero positions
        keys = set(self.data) | set(other.data)
        for r, c in keys:
            val = self.get_element(r, c) - other.get_element(r, c)
            if val != 0:
                result.set_element(r, c, val)
                
        return result

    def __matmul__(self, other):
        """
        Multiply two sparse matrices.
        
        Args:
            other (SparseMatrix): Matrix to multiply with
            
        Returns:
            SparseMatrix: Result of multiplication
            
        Raises:
            ValueError: If matrix dimensions don't match for multiplication
        """
        if self.num_cols != other.num_rows:
            raise ValueError(f"Matrix dimensions do not match for multiplication: "
                            f"{self.num_rows}x{self.num_cols} @ {other.num_rows}x{other.num_cols}")
                            
        result = SparseMatrix(self.num_rows, other.num_cols)
        
        # Optimized multiplication using row and column indices
        for i in self.row_indices:
            for j in other.col_indices:
                # Calculate dot product for this cell
                dot_product = 0
                
                # Get non-zero elements for row i and column j
                row_elements = {col: val for col, val in self.row_indices[i]}
                col_elements = {row: val for row, val in other.col_indices[j]}
                
                # Find common indices (where both have non-zero values)
                common_indices = set(row_elements.keys()) & set(col_elements.keys())
                
                # Calculate dot product
                for k in common_indices:
                    dot_product += row_elements[k] * col_elements[k]
                
                if dot_product != 0:
                    result.set_element(i, j, dot_product)
        
        return result

    def _validate_shape(self, other):
        """
        Validate that two matrices have the same shape.
        
        Args:
            other (SparseMatrix): Matrix to compare with
            
        Raises:
            ValueError: If matrix dimensions don't match
        """
        if not isinstance(other, SparseMatrix):
            raise TypeError(f"Unsupported operand type: {type(other)}")
            
        if self.num_rows != other.num_rows or self.num_cols != other.num_cols:
            raise ValueError(f"Matrix dimensions must match: "
                           f"{self.num_rows}x{self.num_cols} vs {other.num_rows}x{other.num_cols}")

    def to_file(self, output_path):
        """
        Write the matrix to a file.
        
        Args:
            output_path (str): Path to write the output file
        """
        with open(output_path, 'w') as f:
            f.write(f"rows={self.num_rows}\n")
            f.write(f"cols={self.num_cols}\n")
            
            # Write non-zero elements sorted by row then column
            for (r, c), v in sorted(self.data.items()):
                f.write(f"({r}, {c}, {v})\n")

    def transpose(self):
        """
        Return the transpose of this matrix.
        
        Returns:
            SparseMatrix: Transposed matrix
        """
        result = SparseMatrix(self.num_cols, self.num_rows)
        
        for (r, c), v in self.data.items():
            result.set_element(c, r, v)
            
        return result

    def get_row(self, row):
        """
        Get a dictionary representation of a row.
        
        Args:
            row (int): Row index
            
        Returns:
            dict: Dictionary mapping column indices to values
            
        Raises:
            IndexError: If row index is out of bounds
        """
        if not (0 <= row < self.num_rows):
            raise IndexError(f"Row index {row} out of bounds for matrix with {self.num_rows} rows")
            
        return {c: self.data[(row, c)] for r, c in self.data if r == row}

    def get_col(self, col):
        """
        Get a dictionary representation of a column.
        
        Args:
            col (int): Column index
            
        Returns:
            dict: Dictionary mapping row indices to values
            
        Raises:
            IndexError: If column index is out of bounds
        """
        if not (0 <= col < self.num_cols):
            raise IndexError(f"Column index {col} out of bounds for matrix with {self.num_cols} columns")
            
        return {r: self.data[(r, col)] for r, c in self.data if c == col}


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Sparse Matrix Operations')
    parser.add_argument('operation', choices=['add', 'subtract', 'multiply'],
                        help='Operation to perform: add, subtract, or multiply')
    parser.add_argument('matrix1', help='Path to first matrix file')
    parser.add_argument('matrix2', help='Path to second matrix file')
    parser.add_argument('--output', '-o', default=None, 
                        help='Output file path (default: generated based on operation)')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Show verbose output including timing information')
    
    return parser.parse_args()


def main():
    """Main function to run the program."""
    # Command-line version
    try:
        args = parse_arguments()
        start_time = time.time()
        
        if args.verbose:
            print(f"Loading matrix 1 from {args.matrix1}...")
        matrix1 = SparseMatrix.from_file(args.matrix1)
        
        if args.verbose:
            print(f"Loading matrix 2 from {args.matrix2}...")
        matrix2 = SparseMatrix.from_file(args.matrix2)
        
        if args.verbose:
            print(f"Matrix 1: {matrix1.num_rows}x{matrix1.num_cols} with {len(matrix1.data)} non-zero elements")
            print(f"Matrix 2: {matrix2.num_rows}x{matrix2.num_cols} with {len(matrix2.data)} non-zero elements")
        
        # Perform operation
        if args.operation == 'add':
            if args.verbose:
                print("Performing addition...")
            result = matrix1 + matrix2
            operation_name = "addition"
        elif args.operation == 'subtract':
            if args.verbose:
                print("Performing subtraction...")
            result = matrix1 - matrix2
            operation_name = "subtraction"
        elif args.operation == 'multiply':
            if args.verbose:
                print("Performing multiplication...")
            result = matrix1 @ matrix2
            operation_name = "multiplication"
            
        # Output file
        output_file = args.output if args.output else f"output_{operation_name}.txt"
        
        if args.verbose:
            print(f"Writing result to {output_file}...")
        result.to_file(output_file)
        
        if args.verbose:
            end_time = time.time()
            print(f"Operation completed in {end_time - start_time:.4f} seconds")
            print(f"Result: {result.num_rows}x{result.num_cols} with {len(result.data)} non-zero elements")
        
        print(f"Operation successful. Result saved to {output_file}")
        
    except ValueError as e:
        print(f"Error: {e}")
    except FileNotFoundError as e:
        print(f"Error: File not found - {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
        
    # Interactive version
    # This provides an alternative interface for when command line arguments aren't used
    if not hasattr(main, 'ran_from_cmdline') and __name__ == '__main__':
        main.ran_from_cmdline = True
        
        print("\nSparse Matrix Operations")
        print("1. Addition")
        print("2. Subtraction")
        print("3. Multiplication")

        choice = input("Enter your choice (1/2/3): ")
        file1 = input("Enter path to first matrix file: ")
        file2 = input("Enter path to second matrix file: ")

        try:
            matrix1 = SparseMatrix.from_file(file1)
            matrix2 = SparseMatrix.from_file(file2)

            if choice == '1':
                result = matrix1 + matrix2
                output = "output_addition.txt"
            elif choice == '2':
                result = matrix1 - matrix2
                output = "output_subtraction.txt"
            elif choice == '3':
                result = matrix1 @ matrix2
                output = "output_multiplication.txt"
            else:
                print("Invalid choice")
                return

            result.to_file(output)
            print(f"Operation successful. Result saved to {output}")

        except ValueError as e:
            print(f"Error: {e}")
        except FileNotFoundError:
            print("Error: One or both input files not found.")
        except Exception as e:
            print(f"Unexpected error: {e}")


if __name__ == '__main__':
    main()
