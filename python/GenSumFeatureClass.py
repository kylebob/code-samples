# ---------------------------------------------------------------------------
# Name: GenSumFeatureClass.py
# Description:  This script takes the project and region data for the WEDC, then identifies, summarizes, and joins the data.
# Author: Kyle Mullens
# ---------------------------------------------------------------------------

# Note: Exports folder must be writable for this process to work.

# Import arcpy module
import arcpy
if __debug__:
    print "arcpy imported."
    
# Constant strings.
coreUrl = "C:\\Users\\Kyle\\Google Drive\\kylebob.com\\python\\aggregate\\"
sampleData = coreUrl + "DATCP\\DATCP.shp"
tempExport = coreUrl + "exports\\DATCP_Identity.shp"

# Function to create summary tables.
def createSummary(uniqueFID, addedData, summaryExport):
    
    # Set constant variables to global to be accessed within the function.
    global coreUrl
    global sampleData
    global tempExport

    # Redefine unique variable URLs.
    addedData     = coreUrl + addedData
    summaryExport = coreUrl + summaryExport
            
    # Delete old fields from added data.
    try:
        with open(addedData) as file:
            if __debug__:
                print "Deleting rows..."
            dropFields = ["COUNT_Uniq", "SUM_Planne", "SUM_Actual", "SUM_AwardA"]
            arcpy.DeleteField_management(addedData, dropFields)
            if __debug__:
                print "Rows deleted."
    except IOError:
        if __debug__:
            print "File not found."

    # Delete old field from project data.
    try:
        with open(sampleData) as file:
            if __debug__:
                print "Deleting rows..."
            dropFields = [uniqueFID]
            arcpy.DeleteField_management(sampleData, dropFields)
            if __debug__:
                print "Rows deleted."
    except IOError:
        if __debug__:
            print "File not found."

    # Process: Identity -- creates new sample data table with region ID numbers added to each sample data row.
    arcpy.Identity_analysis(sampleData, addedData, tempExport, "ONLY_FID", "", "NO_RELATIONSHIPS")
    if __debug__:
        print "Identity analysis complete."

    # Process: Summary Statistics -- creates new region data table with project and award amount totals in each row, sorted by district ID.
    arcpy.Statistics_analysis(tempExport, summaryExport, [["UniqueID", "COUNT"], ["PlanJobRet", "SUM"], ["AwardAmoun", "SUM"], ["PlanCap", "SUM"]], uniqueFID)
    if __debug__:
        print "Summary statistics complete."

    # Process: Join Field -- combines original region data (senator names, etc.) with new data (project totals, etc.) for use in presented map.
    arcpy.JoinField_management(addedData, "FID", summaryExport, uniqueFID, "COUNT_Uniq;SUM_PlanJo;SUM_AwardA;SUM_PlanCa")
    if __debug__:
        print "Region join complete."

    # Process: Join Field -- combines original project data (project name, investment amount, etc.) with region id numbers.
    arcpy.JoinField_management(sampleData, "FID", tempExport, "objectid", uniqueFID)
    if __debug__:
        print "Project join complete."

    # Delete temporary files.
    try:
        if __debug__:
            print "Deleting files..."
        arcpy.Delete_management(tempExport)
    except IOError:
        if __debug__:
            print "No files found to delete."

    # Delete old summary files.
    try:
        if __debug__:
            print "Deleting files..."
        arcpy.Delete_management(summaryExport)
    except IOError:
        if __debug__:
            print "No files found to delete."

# Run summary function for each region.
createSummary("FID_Senate", "Senate\\Senate.shp", "exports\\summary_Senate.dbf")
createSummary("FID_Assemb", "Assembly\\Assembly.shp", "exports\\summary_Assembly.dbf")
createSummary("FID_County", "County\\County.shp", "exports\\summary_County.dbf")
createSummary("FID_EDO", "EDO\\EDO.shp", "exports\\summary_EDO.dbf")
createSummary("FID_WEDC", "WEDC\\WEDC.shp", "exports\\summary_WEDC.dbf")
