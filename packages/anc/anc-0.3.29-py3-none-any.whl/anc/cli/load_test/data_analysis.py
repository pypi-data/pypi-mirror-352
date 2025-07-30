import json
import numpy as np
import os
import traceback
def read_benchmark_results(file_path):
    with open(file_path, "r") as f:
        return json.load(f)

def analyze_benchmark_results_anc(file_path, base_result_dir, first_sentence_len=50):
    """
    Analyze benchmark results by creating a pandas DataFrame and generating summary statistics.
    
    Args:
        benchmark_results_list: List of benchmark result dictionaries
        base_result_dir: Directory to save analysis results
    """
    try:
        import pandas as pd
        import matplotlib.pyplot as plt
        import numpy as np
    except ImportError as e:
        print("Missing optional dependencies for analysis: pandas, matplotlib, numpy")
        print("Install them with: pip install pandas matplotlib numpy")
        return
    
    try:
        # Check if file_path is a directory or a single file
        all_results = []
        if os.path.isdir(file_path):
            # Process all JSON files in the directory
            print(f"Processing all JSON files in the directory: {file_path}")
            json_files = [f for f in os.listdir(file_path) if f.endswith('.json')]
            for json_file in json_files:
                full_path = os.path.join(file_path, json_file)
                file_results = read_benchmark_results(full_path)
                # Add filename as a column (without .json extension)
                file_name = os.path.basename(json_file).replace('.json', '')
                for result in file_results:
                    result['file_name'] = file_name
                all_results.extend(file_results)
        else:
            # Process a single file
            file_results = read_benchmark_results(file_path)
            file_name = os.path.basename(file_path).replace('.json', '')
            for result in file_results:
                result['file_name'] = file_name
            all_results.extend(file_results)
            
        # Convert list of dictionaries to DataFrame
        df = pd.DataFrame(all_results)

        # Recalculate request_throughput and output_throughput based on tensor_parallel_size
        if 'tensor_parallel_size' in df.columns and 'request_throughput' in df.columns:
            # Convert tensor_parallel_size to numeric type to avoid TypeError
            df['tensor_parallel_size'] = pd.to_numeric(df['tensor_parallel_size'])
            df['request_throughput'] = df['request_throughput'] * 8 / df['tensor_parallel_size']
        
        if 'tensor_parallel_size' in df.columns and 'output_throughput' in df.columns:
            # Ensure tensor_parallel_size is numeric
            if not pd.api.types.is_numeric_dtype(df['tensor_parallel_size']):
                df['tensor_parallel_size'] = pd.to_numeric(df['tensor_parallel_size'])
            df['output_throughput'] = df['output_throughput'] * 8 / df['tensor_parallel_size']

        grid_search_columns = ["enable_chunked_prefill",
                               "enable_prefix_caching",
                               "use-v2-block-manager",
                               "multi-step-stream-outputs",
                               "tensor_parallel_size",
                               "speculative-draft-tensor-parallel-size",
                               "num-speculative-tokens"]
        
        select_columns = ["request_throughput",
                          "output_throughput", 
                          "mean_output_token_len",
                          "mean_input_token_len",
                          "p90_input_token_len",
                          "max_concurrency", 
                          "mean_ttfs_ms",
                          "std_ttfs_ms",
                          "p90_ttfs_ms",
                          "mean_tpot_ms",
                          "std_tpot_ms",
                          "p90_tpot_ms",
                          "mean_ttft_ms",
                          "std_ttft_ms",
                          "p90_ttft_ms",
                          "mean_e2el_ms",
                          "std_e2el_ms",
                          "p90_e2el_ms",
                          "mean_fs_token_len",
                          "std_fs_token_len",
                          "p90_fs_token_len",
         ]
        if 'file_name' in df.columns:
            select_columns = ["file_name"] + select_columns

        if first_sentence_len:
            recalculate_ttfs(df, first_sentence_len=first_sentence_len)
        # Filter out columns that have only a single unique value
        # df = df[(df["enable_prefix_caching"] == "True") ]
        # df = df[(df["enable_prefix_caching"] == "True") & (df["max_concurrency"]<=8) & (df["speculative-draft-tensor-parallel-size"]=="4")]
        
        all_selected_columns = grid_search_columns + select_columns
        filtered_columns = []
        for col in all_selected_columns:
            if col in df.columns:
                if df[col].nunique() > 1:
                    filtered_columns.append(col)
        df = df[filtered_columns]
        df.to_csv(os.path.join(base_result_dir, "benchmark_results.csv"), index=False)
        print(f"Data frame of Benchmark results saved to {os.path.join(base_result_dir, 'benchmark_results.csv')}")
        # Rename columns
        renamed_grid_search_columns = {
            "enable_chunked_prefill": "chunkfill",
            "enable_prefix_caching": "precache",
            "tensor_parallel_size": "TP",
            "file_name": "file",
            "speculative-draft-tensor-parallel-size": "sp_tp",
            "num-speculative-tokens": "k"
        }
        # Calculate TTFS as TTFT + TPOT * output_token_len
        #recalculate_ttfs(df)
            
        df.rename(columns=renamed_grid_search_columns, inplace=True)
        
        # Create a figure with 4 subfigures
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
        
        # Create groups based on configuration parameters
        # Use grid_search_columns to create unique configuration identifiers
        df['config_id'] = df.apply(lambda row: '_'.join([f"{col}_{row[col]}" for col in renamed_grid_search_columns.values() if col in row]), axis=1)
        
        # Get unique configuration IDs
        config_ids = df['config_id'].unique()
        
        # Create groups based on configuration
        groups = []
        for config_id in config_ids:
            group_df = df[df['config_id'] == config_id]
            if not group_df.empty:
                groups.append((config_id, group_df))
        
        # Use different colors for different configurations
        colors = plt.cm.viridis(np.linspace(0, 1, len(groups)))
        
        # Define metrics to plot
        mean_metrics = [
            ('mean_ttft_ms', 'Mean TTFT (ms)'),
            ('mean_tpot_ms', 'Mean TPOT (ms)'),
            ('mean_ttfs_ms', 'Mean TTFS (ms)'),
            ('mean_e2el_ms', 'Mean E2EL (ms)')
        ]
        
        p90_metrics = [
            ('p90_ttft_ms', 'P90 TTFT (ms)'),
            ('p90_tpot_ms', 'P90 TPOT (ms)'),
            ('p90_ttfs_ms', 'P90 TTFS (ms)'),
            ('p90_e2el_ms', 'P90 E2EL (ms)')
        ]
        
        # Function to create plots with given x-axis
        def create_performance_plots(y_axis, y_label, filename, swap_axes=False):
            # default x-axis is max_concurrency
            fig, axes = plt.subplots(2, 4, figsize=(20, 10))
            
            # Flatten axes for easier iteration
            axes = axes.flatten()
            
            # Helper function to create a plot for a metric
            def plot_metric(ax, metric, metric_label, y_axis_name, groups_data, swap_axes=swap_axes):
                # Define different marker styles for different configurations
                markers = ['o', 's', '^', 'D', 'v', '<', '>', 'p', '*', 'h', 'H', '+', 'x', '|']
                
                for j, (config_id, group) in enumerate(groups_data):
                    # Use different marker styles based on configuration
                    marker_idx = j % len(markers)
                    marker_style = markers[marker_idx]
                    
                    if swap_axes:
                        ax.scatter(group[y_axis], group[metric],
                                  label=config_id, 
                                  color=colors[j], marker=marker_style, s=70)
                        ax.plot(group[y_axis], group[metric],
                               color=colors[j], linestyle='-')
                        ax.set_xlabel(y_label)
                        ax.set_ylabel(metric_label)
                        ax.set_title(f'{y_label} vs {metric_label}')
                    else:
                        ax.scatter(group[metric], group[y_axis],
                                  label=config_id, 
                                  color=colors[j], marker=marker_style, s=70)
                        ax.plot(group[metric], group[y_axis],
                               color=colors[j], linestyle='-')
                        ax.set_ylabel(y_label)
                        ax.set_xlabel(metric_label)
                        ax.set_title(f'{metric_label} vs {y_label}')
                        # ax.set_xlim(right=4000)
                        # ax.set_ylim(top=7)
                ax.grid(True)
                
                # Only add legend to the first graph (index 0)
                if ax == axes[0]:
                    ax.legend(fontsize='x-small', loc='upper right', frameon=True)
            
            # Create two sets of plots - one with default axes and one with swapped axes
            # Plot mean metrics (first row)
            for i, (metric, ylabel) in enumerate(mean_metrics):
                plot_metric(axes[i], metric, ylabel, y_label, groups, swap_axes=swap_axes)
            
            # Plot p90 metrics (second row)
            for i, (metric, ylabel) in enumerate(p90_metrics):
                plot_metric(axes[i+4], metric, ylabel, y_label, groups, swap_axes=swap_axes)
            
            plt.tight_layout()
            plt.savefig(os.path.join(base_result_dir, filename))
            plt.close()
        # Create plots with concurrency as x-axis
        create_performance_plots('max_concurrency', 'Concurrency', 'concurrency_analysis.png', swap_axes=True)
        
        # Create plots with request throughput as x-axis
        create_performance_plots('request_throughput', 'Request Throughput', 'throughput_analysis.png')
            
    except ImportError as e:
        print(f"Could not analyze results: {e}")
        print("To enable analysis, install pandas and matplotlib: pip install pandas matplotlib")
    except Exception as e:
        print(f"Error analyzing benchmark results: {e}")
        print(traceback.format_exc())

