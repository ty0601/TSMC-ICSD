import pandas as pd

# Re-loading the data to address the issue with non-numeric columns
cloud_data = pd.read_csv('./merged_cloud_data.csv')

# Dropping non-numeric columns before calculating statistics
cloud_data_numeric = cloud_data.select_dtypes(include=['number'])

# Recalculating the mean, standard deviation, minimum, and maximum for numeric columns
mean_values = cloud_data_numeric.mean()
std_values = cloud_data_numeric.std()
min_values = cloud_data_numeric.min()
max_values = cloud_data_numeric.max()

# Creating a summary DataFrame
summary_stats_numeric = pd.DataFrame({'Mean': mean_values,
                                      'Standard Deviation': std_values,
                                      'Minimum': min_values,
                                      'Maximum': max_values})

# Saving the summary statistics to a CSV file
output_file_path = './summary_statistics_numeric.csv'
summary_stats_numeric.to_csv(output_file_path, index=True)