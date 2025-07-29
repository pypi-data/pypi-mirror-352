# zr
AdWords reporting tools

To install:	```pip install zr```

## Overview
The `zr` package provides a suite of tools designed to facilitate the reporting and analysis of Google AdWords campaigns. It includes functionality to handle AdWords client interactions, report downloading, and data transformation into user-friendly formats such as pandas DataFrames.

## Features
- **Client Management**: Easily manage AdWords client configurations and authenticate sessions.
- **Report Downloading**: Download various types of AdWords performance reports using flexible query options.
- **Data Processing**: Convert raw report data into structured pandas DataFrames, making it easier to analyze and visualize campaign performance.

## Installation
Install the package using pip:
```bash
pip install zr
```

## Usage

### Getting Started with Client Configuration
To interact with Google AdWords, you need to configure and authenticate a client. Here's how you can do it:
```python
from zr import get_client
client = get_client(clientCustomerId='your_customer_id')
```

### Downloading Reports
You can download reports by specifying the type of report and the format you need. Here's an example of downloading a search query performance report:
```python
from zr import get_report_downloader, download_report

# Get a report downloader instance
report_downloader = get_report_downloader(client='your_client_id')

# Define your report query
report_query_str = """
SELECT Query, Impressions, Clicks, Cost
FROM SEARCH_QUERY_PERFORMANCE_REPORT
WHERE CampaignStatus = ENABLED
DURING LAST_30_DAYS
"""

# Download the report as a DataFrame
df = download_report(
    report_downloader=report_downloader,
    report_query_str=report_query_str,
    download_format='df'
)
```

### Converting Reports to DataFrames
After downloading the report, you can convert it into a pandas DataFrame for easier manipulation and analysis:
```python
from zr import report_to_df

# Assuming 'report' is the raw data fetched from AdWords
df = report_to_df(report)
```

## Documentation
Each function in the `zr` package is documented with docstrings, providing a detailed description of its purpose, parameters, and return values. This allows users to understand and utilize the functionalities effectively without diving deep into the source code.

### Key Functions
- `get_client()`: Configure and return a Google AdWords client.
- `get_report_downloader()`: Get a downloader object that can be used to fetch reports based on the client configuration.
- `download_report()`: Download AdWords reports using AWQL (AdWords Query Language).
- `report_to_df()`: Convert the raw report data into a pandas DataFrame.

## Contributing
Contributions to the `zr` package are welcome! If you have suggestions for improvements or bug fixes, please feel free to fork the repository and submit a pull request.

## License
This project is licensed under the MIT License - see the LICENSE file for details.