# An ArcGIS Toolbox for Depth-to-Water Index Calculation
This tool is the first openly-accessible tool that calculates the (cartographic) Depth-to-Water (DTW) index, representing the simulated vertical difference (meters) between a landscape cell and the nearest surface water cell along the accumulative least-cost slope path. DTW is commonly used for soil wetness modelling and identifying areas of high or low probability of water accumulation, which can be useful for hydrologic modelling, environmental planning and landscape monitoring. 

It is not necessary to download the *DepthToWater.py* script, as it is automatically implemented in the .atbx toolbox.

Consult the User Manual for more detailed information.


## Usage
This toolbox has a GNU GPL license and is open for public use and distribution. Users are encouraged to use, share and further enhance the tool according to their needs. However, when sharing, modifying or citing the tool, please give an appropriate credit to the original creator according to the following:

*Greupner, N. (2024): DepthToWater. An ArcGIS Pro toolbox for Depth-to-Water index calculation. University of Salzburg. Available at: https://zenodo.org/doi/10.5281/zenodo.13381566*.  

## Prerequisites 
- ArcGIS Pro: The tool is designed to be used within ArcGIS Pro. The Spatial Analyst extension is required for executing the tool. As it was implemented in ArcGIS Pro 3.3.0, there might be compatibility issues in other versions of the software.

- SAGA GIS Installation: Ensure that SAGA GIS is installed on your system as the tool relies on it for calculations of accumulated cost which are not available within the ArcGIS geoprocessing tool environment. SAGA GIS can be downloaded under https://sourceforge.net/projects/saga-gis/.





