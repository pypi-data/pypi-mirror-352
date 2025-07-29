"""Utility functions for the mlfastflow package."""

import time
import functools

def timer_decorator(func):
    """
    A decorator that prints the execution time of the function it decorates.
    """
    @functools.wraps(func)  # Preserves function metadata (name, docstring, etc.)
    def wrapper_timer(*args, **kwargs):
        start_time = time.perf_counter()  # More precise for short durations
        value = func(*args, **kwargs)
        end_time = time.perf_counter()
        run_time = end_time - start_time
        print(f"Finished {func.__name__!r} in {run_time:.4f} secs")
        return value
    return wrapper_timer


def concat_files(folder_path, file_type='csv', add_source_column=False):
    """Concatenate all files in a folder and its subfolders.
    
    Args:
        folder_path (str): Path to the folder containing files to concatenate
        file_type (str): File extension to look for ('csv' or 'parquet')
        add_source_column (bool): If True, adds a 'SOURCE' column with the filename
    
    Returns:
        str: Path to the concatenated output file
    """
    import os
    import polars as pl
    from pathlib import Path
    
    # Ensure proper path handling
    file_path = Path(folder_path)
    parent_dir = file_path.parent
    folder_name = file_path.name
    
    # Define output filename at the same level as input folder
    output_file = parent_dir / f"{folder_name}_combined.{file_type}"
    
    # Get all files with the specified extension in the folder and subfolders
    all_files = []
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.endswith(f".{file_type}"):
                all_files.append(os.path.join(root, file))
    
    if not all_files:
        print(f"No .{file_type} files found in {folder_path}")
        return None
    
    print(f"Found {len(all_files)} .{file_type} files to combine")
    
    # Read and concatenate all files
    dataframes = []
    for file in all_files:
        try:
            if file_type.lower() == 'csv':
                df = pl.read_csv(file)
            elif file_type.lower() == 'parquet':
                df = pl.read_parquet(file)
            else:
                raise ValueError(f"Unsupported file type: {file_type}")
                
            # Add source column if requested
            if add_source_column:
                # Extract just the filename without path
                filename = os.path.basename(file)
                # # Extract just the filename without path and extension
                # filename = os.path.splitext(os.path.basename(file))[0]
                # Add the SOURCE column with the filename
                df = df.with_columns(pl.lit(filename).alias("SOURCE"))
                
            dataframes.append(df)
        except Exception as e:
            print(f"Error reading file {file}: {str(e)}")
    
    if not dataframes:
        print("No valid dataframes to concatenate")
        return None
    
    # Concatenate all dataframes
    combined_df = pl.concat(dataframes)
    
    # Save the combined dataframe
    if file_type.lower() == 'csv':
        combined_df.write_csv(output_file)
    elif file_type.lower() == 'parquet':
        combined_df.write_parquet(output_file)
    
    print(f"Combined {len(dataframes)} files into {output_file}")
    return str(output_file)


def profile(
        df,
        title: str = "Pandas Profiling Report",
        output_path: str = None,
        minimal: bool = True,
    ):
    """Generate a pandas profiling report for a dataframe.
    
    Args:
        df: A polars or pandas DataFrame
        title: Title of the report
        output_path: Directory path where the HTML report will be saved.
            If None, saves to current directory
        minimal: Whether to generate a minimal report (faster) or a complete report
        
    Returns:
        ProfileReport object
    """
    # Import ProfileReport from ydata-profiling
    try:
        from ydata_profiling import ProfileReport
    except ImportError:
        raise ImportError("Please install ydata-profiling: pip install ydata-profiling")
    
    # Import required modules
    import pandas as pd
    import os
    import warnings
    
    # Suppress irrelevant warnings
    warnings.filterwarnings("ignore", message=".*IProgress not found.*")
    
    # Disable promotional banners
    os.environ["YDATA_PROFILING_DISABLE_PREMIUM_BANNER"] = "1"
    
    # Convert to pandas DataFrame if necessary
    if hasattr(df, 'to_pandas'):
        # This is a polars DataFrame
        pandas_df = df.to_pandas()
    else:
        # Assume it's already a pandas DataFrame
        pandas_df = df
    
    # Check for empty DataFrame
    if len(pandas_df) == 0:
        print("Warning: Cannot profile an empty DataFrame")
        return None
    
    # Create the profiling report
    profile = ProfileReport(
        pandas_df,
        title=title,
        minimal=minimal,  # Simple toggle between minimal and complete report
    )
    
    # Create filename from title
    filename = title.replace(" ", "_") + ".html"
    
    # Determine full output path
    if output_path is not None:
        # Ensure output_path exists
        os.makedirs(output_path, exist_ok=True)
        # Combine directory path with filename
        full_path = os.path.join(output_path, filename)
    else:
        # Use current directory if no output_path provided
        full_path = filename
    
    # Try to save the report
    try:
        profile.to_file(full_path)
        print(f"Profile report saved to {full_path}")
    except Exception as e:
        print(f"Error saving profile report: {str(e)}")
        print("This may happen with problematic data. Try with different data or parameters.")
    
    # Create a non-displaying wrapper to prevent showing in Jupyter
    class NoDisplayProfileReport:
        def __init__(self, profile_report):
            self._profile = profile_report
            
        def to_file(self, *args, **kwargs):
            return self._profile.to_file(*args, **kwargs)
            
        # Block the _repr_html_ method that causes automatic display in Jupyter
        def _repr_html_(self):
            return None
            
        # Provide access to other methods of the original profile
        def __getattr__(self, name):
            return getattr(self._profile, name)
            
    return NoDisplayProfileReport(profile)