def analyze_benchmark_results(file_path, base_result_dir):
    """
    Analyze benchmark results by creating a pandas DataFrame and generating summary statistics.
    
    Args:
        benchmark_results_list: List of benchmark result dictionaries
        base_result_dir: Directory to save analysis results
    """
    try:
        import pandas as pd
        import matplotlib.pyplot as plt

        benchmark_results_list = read_benchmark_results(file_path)
        # Convert list of dictionaries to DataFrame
        df = pd.DataFrame(benchmark_results_list)

        select_columns = ["request_throughput",
                          "output_throughput", 
                          "tensor_parallel_size", 
                          "mean_output_token_len",
                          "mean_input_token_len",
                          "max_concurrency", 
                          "mean_ttfs_ms",
                          "std_ttfs_ms",
                          "p90_ttfs_ms",
                          "mean_tpot_ms",
                          "std_tpot_ms",
                          "p90_tpot_ms",
                          "mean_ttft_ms",
                          "std_ttft_ms",
                          "p90_ttft_ms",
                          "mean_e2el_ms",
                          "std_e2el_ms",
                          "p90_e2el_ms"]
        # Calculate TTFS as TTFT + TPOT * output_token_len
        recalculate_ttfs(df, first_sentence_len=20)
            
        df = df[select_columns]

        df.to_csv(os.path.join(base_result_dir, "benchmark_results.csv"), index=False)
        print(f"Data frame of Benchmark results saved to {os.path.join(base_result_dir, 'benchmark_results.csv')}")
        
        # Create a figure with 4 subfigures
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
        
        # Group data by input token length and output token length
        distinct_input_lens = df['mean_input_token_len'].drop_duplicates().values
        distinct_output_lens = df['mean_output_token_len'].drop_duplicates().values
        
        # Create groups based on both input and output token lengths
        groups = []
        for input_len in distinct_input_lens:
            input_df = df[df['mean_input_token_len'] == input_len]
            for output_len in distinct_output_lens:
                group_df = input_df[input_df['mean_output_token_len'] == output_len]
                if not group_df.empty:
                    groups.append((input_len, output_len, group_df))
        
        # Use different colors for different combinations
        colors = plt.cm.viridis(np.linspace(0, 1, len(groups)))
        
        # Define metrics to plot
        mean_metrics = [
            ('mean_ttft_ms', 'Mean TTFT (ms)'),
            ('mean_tpot_ms', 'Mean TPOT (ms)'),
            ('mean_ttfs_ms', 'Mean TTFS (ms)'),
            ('mean_e2el_ms', 'Mean E2EL (ms)')
        ]
        
        p90_metrics = [
            ('p90_ttft_ms', 'P90 TTFT (ms)'),
            ('p90_tpot_ms', 'P90 TPOT (ms)'),
            ('p90_ttfs_ms', 'P90 TTFS (ms)'),
            ('p90_e2el_ms', 'P90 E2EL (ms)')
        ]
        
        # Function to create plots with given x-axis
        def create_performance_plots(y_axis, y_label, filename, swap_axes=False):
            fig, axes = plt.subplots(2, 4, figsize=(20, 10))
            
            # Flatten axes for easier iteration
            axes = axes.flatten()
            
            # Plot mean metrics (first row)
            # Helper function to create a plot for a metric
            def plot_metric(ax, metric, metric_label, y_axis_name, groups_data, swap_axes=swap_axes):
                # Define different marker styles for different output token lengths
                markers = ['o', 's', '^', 'D', 'v', '<', '>', 'p', '*', 'h', 'H', '+', 'x', '|']
                
                for j, (input_len, output_len, group) in enumerate(groups_data):
                    # Use different marker styles based on output token length
                    marker_idx = list(distinct_output_lens).index(output_len) % len(markers)
                    marker_style = markers[marker_idx]
                    
                    if swap_axes:
                        ax.scatter(group[y_axis], group[metric],
                                  label=f'In: {input_len}, Out: {output_len}', 
                                  color=colors[j], marker=marker_style, s=70)
                        ax.plot(group[y_axis], group[metric],
                               color=colors[j], linestyle='-')
                        ax.set_xlabel(y_label)
                        ax.set_ylabel(metric)
                        ax.set_title(f'{y_label} vs {metric}')
                    else:
                        ax.scatter(group[metric], group[y_axis],
                                  label=f'In: {input_len}, Out: {output_len}', 
                                  color=colors[j], marker=marker_style, s=70)
                        ax.plot(group[metric], group[y_axis],
                               color=colors[j], linestyle='-')
                        ax.set_ylabel(y_label)
                        ax.set_xlabel(metric)
                        ax.set_title(f'{metric} vs {y_label}')
                ax.grid(True)
                ax.legend()
            
            # Create two sets of plots - one with default axes and one with swapped axes
            # Plot mean metrics (first row) - default axes
            for i, (metric, ylabel) in enumerate(mean_metrics):
                plot_metric(axes[i], metric, ylabel, y_label, groups, swap_axes=swap_axes)
            
            # Plot p90 metrics (second row) - default axes
            for i, (metric, ylabel) in enumerate(p90_metrics):
                plot_metric(axes[i+4], metric, ylabel, y_label, groups, swap_axes=swap_axes)
            
            plt.tight_layout()
            plt.savefig(os.path.join(base_result_dir, filename))
            plt.close()
            
        # Create plots with concurrency as x-axis
        create_performance_plots('max_concurrency', 'Concurrency', 'concurrency_analysis.png', swap_axes=True)
        
        # Create plots with request throughput as x-axis
        create_performance_plots('request_throughput', 'Request Throughput', 'throughput_analysis.png')
            
    except ImportError as e:
        print(f"Could not analyze results: {e}")
        print("To enable analysis, install pandas and matplotlib: pip install pandas matplotlib")
    except Exception as e:
        print(f"Error analyzing benchmark results: {e}")

def recalculate_ttfs(df, first_sentence_len):
    if 'mean_ttfs_ms' in df.columns and 'mean_ttft_ms' in df.columns and 'mean_tpot_ms' in df.columns and 'mean_output_token_len' in df.columns:
        df['mean_ttfs_ms'] = df['mean_ttft_ms'] + df['mean_tpot_ms'] * first_sentence_len
            
    if 'p90_ttfs_ms' in df.columns and 'p90_ttft_ms' in df.columns and 'p90_tpot_ms' in df.columns and 'p90_output_token_len' in df.columns:
        df['p90_ttfs_ms'] = df['p90_ttft_ms'] + df['p90_tpot_ms'] * first_sentence_len
            
    if 'std_ttfs_ms' in df.columns and 'std_ttft_ms' in df.columns and 'std_tpot_ms' in df.columns and 'std_output_token_len' in df.columns:
            # This is an approximation for std of sum of dependent variables
        df['std_ttfs_ms'] = np.sqrt(df['std_ttft_ms']**2 + (df['std_tpot_ms'] * first_sentence_len)**2)
    # Save the raw DataFrame to CSV