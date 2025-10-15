# Detailed Prompt for Processing Shapefile Line Segments

You are tasked with writing a Python script using libraries such as `geopandas`, `shapely`, and other relevant geospatial libraries to process a shapefile containing multiple line segments as features. The goal is to filter, sort, and extract specific coordinates based on the following requirements. Please ensure the script is efficient, well-commented, and handles edge cases appropriately.

## Input Description
- The input is a shapefile containing multiple line segments, where each segment is a feature.
- Each feature has the following fields:
  - `span_name`: A string identifying a group of segments.
  - `segment_sequence`: An integer or string indicating the sequence order of the segment within its group.
  - `feature_type`: A string indicating the type of segment (e.g., "Bridge", "Road Cross", or other types).
  - Geometry: A LineString representing the line segment with coordinate points.
- The shapefile is assumed to be in a projected coordinate system (e.g., UTM) where distances can be calculated in meters.

## Processing Requirements
1. **Filtering and Sorting**:
   - Filter the segments based on a specific `span_name` provided as input.
   - Sort the filtered segments in ascending order based on the `segment_sequence` field.
2. **Coordinate Extraction**:
   - **First Coordinate**:
     - Identify the first segment in the sorted list (lowest `segment_sequence`).
     - Extract a coordinate that is 10 meters away from the start coordinate of this first segment, measured along the line segment.
   - **Second Coordinate**:
     - Starting from the first extracted coordinate, traverse the sorted segments sequentially to find the next coordinate based on one of the following conditions (whichever occurs first):
       - **Condition i**: A point that is 1800 meters away from the first extracted coordinate, measured along the path of the line segments.
       - **Condition ii**: A point at the start or end of a segment marked as "Bridge" or "Road Cross" in the `feature_type` field.
       - **Condition iii**: If the segment is marked as "Bridge" and its length is greater than 150 meters:
         - Extract two coordinates: one 50 meters before the start of the segment (in the opposite direction along the previous segment, if available) and one 50 meters beyond the end of the segment (along the next segment, if available).
       - **Condition iv**: If the segment is marked as "Bridge" and its length is 150 meters or less:
         - Select the start or end coordinate of the segment, whichever is farther from the previously extracted coordinate (i.e., the first extracted coordinate or any previously selected coordinate in the sequence).
     - The second coordinate should be the earliest point satisfying any of the above conditions when traversing the segments sequentially.

## Output Requirements
- The script should output:
  - The first coordinate (x, y) that is 10 meters from the start of the first segment.
  - The second coordinate (x, y) based on the conditions above, or multiple coordinates in the case of a long bridge (>150 meters).
  - If a bridge >150 meters is encountered, output the two coordinates (50 meters before start and 50 meters beyond end).
- The output should be in a clear format, such as a dictionary or list of coordinates with metadata (e.g., which condition was satisfied).
- Handle edge cases, such as:
  - Missing or invalid `span_name` or `segment_sequence`.
  - Segments with insufficient length to satisfy distance requirements.
  - Cases where no "Bridge" or "Road Cross" segments exist.
  - Cases where the total length of segments is less than 1800 meters.
  - Invalid geometries or empty shapefiles.

## Additional Guidelines
- Use `geopandas` to read and manipulate the shapefile.
- Use `shapely` for geometric operations like calculating distances, interpolating points, and extending lines.
- Ensure the script is robust and includes error handling for invalid inputs or unexpected data.
- Include comments explaining the logic for each major step.
- Assume distances are calculated in meters and the shapefile is in a suitable projected coordinate system.
- If external libraries are required beyond `geopandas` and `shapely`, specify them clearly.
- Provide a sample usage example with a hypothetical shapefile path and `span_name`.

## Example Usage
```python
shapefile_path = "path/to/shapefile.shp"
span_name = "span_1"
coordinates = process_shapefile(shapefile_path, span_name)
print("First Coordinate:", coordinates["first"])
print("Second Coordinate(s):", coordinates["second"])
```

## Expected Output Format
```python
{
    "first": (x1, y1),
    "second": [(x2, y2), ...],  # List to accommodate multiple coordinates for long bridges
    "condition_met": "distance_1800m | bridge_short | bridge_long | road_cross",
    "segment_id": "ID of the segment where second coordinate was found, if applicable"
}
```

Please provide a complete Python script that meets these requirements, including all necessary imports, functions, and error handling. Ensure the script is tested with a sample dataset or includes instructions for creating a sample shapefile for testing.