def csv2parquet(input_dir, output_dir=None, sub_folders=False, schema_overrides=None):
    """
    Convert CSV file(s) to Parquet format using Polars with LazyFrame for better performance.
    
    Args:
        input_dir (str): Path to a CSV file or directory containing CSV files
        output_dir (str, optional): Directory to save the Parquet files. If None, saves in the same location as input.
        sub_folders (bool, optional): If True and input_dir is a directory, process subfolders recursively. Default is False.
        
    Returns:
        list: List of paths to the created Parquet files
    """
    import os
    import polars as pl
    from pathlib import Path
    
    # Normalize path to handle both "/path/folder" and "/path/folder/" formats
    input_path = Path(input_dir).resolve()
    
    # Prepare output directory if specified
    if output_dir:
        output_path = Path(output_dir).resolve()
        output_path.mkdir(parents=True, exist_ok=True)
    else:
        output_path = None
    
    created_files = []
    
    # Case 1: Input is a file
    if input_path.is_file():
        if input_path.suffix.lower() != '.csv':
            print(f"Warning: {input_path} is not a CSV file. Skipping.")
            return created_files
        
        # Determine output path
        if output_path:
            output_file = output_path / f"{input_path.stem}.parquet"
        else:
            output_file = input_path.with_suffix('.parquet')
        
        # Convert CSV to Parquet using LazyFrame for better performance
        try:
            print(f"Converting {input_path} to {output_file}")
            (pl.scan_csv(input_path, schema_overrides=schema_overrides)
                .collect()
                .write_parquet(output_file))
            created_files.append(str(output_file))
            print(f"Converted {input_path} to {output_file}")
        except Exception as e:
            print(f"Error converting {input_path}: {str(e)}")
    
    # Case 2: Input is a directory
    elif input_path.is_dir():
        if sub_folders:
            # Process directory and all subdirectories
            walk_gen = os.walk(input_path)
        else:
            # Process only the top directory
            walk_gen = [(input_path, [], [f.name for f in input_path.glob('*.csv')])]
        
        for root, _, files in walk_gen:
            root_path = Path(root)
            
            # Create corresponding output directory structure if output_dir is specified
            if output_path:
                rel_path = root_path.relative_to(input_path) if root_path != input_path else Path('')
                current_output_dir = output_path / rel_path
                current_output_dir.mkdir(parents=True, exist_ok=True)
            else:
                current_output_dir = root_path
            
            # Process each CSV file in the current directory
            for file in files:
                file_path = root_path / file
                
                # Skip non-CSV files
                if file_path.suffix.lower() != '.csv':
                    continue
                
                # Determine output file path
                output_file = current_output_dir / f"{file_path.stem}.parquet"
                
                # Convert CSV to Parquet using LazyFrame for better performance
                try:
                    print(f"Converting {file_path} to {output_file}")
                    (pl.scan_csv(file_path, schema_overrides=schema_overrides)
                        .collect()
                        .write_parquet(output_file))
                    created_files.append(str(output_file))
                    print(f"Converted {file_path} to {output_file}")
                except Exception as e:
                    print(f"Error converting {file_path}: {str(e)}")
    
    else:
        print(f"Error: {input_dir} is neither a file nor a directory")
    
    if created_files:
        print(f"Created {len(created_files)} parquet file(s)")
    else:
        print("No files were converted")
    
    return created_files







