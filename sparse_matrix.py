import argparse
import sys
import time
from collections import defaultdict
from typing import Dict, List, Tuple, Set, Optional, Union


class SparseMatrix:
    """
    An efficient implementation of sparse matrices using multiple indexing strategies.
    
    This implementation uses a dictionary-based storage approach where only non-zero
    elements are stored, along with specialized indices to optimize different types
    of operations (row access, column access, etc.).
    """
    
    def __init__(self, rows: int, cols: int):
        """
        Initialize a new sparse matrix with the given dimensions.
        
        Args:
            rows: Number of rows in the matrix
            cols: Number of columns in the matrix
        """
        if rows <= 0 or cols <= 0:
            raise ValueError("Matrix dimensions must be positive integers")
            
        self.rows = rows
        self.cols = cols
        
        # Main storage for non-zero elements
        self.elements: Dict[Tuple[int, int], int] = {}
        
        # Specialized indices for faster operations
        self.row_map: Dict[int, Dict[int, int]] = defaultdict(dict)  # {row: {col: value}}
        self.col_map: Dict[int, Dict[int, int]] = defaultdict(dict)  # {col: {row: value}}
        
        # Track statistics for optimization decisions
        self.num_nonzero = 0
        self._last_operation_time = 0.0
    
    def __str__(self) -> str:
        """Return a readable string representation of the matrix."""
        if not self.elements:
            return f"Empty sparse matrix ({self.rows}×{self.cols})"
            
        elements_list = [f"({r}, {c}, {v})" for (r, c), v in sorted(self.elements.items())]
        elements_str = "\n".join(elements_list)
        return f"Sparse matrix ({self.rows}×{self.cols}) with {self.num_nonzero} non-zero elements:\n{elements_str}"
    
    def __repr__(self) -> str:
        """Return a string representation for debugging."""
        return f"SparseMatrix(rows={self.rows}, cols={self.cols}, nonzero={self.num_nonzero})"
    
    @classmethod
    def from_file(cls, filepath: str) -> 'SparseMatrix':
        """
        Create a sparse matrix by reading from a file.
        
        Args:
            filepath: Path to the input file
            
        Returns:
            A new SparseMatrix instance
            
        Raises:
            ValueError: If the file format is invalid
            FileNotFoundError: If the file cannot be opened
        """
        try:
            with open(filepath, 'r') as file:
                lines = [line.strip() for line in file if line.strip()]
                
                # Need at least rows and columns specifications
                if len(lines) < 2:
                    raise ValueError("File must contain at least rows and columns specifications")
                
                # Parse header
                if not lines[0].startswith('rows='):
                    raise ValueError("First line must specify number of rows (rows=X)")
                    
                if not lines[1].startswith('cols='):
                    raise ValueError("Second line must specify number of columns (cols=X)")
                
                try:
                    rows = int(lines[0].split('=')[1])
                    cols = int(lines[1].split('=')[1])
                except (IndexError, ValueError):
                    raise ValueError("Invalid row or column specification")
                
                # Create the matrix
                matrix = cls(rows, cols)
                
                # Parse elements
                for i, line in enumerate(lines[2:], start=3):
                    if not (line.startswith('(') and line.endswith(')')):
                        raise ValueError(f"Line {i}: Element must be in format (row, col, value)")
                    
                    # Remove parentheses and split by comma
                    content = line[1:-1].split(',')
                    
                    if len(content) != 3:
                        raise ValueError(f"Line {i}: Element must have exactly 3 components")
                    
                    try:
                        r = int(content[0].strip())
                        c = int(content[1].strip())
                        v = int(content[2].strip())
                    except ValueError:
                        raise ValueError(f"Line {i}: All components must be integers")
                    
                    # Set the element (this will validate indexes)
                    matrix.set(r, c, v)
                
                return matrix
                
        except FileNotFoundError:
            raise FileNotFoundError(f"Could not open file: {filepath}")
        except Exception as e:
            if isinstance(e, ValueError):
                raise
            raise ValueError(f"Error parsing file: {str(e)}")
    
    def set(self, row: int, col: int, value: int) -> None:
        """
        Set the value at the specified position.
        
        Args:
            row: Row index (0-based)
            col: Column index (0-based)
            value: Value to set
            
        Raises:
            IndexError: If row or column is out of bounds
        """
        # Validate indices
        if not (0 <= row < self.rows and 0 <= col < self.cols):
            raise IndexError(f"Index ({row}, {col}) out of bounds for matrix size {self.rows}×{self.cols}")
        
        # If setting to zero, remove the element
        if value == 0:
            if (row, col) in self.elements:
                del self.elements[(row, col)]
                del self.row_map[row][col]
                del self.col_map[col][row]
                
                # Clean up empty dictionaries
                if not self.row_map[row]:
                    del self.row_map[row]
                if not self.col_map[col]:
                    del self.col_map[col]
                    
                self.num_nonzero -= 1
        else:
            # Only increment if it's a new non-zero element
            if (row, col) not in self.elements:
                self.num_nonzero += 1
                
            # Update all data structures
            self.elements[(row, col)] = value
            self.row_map[row][col] = value
            self.col_map[col][row] = value
    
    def get(self, row: int, col: int) -> int:
        """
        Get the value at the specified position.
        
        Args:
            row: Row index (0-based)
            col: Column index (0-based)
            
        Returns:
            The value at the position, or 0 if not set
            
        Raises:
            IndexError: If row or column is out of bounds
        """
        if not (0 <= row < self.rows and 0 <= col < self.cols):
            raise IndexError(f"Index ({row}, {col}) out of bounds for matrix size {self.rows}×{self.cols}")
            
        return self.elements.get((row, col), 0)
    
    def add(self, other: 'SparseMatrix') -> 'SparseMatrix':
        """
        Add this matrix with another matrix.
        
        Args:
            other: The matrix to add
            
        Returns:
            A new matrix containing the sum
            
        Raises:
            ValueError: If matrix dimensions don't match
        """
        start_time = time.time()
        
        if self.rows != other.rows or self.cols != other.cols:
            raise ValueError(f"Cannot add matrices of different dimensions: "
                           f"{self.rows}×{self.cols} and {other.rows}×{other.cols}")
        
        result = SparseMatrix(self.rows, self.cols)
        
        # Method 1: Process each matrix separately (more efficient for very sparse matrices)
        if self.num_nonzero + other.num_nonzero < 0.01 * self.rows * self.cols:
            # Process elements from first matrix
            for (r, c), v in self.elements.items():
                result.set(r, c, v)
                
            # Process elements from second matrix
            for (r, c), v in other.elements.items():
                new_val = result.get(r, c) + v
                result.set(r, c, new_val)
        else:
            # Method 2: Process unique positions across both matrices
            # Get all positions that have non-zero values in either matrix
            positions = set(self.elements.keys()) | set(other.elements.keys())
            
            for r, c in positions:
                val = self.get(r, c) + other.get(r, c)
                if val != 0:  # Only store non-zero results
                    result.set(r, c, val)
        
        self._last_operation_time = time.time() - start_time
        return result
    
    def subtract(self, other: 'SparseMatrix') -> 'SparseMatrix':
        """
        Subtract another matrix from this matrix.
        
        Args:
            other: The matrix to subtract
            
        Returns:
            A new matrix containing the difference
            
        Raises:
            ValueError: If matrix dimensions don't match
        """
        start_time = time.time()
        
        if self.rows != other.rows or self.cols != other.cols:
            raise ValueError(f"Cannot subtract matrices of different dimensions: "
                           f"{self.rows}×{self.cols} and {other.rows}×{other.cols}")
        
        result = SparseMatrix(self.rows, self.cols)
        
        # Method 1: Process each matrix separately
        if self.num_nonzero + other.num_nonzero < 0.01 * self.rows * self.cols:
            # Process elements from first matrix
            for (r, c), v in self.elements.items():
                result.set(r, c, v)
                
            # Process elements from second matrix (subtract)
            for (r, c), v in other.elements.items():
                new_val = result.get(r, c) - v
                result.set(r, c, new_val)
        else:
            # Method 2: Process all positions that have non-zero values in either matrix
            positions = set(self.elements.keys()) | set(other.elements.keys())
            
            for r, c in positions:
                val = self.get(r, c) - other.get(r, c)
                if val != 0:  # Only store non-zero results
                    result.set(r, c, val)
        
        self._last_operation_time = time.time() - start_time
        return result
    
    def multiply(self, other: 'SparseMatrix') -> 'SparseMatrix':
        """
        Multiply this matrix with another matrix.
        
        Args:
            other: The matrix to multiply with
            
        Returns:
            A new matrix containing the product
            
        Raises:
            ValueError: If matrices cannot be multiplied due to dimension mismatch
        """
        start_time = time.time()
        
        if self.cols != other.rows:
            raise ValueError(f"Cannot multiply matrices with incompatible dimensions: "
                           f"{self.rows}×{self.cols} and {other.rows}×{other.cols}")
        
        result = SparseMatrix(self.rows, other.cols)
        
        # Optimization: Only iterate through non-empty rows and columns
        for row_idx in self.row_map:
            # For each row with non-zero elements
            row_data = self.row_map[row_idx]
            
            # Iterate through only the possible columns in the result
            for col_idx in other.col_map:
                # Compute dot product for this cell
                value = 0
                
                # Only consider columns in the first matrix that have matching rows in the second
                for k, v1 in row_data.items():
                    if k in other.row_map and col_idx in other.row_map[k]:
                        v2 = other.row_map[k][col_idx]
                        value += v1 * v2
                
                # Only set non-zero values
                if value != 0:
                    result.set(row_idx, col_idx, value)
        
        self._last_operation_time = time.time() - start_time
        return result
    
    def transpose(self) -> 'SparseMatrix':
        """
        Create a transposed version of this matrix.
        
        Returns:
            A new matrix that is the transpose of this matrix
        """
        result = SparseMatrix(self.cols, self.rows)
        
        # Swap rows and columns for each element
        for (r, c), v in self.elements.items():
            result.set(c, r, v)
            
        return result
    
    def to_file(self, filepath: str) -> None:
        """
        Write the matrix to a file.
        
        Args:
            filepath: Path where the matrix will be saved
        """
        with open(filepath, 'w') as file:
            # Write header
            file.write(f"rows={self.rows}\n")
            file.write(f"cols={self.cols}\n")
            
            # Write non-zero elements in sorted order
            for (r, c), v in sorted(self.elements.items()):
                file.write(f"({r}, {c}, {v})\n")
    
    def density(self) -> float:
        """
        Calculate the density of the matrix (proportion of non-zero elements).
        
        Returns:
            Density as a float between 0 and 1
        """
        total_cells = self.rows * self.cols
        if total_cells == 0:
            return 0.0
        return self.num_nonzero / total_cells
    
    def performance_stats(self) -> Dict[str, Union[int, float]]:
        """
        Get performance statistics for the matrix.
        
        Returns:
            Dictionary with statistics about the matrix and recent operations
        """
        return {
            'rows': self.rows,
            'cols': self.cols,
            'nonzero_elements': self.num_nonzero,
            'density': self.density(),
            'last_operation_time_ms': self._last_operation_time * 1000
        }


