# Import necessary libraries
import arcpy
import os
import subprocess

# Define input and output parameters
inputDEM = arcpy.GetParameterAsText(0)
fia = arcpy.GetParameterAsText(1)
hexagons = arcpy.GetParameterAsText(2)
saga_cmd_path = arcpy.GetParameterAsText(3)
workspace = arcpy.GetParameterAsText(4)
output_layer = arcpy.GetParameterAsText(5)

# Create workspace
os.makedirs(workspace, exist_ok=True)
arcpy.env.workspace = workspace
arcpy.AddMessage(f"Workspace set to {workspace}")

# Define paths for intermediate outputs
correctedDEM = os.path.join(workspace, "correctedDEM.tif") # hier noch überall die paths hinzufügen
flow_direction = os.path.join(workspace, "flowDirection.tif")
flow_acc = os.path.join(workspace, "flowAcc.tif")
slope_path = os.path.join(workspace, "slope.tif")
stream_network_path = os.path.join(workspace, "extracted_streams.tif")
accumulated_cost_path = os.path.join(workspace, "accumulated_cost.tif")

# Fill sinks and depressions
arcpy.AddMessage("Start filling depressions...")
filled_dem = arcpy.sa.Fill(inputDEM)
filled_dem.save(correctedDEM)
arcpy.AddMessage("Depressions filled.")

# Calculate flow direction
arcpy.AddMessage("Start calculating flow direction...")
arcpy.env.workspace = workspace
flowDirection = arcpy.sa.FlowDirection(correctedDEM)
flowDirection.save(flow_direction)
arcpy.AddMessage("Flow direction calculated.")

# Calculate flow accumulation
arcpy.AddMessage("Start calculating flow accumulation...")
flowAccumulation = arcpy.sa.FlowAccumulation(flowDirection)
flowAccumulation.save(flow_acc)
arcpy.AddMessage("Flow accumulation calculated.")

# Calculate slope
arcpy.AddMessage("Start calculating slope...")
slope = arcpy.sa.Slope(inputDEM, "PERCENT_RISE")
#slope_without_0 = arcpy.sa.Con(slope == 0, 0.001, slope)
slope.save(slope_path)
arcpy.AddMessage("Slope calculated.")

# Translate user FIA to input number for the  "Con" tool when extracting streams
cell_size = arcpy.GetRasterProperties_management(inputDEM, "CELLSIZEX").getOutput(0)
fia_m2 = float(fia) * 10000
t = fia_m2 / (float(cell_size) ** 2)

# Extract streams
arcpy.AddMessage("Start extracting streams based on FIA...")
stream_network = arcpy.sa.Con(flow_acc, 1, "", f"VALUE > {t}")
stream_network.save(stream_network_path)
arcpy.AddMessage("Streams extracted.")

# Calculate DTW by executing the 'Accumulated Cost' tool from SAGA GIS
arcpy.AddMessage("Start calculating Depth-to-Water...")

# Define command where SAGA CMD runs in the background
saga_command = [
    saga_cmd_path,
    "grid_analysis",                        # library
    "Accumulated Cost",                     # tool
    "-DEST_TYPE", "1",                      # type "GRID"
    "-DEST_GRID", stream_network_path,      # sources
    "-COST", slope_path,                    # cost surface
    "-ACCUMULATED", accumulated_cost_path   # output
]

# Execute command
subprocess.run(saga_command, creationflags=subprocess.CREATE_NO_WINDOW)

# Scale the accumulated cost raster to meters to represent DTW
DepthToWater = arcpy.sa.Raster(accumulated_cost_path) * (float(cell_size) / 100.0)
DepthToWater.save(output_layer)

# Aggregate DTW in hexagons if provided by the user
if hexagons:

    # Create variables for the output path and basename and change output name of aggregated raster
    output_dir = os.path.dirname(output_layer)
    output_filename = os.path.basename(output_layer)

    # Change layer name depending on if it is saved in a FGDB or in another directory
    if output_layer.endswith('.tif'):
        aggregated_dtw_path = os.path.join(output_dir, "agg_" + output_filename)  # Für .tif-Dateien
    else:
        aggregated_dtw_path = os.path.join(output_dir, "agg_" + os.path.splitext(output_filename)[0])

    # Get the name of the first field (it will probably mostly be the FID)
    fields = arcpy.ListFields(hexagons)
    first_field = fields[0].name

    # Execute zonal statistics using the first field for the "zone_field" argument
    aggregated_dtw = arcpy.sa.ZonalStatistics(in_zone_data=hexagons, zone_field=first_field,
                                              in_value_raster=DepthToWater, statistics_type="MEAN")

    # Save aggregated raster and add it to the project
    aggregated_dtw.save(aggregated_dtw_path)

    aprx = arcpy.mp.ArcGISProject("CURRENT")
    map_obj = aprx.activeMap
    map_obj.addDataFromPath(aggregated_dtw_path)

    arcpy.AddMessage("Depth-to-Water successfully calculated and aggregated.")
    arcpy.AddMessage(f"Intermediate results are saved under {workspace}.")

else:
    arcpy.AddMessage("Depth-to-Water successfully calculated.")
    arcpy.AddMessage(f"Intermediate results are saved under {workspace}.")
