from methods import *
block = "Gangev"

if __name__ == "__main__":
    #Creating the RoW Authorities Shape File
    input_file = f"input/{block}/OFC_NEW.shp"
    output_file = f"input/{block}/RoW Authorities-{block}.shp"
    input_gdf = process_shapefile(input_file, output_file)

    #creating the output points shape file and Json for span
    input_shape_file = output_file
    output_shape_file = f"input/{block}/output_points-{block}.shp"
    output_json = f"input/{block}/span_details-{block}.json"
    gdf = gpd.read_file(input_shape_file)
    output_gdf, span_details = process_span_data(gdf, output_shape_file, output_json)
    print("✅ Output Points Shape file, Json, ROW Auth Saved ")

    # creating the  Json for ring data
    print("_______________Processing Ring data Json______________")
    input_file = output_json
    output_file = f"input/{block}/ring_details_{block}.json"
    with open(input_file, "r") as f:
        data = json.load(f)
    grouped = defaultdict(lambda: {"spans": {}, "meta": {}})
    for span_name, span_data in data.items():
        ring = span_data.get("Ring", "UNKNOWN")
        grouped[ring]["spans"][span_name] = span_data
    # Now calculate meta info for each ring
    for ring, ring_data in grouped.items():
        total_length = 0.0
        category_sums = defaultdict(float)
        total_spans = len(ring_data["spans"])
        for span_name, span_data in ring_data["spans"].items():
            for key, value in span_data.items():
                if isinstance(value, (int, float)):
                    category_sums[key] += value
                    total_length += value
        ring_data["meta"] = {
            "total_length": total_length,
            "total_spans": total_spans,
            "row_autho": dict(category_sums)
        }
    # Write output JSON
    with open(output_file, "w") as f:
        json.dump(grouped, f, indent=4)
    print(f"✅ Grouped JSON for ring data written")

# Creating the Shape file data for ring output points
    print("________________Processing Ring Data Json_______________")
    inp = f"input/{block}/ROW Authorities-{block}.shp"
    outp = f"input/{block}/output_points_rings-{block}.shp"
    process(inp, outp)