def create_example_files() -> None:
    """Create example matrix files for testing."""
    # Create matrix1.txt
    matrix1 = SparseMatrix(4, 5)
    matrix1.set(0, 0, 5)
    matrix1.set(0, 3, 8)
    matrix1.set(1, 1, 3)
    matrix1.set(1, 4, 12)
    matrix1.set(2, 2, 7)
    matrix1.set(3, 0, 4)
    matrix1.set(3, 3, 9)
    matrix1.to_file("examples/matrix1.txt")
    
    # Create matrix2.txt
    matrix2 = SparseMatrix(4, 5)
    matrix2.set(0, 0, 2)
    matrix2.set(0, 2, 6)
    matrix2.set(1, 1, 5)
    matrix2.set(2, 0, 8)
    matrix2.set(2, 3, 4)
    matrix2.set(3, 1, 1)
    matrix2.set(3, 4, 7)
    matrix2.to_file("examples/matrix2.txt")
    
    # Create matrix3.txt and matrix4.txt for multiplication testing
    matrix3 = SparseMatrix(3, 4)
    matrix3.set(0, 0, 2)
    matrix3.set(0, 2, 3)
    matrix3.set(1, 1, 5)
    matrix3.set(1, 3, 1)
    matrix3.set(2, 0, 4)
    matrix3.set(2, 2, 6)
    matrix3.to_file("examples/matrix3.txt")
    
    matrix4 = SparseMatrix(4, 2)
    matrix4.set(0, 0, 1)
    matrix4.set(0, 1, 2)
    matrix4.set(1, 0, 3)
    matrix4.set(2, 1, 4)
    matrix4.set(3, 0, 5)
    matrix4.to_file("examples/matrix4.txt")
    
    print("Example files created in 'examples' directory")


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Sparse Matrix Operations")
    
    # Command type
    parser.add_argument('command', choices=['add', 'subtract', 'multiply', 'create-examples'],
                       help="Operation to perform")
    
    # Input files
    parser.add_argument('--matrix1', help="Path to first matrix file")
    parser.add_argument('--matrix2', help="Path to second matrix file")
    
    # Output options
    parser.add_argument('--output', '-o', default=None,
                       help="Output file path (default: output_[operation].txt)")
    
    # Additional options
    parser.add_argument('--verbose', '-v', action='store_true',
                       help="Display detailed information")
    parser.add_argument('--benchmark', '-b', action='store_true',
                       help="Display performance information")
    
    return parser.parse_args()


