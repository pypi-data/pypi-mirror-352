def merge_results(results: list):
    """Merge results from multiple tools."""
    merged_results = []
    for result in results:
        if isinstance(result, list):
            merged_results.extend(result)
        else:
            merged_results.append(result)
    return merged_results


import datetime

def format_diagnostic(diagnostic: str):
    """Format diagnostic information."""
    timestamp = datetime.datetime.now().isoformat()
    return f"{timestamp} - {diagnostic}"