def interactive_mode() -> None:
    """Run the program in interactive mode."""
    print("\nSparse Matrix Operations")
    print("========================")
    print("1. Addition")
    print("2. Subtraction")
    print("3. Multiplication")
    print("4. Create example files")
    print("0. Exit")
    
    try:
        choice = input("\nEnter your choice (0-4): ")
        
        if choice == '0':
            print("Exiting program.")
            return
        elif choice == '4':
            import os
            # Create examples directory if it doesn't exist
            os.makedirs("examples", exist_ok=True)
            create_example_files()
            return
        
        # Get file paths for operations
        file1 = input("Enter path to first matrix file: ")
        file2 = input("Enter path to second matrix file: ")
        
        # Load matrices
        try:
            print(f"Loading matrix 1 from {file1}...")
            matrix1 = SparseMatrix.from_file(file1)
            
            print(f"Loading matrix 2 from {file2}...")
            matrix2 = SparseMatrix.from_file(file2)
            
            # Perform operation
            if choice == '1':
                print("Performing addition...")
                result = matrix1.add(matrix2)
                output_file = "output_addition.txt"
            elif choice == '2':
                print("Performing subtraction...")
                result = matrix1.subtract(matrix2)
                output_file = "output_subtraction.txt"
            elif choice == '3':
                print("Performing multiplication...")
                result = matrix1.multiply(matrix2)
                output_file = "output_multiplication.txt"
            else:
                print("Invalid choice. Exiting.")
                return
            
            # Save result
            result.to_file(output_file)
            print(f"Operation successful. Result saved to {output_file}")
            
            # Show stats
            stats = result.performance_stats()
            print(f"\nResult matrix: {stats['rows']}×{stats['cols']} with {stats['nonzero_elements']} non-zero elements")
            print(f"Operation completed in {stats['last_operation_time_ms']:.2f} ms")
            
        except ValueError as e:
            print(f"Error: {e}")
        except FileNotFoundError as e:
            print(f"Error: File not found - {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")
            
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
    except Exception as e:
        print(f"Unexpected error: {e}")


def main() -> None:
    """Main function to run the program."""
    # Try to parse arguments - if none provided, run in interactive mode
    if len(sys.argv) == 1:
        interactive_mode()
        return
    
    args = parse_args()
    
    # Special case for creating examples
    if args.command == 'create-examples':
        import os
        os.makedirs("examples", exist_ok=True)
        create_example_files()
        return
    
    # Validate input for operations
    if not args.matrix1 or not args.matrix2:
        print("Error: Both matrix1 and matrix2 must be specified for operations.")
        return
    
    try:
        # Start timing
        start_time = time.time()
        
        if args.verbose:
            print(f"Loading matrix 1 from {args.matrix1}...")
        matrix1 = SparseMatrix.from_file(args.matrix1)
        
        if args.verbose:
            print(f"Loading matrix 2 from {args.matrix2}...")
        matrix2 = SparseMatrix.from_file(args.matrix2)
        
        # Perform operation
        if args.command == 'add':
            if args.verbose:
                print("Performing addition...")
            result = matrix1.add(matrix2)
            operation_name = "addition"
        elif args.command == 'subtract':
            if args.verbose:
                print("Performing subtraction...")
            result = matrix1.subtract(matrix2)
            operation_name = "subtraction"
        elif args.command == 'multiply':
            if args.verbose:
                print("Performing multiplication...")
            result = matrix1.multiply(matrix2)
            operation_name = "multiplication"
        
        # Save result
        output_file = args.output if args.output else f"output_{operation_name}.txt"
        
        if args.verbose:
            print(f"Writing result to {output_file}...")
        result.to_file(output_file)
        
        # Performance stats
        end_time = time.time()
        total_time = end_time - start_time
        
        print(f"Operation successful. Result saved to {output_file}")
        
        if args.verbose or args.benchmark:
            stats = result.performance_stats()
            print(f"\nPerformance details:")
            print(f"- Matrix 1: {matrix1.rows}×{matrix1.cols} with {matrix1.num_nonzero} non-zero elements")
            print(f"- Matrix 2: {matrix2.rows}×{matrix2.cols} with {matrix2.num_nonzero} non-zero elements")
            print(f"- Result: {result.rows}×{result.cols} with {result.num_nonzero} non-zero elements")
            print(f"- Total operation time: {total_time*1000:.2f} ms")
            print(f"- Matrix operation time: {stats['last_operation_time_ms']:.2f} ms")
        
    except ValueError as e:
        print(f"Error: {e}")
    except FileNotFoundError as e:
        print(f"Error: File not found - {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


if __name__ == "__main__":
    main()
