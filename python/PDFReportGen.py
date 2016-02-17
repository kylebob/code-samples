# -*- coding: utf-8 -*-

# ---------------------------------------------------------------------------
# Name:         PDFReportGen.py
# Description:  This script generates a PDF report with text, tables, and graphs based on a specific database query.
#               One of four templates will be used, depending on if the data is for an Excel project or region/state file, or a PDF project or region/state report.
# Author:       Kyle Mullens
# ---------------------------------------------------------------------------

__version__='''$Id$'''
__doc__= """WEDC PDF Report"""

# Import selected libraries.
import arcpy                                                    # ArcGIS Python library.
import os, sys, copy, unittest, operator, string                # Standard libraries.
from types import TupleType, ListType, StringType, UnicodeType  # Data types.
from os.path import join, basename, splitext                    # Path libraries from os.
from pg8000 import DBAPI                                        # pg8000 database connection libraries.
import datetime                                                 # Date and time.

# Import reportlab libraries for PDF generation.
from reportlab.lib.styles import PropertySet, getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors, utils
from reportlab.lib.units import cm
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.validators import Auto
from reportlab.lib.testutils import setOutDir, outputfile
from reportlab.lib.colors import HexColor, black
from reportlab.graphics.shapes import *
from reportlab.graphics.charts.textlabels import Label
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.legends import Legend
from reportlab.graphics.charts.linecharts import HorizontalLineChart
from reportlab.graphics.widgets.markers import makeMarker
from reportlab.graphics.shapes import Image, Drawing
from reportlab.graphics import renderPDF
from reportlab.platypus import *
from reportlab.platypus.flowables import Spacer, PageBreak
from reportlab.platypus.paragraph import Paragraph
from reportlab.platypus.xpreformatted import XPreformatted
from reportlab.platypus.frames import Frame
from reportlab.platypus.doctemplate import PageTemplate, BaseDocTemplate
from reportlab.pdfgen.canvas import Canvas

# Define global variables.
wiImage = 'C:\\Users\\Kyle\\Google Drive\\kylebob.com\\python\\wi.jpg' #'c:\\WEDC\\wi.jpg'
headerImage = 'C:\\Users\\Kyle\\Google Drive\\kylebob.com\\python\\blue-header.jpg' #'c:\\WEDC\\blue-header.jpg'
folder = arcpy.env.scratchFolder

# Define formatting for text elements.
styleSheet = getSampleStyleSheet()
bodyText = styleSheet['BodyText']
cellStyle = styleSheet['Normal']
chartText = styleSheet['Heading2']


# Connect to database.
def connectDB():
    global db
    arcpy.AddMessage("Connecting to database...")
    db = DBAPI.connect(
        host="shepard.uww.edu",
        user="sde",
        password="Culvers2day?",
        database="wedc")
    arcpy.AddMessage("Connection opened.")

# Runs selected query and returns the results in a 2D array.
def runDatabaseQuery(selectQuery, fetchAll):
    arcpy.AddMessage("Query: " + selectQuery)
    cursor = db.cursor()
    db.commit()
    cursor.execute(selectQuery)
    arcpy.AddMessage("Executed.")
    if (fetchAll is True):
        data = cursor.fetchall()
    else:
        data = cursor.fetchone()
    cursor.close()
    return data

# Close database connection.
def closeDB():
    db.close()
    arcpy.AddMessage("Connection closed.")
    
    
# Creates a report for a selected project.
def projectReport(ID):

    # Run project list query.
    query = "SELECT convert_to(Recipient, 'UTF8'), convert_to(Agency, 'UTF8'), AwardAmoun, convert_to(awardtype1, 'UTF8'), AwardDate, convert_to(industryty, 'UTF8'), PlannedJob, convert_to(ProjectSum, 'UTF8') FROM Project WHERE OBJECTID = " + ID + " LIMIT 1"
    projects = runDatabaseQuery(query, False)

    # If data exists.
    if projects:

        # Define and create single array of data fields for report.
        data = []
        for d in projects:
            data.append(d)
            
        # Define document name and properties.
        n = "WEDC_Report_for_" + stripPunctuation(unicode(data[0])) + ".pdf"
        outFile = n#os.path.join(folder,n)
        doc = SimpleDocTemplate(outFile, rightMargin=24,leftMargin=24,topMargin=24,bottomMargin=24)

        # Define formatted labels and data of strings in paragraph form.
        labels  = ["Agency", "Award Amount", "Award Type", "Award Date", "Industry", "Planned Jobs"]
        tableLabels = []
        tableData = []
        for l in labels:
            arcpy.AddMessage(l)
            tableLabels.append(Paragraph("<b>" + unicode(l) + ":</b>", cellStyle))
        for d in data:
            tableData.append(Paragraph(unicode(d), cellStyle))
                
        # Add data to table based on arguments. ##### Move this to one function.
        projectTable = []
        for x in xrange(len(tableLabels)):
            projectTable.append([tableLabels[x], tableData[x+1]])

        # Create table with formatting.
        gridStyle = TableStyle([
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('LEFTPADDING', (0,0), (-1,-1), 0),
            ('RIGHTPADDING', (0,0), (-1,-1), 0)
            ])
        dataTable = Table(projectTable, colWidths=(100, 266), rowHeights=None, style=gridStyle)

        # Output award recipient and location.
        header = []
        header.append(Paragraph(unicode(removeNonAscii(data[0])).upper(), styleSheet['Heading1']))
        #header.append(Paragraph(unicode(data[1]).upper(), styleSheet['Heading2']))
        header.append(dataTable)

        # Put data on left, WI image on right.
        fullTable = [[header, getImage(wiImage, width=170)]]
        table = Table(fullTable, colWidths=(366, 170), rowHeights=None, style=gridStyle)

        output = []                                                             # Initialize output.
        output.append(getImage(headerImage, width=584))                         # Add header image on top of page.
        output.append(Spacer(0,1*cm))                                           # Add space before table data.
        output.append(table)                                                    # Add previously defined table of selected data.
        output.append(Spacer(0,1*cm))                                           # Add space after table data.
        output.append(Paragraph(unicode(removeNonAscii(data[7])), bodyText))    # Display description.
        doc.build(output)                                                       # Export PDF file.
        return n

    else:

        # Send user to page to inform them that there are no records to show.
        return noResultsFound()


    
# Creates a report for a selected region or the entire state.
def regionReport(summary, ID, agency, year, industry, awardType):

    # Select name column, foreign ID, and table based on report name.
    if (summary == "Counties"):
        name     = "CTY_NAME"
        fid      = "FID_Counti"
        table    = "actualjobspercounty"
        preTitle = "County of "
    elif (summary == "Senate"):
        name     = "SEN_NUM"
        fid      = "FID_Senate"
        table    = "actualjobspersenate"
        preTitle = "Senate District "
    elif (summary == "Assembly"):
        name     = "DISTRICT_S"
        fid      = "FID_Assemb"
        table    = "actualjobsperassembly"
        preTitle = "Assembly District "
    elif (summary == "EDO"):
        name     = "EDO_REGION"
        fid      = "FID_EDO"
        table    = "actualjobsperedo"
        preTitle = "EDO Region "

    # If "all" for any criteria are selected, tell the database to select all rows where data exists, otherwise leave data blank.
    agencyColumn = getColumns(agency, "agency")
    yearColumn = getColumns(year, "year")
    industryColumn = getColumns(awardType, "industryty")
    awardTypeColumn = getColumns(awardType, "awardtype1")

    sumsQuery = "COUNT(Recipient) AS TotalReci, SUM(AwardAmoun) AS TotalAward, SUM(PlannedCap) AS TotalCap, SUM(PlannedJob) AS TotalJob FROM Project"

    if (summary == "state"):
        preTitle = "State of "
        title = ["Wisconsin"]
        whereQuery = " WHERE OBJECTID >= 0 %s %s %s" % (yearColumn, industryColumn, awardTypeColumn)
    else:
        # Define report creation arguments.
        whereQuery = " WHERE %s = (%s - 1) %s %s %s" % (fid, ID, yearColumn, industryColumn, awardTypeColumn)
        titleQuery = "SELECT convert_to(%s, 'UTF8') FROM %s WHERE OBJECTID = '%s' LIMIT 1" % (name, table, ID)
        title = runDatabaseQuery(titleQuery, False)     # Run region name database query.

    totalsQuery = "SELECT %s %s" % (sumsQuery, whereQuery)
    totals = runDatabaseQuery(totalsQuery, False)       # Run totals for each column.

    projectsQuery = "SELECT convert_to(Recipient, 'UTF8') FROM Project %s" % (whereQuery)
    projects = runDatabaseQuery(projectsQuery, True)    # Run project list query.

    if (industry == "all"):
        industryQuery = "SELECT convert_to(industryty, 'UTF8'), %s %s GROUP BY industryty ORDER BY industryty" % (sumsQuery, whereQuery)
        industryData = runDatabaseQuery(industryQuery, True)    

    if (awardType == "all"):
        awardTypeQuery = "SELECT convert_to(awardtype1, 'UTF8'), %s %s GROUP BY awardtype1 ORDER BY awardtype1" % (sumsQuery, whereQuery)
        awardTypeData = runDatabaseQuery(awardTypeQuery, True)

    # If data exists.
    if title and projects:

        # Define and create single array of data fields for report.
        data = []
        recipients = ""

        data.append(agency)
        data.append(year)
        data.append(industry)
        data.append(awardType)
        
        for d in totals:
            data.append(d)  
        data.append("")
        print data

        # Define document name and properties.
        n = "WEDC_Report_for_" + stripPunctuation(unicode(title[0])) + ".pdf"
        outFile = n#os.path.join(folder,n)
        doc = SimpleDocTemplate(outFile, rightMargin=24,leftMargin=24,topMargin=24,bottomMargin=24)

        # Define formatted labels and data of strings in paragraph form.
        labels  = ["Agency", "Fiscal Year", "Industry", "Award Type", "Number of Awards", "Award Amount", "Project Cost", "Projected Jobs", "Awards by Name"]
        tableLabels = []
        tableData = []
        for l in labels:
            tableLabels.append(Paragraph("<b>" + l + ":</b>", cellStyle))
        for d in data:
            tableData.append(Paragraph(unicode(d), cellStyle))
                
        # Add data to table based on arguments.
        projectTable = []
        for x in xrange(len(tableLabels)):
            projectTable.append([tableLabels[x], tableData[x]])

        # Create table with formatting.
        gridStyle = TableStyle([
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('LEFTPADDING', (0,0), (-1,-1), 0),
            ('RIGHTPADDING', (0,0), (-1,-1), 0)
            ])
        dataTable = Table(projectTable, colWidths=(100, 266), rowHeights=None, style=gridStyle)

        # Output award recipient and location.
        header = []
        header.append(Paragraph(unicode(preTitle + title[0]).upper(), styleSheet['Heading1']))
        header.append(Spacer(0,1*cm))
        header.append(dataTable)

        # Put data on left, WI image on right.
        fullTable = [[header, getImage(wiImage, width=170)]]
        table = Table(fullTable, colWidths=(366, 170), rowHeights=None, style=gridStyle)

        # Create list of recipients.
        for r in projects:
            arcpy.AddMessage(r[0])
            recipients += unicode(removeNonAscii(r[0])) + ", "
        
        
        output = []                                                 # Initialize output.
        output.append(getImage(headerImage, width=584))             # Add header image on top of page.
        output.append(Spacer(0,1*cm))                               # Add space before table data.
        output.append(table)                                        # Add previously defined table of selected data.
        output.append(Paragraph(unicode(recipients), cellStyle))    # Add list of recipients.


        # Create graphs for some data without filters.
        graphTypes = ["Number of Awards", "Award Amount", "Project Cost", "Projected Jobs"]

        # If "all" in a category is selected, display graphs for comparison between categories.
        sortTypes = []
        if (industry == "all"):
            sortTypes.append(" by Industry")
        if (awardType == "all"):
            sortTypes.append(" by Award Type")

        # Dynamically create graphs based on criteria.
        for s in range(len(sortTypes)):
            for g in range(len(graphTypes)):

                # Create a line graph for years, and a pie chart for industries and award types.
                output.append(Spacer(0,1*cm))
                output.append(Paragraph(unicode(graphTypes[g]) + unicode(sortTypes[s]), chartText))
                
                if (sortTypes[s] == " by Industry"):

                    graph = createPie(unicode(graphTypes[g]), industryData, g)
                    output.append(graph)
                    
                elif (sortTypes[s] == " by Award Type"):
                    graph = createPie(unicode(graphTypes[g]), awardTypeData, g)
                    output.append(graph)
                    

        doc.build(output)   # Export PDF file.
        return n

    else:
        
        # Send user to page to inform them that there are no records to show.
        return noResultsFound()

# Gets specific columns in database based on filters.
def getColumns(f, c):
    if (f == "all"):
        return ""
    else:
        return " AND %s = '%s'" % (c, f)
        
# Remove non-ASCII characters to prevent errors. -- Will find a way to encode these correctly in the future.
def removeNonAscii(s):
    newText = ""
    for i in s:
        if (ord(i)<128):
            newText += i
    return newText

# Strips punctuation from report title to prevent errors in file name.
def stripPunctuation(oldString):
    newString = ""
    for c in oldString:
        if c in "!,.?'":
            c = ""
        elif c in " ":
            c = "_"
        newString += c
    return newString    
    
# Imports image and adjusts size.
def getImage(path, width=1*cm):
    image = utils.ImageReader(path)
    w, h = image.getSize()
    aspect = h / float(w)
    return Image(path, width=width, height=(width * aspect))

# Creates pie chart for data (regions only).    
def createPie(t, d, g):

    # Define graph data and labels.
    numbers = []
    categories = []
    for i in range(len(d)):
        if (d[i][g + 1] != 0):
            numbers.append(int(d[i][g + 1]))
            categories.append(str(d[i][0]))

    if (len(numbers) == 0):
        styleSheet = getSampleStyleSheet()
        return Paragraph(unicode("No data available."), styleSheet['BodyText'])
      
    # Define graph settings.
    bc = Pie() 
    bc.x = 0
    bc.y = 0
    bc.height = 120
    bc.width = 120
    bc.data = numbers
    bc.strokeWidth          = 0
    bc.labels               = categories
    bc.sideLabels           = 0
    bc.checkLabelOverlap    = 1
    bc.simpleLabels         = 1
    bc.slices.strokeWidth   = 1
    bc.slices.label_visible = 0 
    bc.slices.fontColor     = None

    # Define legend settings.
    legend = Legend()
    legend.x                = bc.width+30
    legend.y                = bc.height / 2
    legend.dx               = 10
    legend.dy               = 10
    legend.deltax           = 0 
    legend.boxAnchor        = 'w'  
    legend.columnMaximum    = 8  
    legend.strokeWidth      = 1  
    legend.strokeColor      = black  
    legend.deltax           = 75  
    legend.deltay           = 10  
    legend.autoXPadding     = 5  
    legend.yGap             = 5  
    legend.dxTextSpace      = 5  
    legend.alignment        = 'right'    
    legend.subCols.rpad     = 30
    legend.colorNamePairs   = Auto(chart=bc)

    if (t == "Number of Awards"):
        pieColors = [  
            HexColor("#554330FF", False, True),  
            HexColor("#82551FFF", False, True),  
            HexColor("#D98527FF", False, True),
            HexColor("#FAC57EFF", False, True),
            HexColor("#55433099", False, True),  
            HexColor("#82551F99", False, True),  
            HexColor("#D9852799", False, True),
            HexColor("#FAC57E99", False, True),
        ]

    elif (t == "Award Amount"):
        pieColors = [  
            HexColor("#381250FF", False, True),  
            HexColor("#62589CFF", False, True),  
            HexColor("#5D86BDFF", False, True),  
            HexColor("#A4CAEBFF", False, True),
            HexColor("#38125099", False, True),  
            HexColor("#62589C99", False, True),  
            HexColor("#5D86BD99", False, True),  
            HexColor("#A4CAEB99", False, True),
        ]

    elif (t == "Project Cost"):
        pieColors = [     
            HexColor("#554330FF", False, True),  
            HexColor("#82551FFF", False, True),  
            HexColor("#D98527FF", False, True),
            HexColor("#FAC57EFF", False, True),
            HexColor("#55433099", False, True),  
            HexColor("#82551F99", False, True),  
            HexColor("#D9852799", False, True),
            HexColor("#FAC57E99", False, True),
        ]
        
    elif (t == "Projected Jobs"):
        pieColors = [  
            HexColor("#256884FF", False, True),  
            HexColor("#13AB88FF", False, True),  
            HexColor("#9DD29EFF", False, True),  
            HexColor("#FFF8ADFF", False, True),
            HexColor("#25688499", False, True),  
            HexColor("#13AB8899", False, True),  
            HexColor("#9DD29E99", False, True),  
            HexColor("#FFF8AD99", False, True),
        ]
        

    # Select template colors for pie slices.
    dataSlices = len(bc.data)
    m = len(pieColors)  
    i = m // dataSlices  
    for j in xrange(dataSlices):
        setattr(bc.slices[j],'fillColor',pieColors[j*i % m])
    legend.colorNamePairs = [(bc.slices[i].fillColor, (bc.labels[i][0:20], '%0.2f' % bc.data[i])) for i in xrange(dataSlices)]

    
    # Add defined values to graph.
    drawing = Drawing(560, 120)
    drawing.add(bc)
    drawing.add(legend)

    # Return graph to be used as output.
    return drawing


# If the queries yield no results, display a simple text file to inform the user.
def noResultsFound():
    n = "noresults.txt"
    outFile = os.path.join(folder,n)
    noResults = open(outFile, 'w')
    print outFile
    noResults.write("No results found.")
    noResults.close()
    return n

    
# Grab arguments from arcpy.
getExport = "pdf"#arcpy.GetParameterAsText(0)
getSummary = "project"#arcpy.GetParameterAsText(1)
getID = "44"#arcpy.GetParameterAsText(2)
getYear = "all"#arcpy.GetParameterAsText(3)
getIndustry = "all"#arcpy.GetParameterAsText(4)
getAwardType = "all"#arcpy.GetParameterAsText(5)
getAgency = "all"

connectDB()	# Connect to database.

# Create different report for projects and regions.
setOutDir(__name__)
if (getSummary == "project"):
    outputFile = projectReport(getID)
else:
    outputFile = regionReport(getSummary, getID, getYear, getIndustry, getAwardType, getAgency)
        
closeDB()	# Close database connection.

# Return file name.
arcpy.SetParameterAsText(6,outputFile)
arcpy.AddMessage("Output File: " + outputFile)
arcpy.AddMessage("PDFReportGen.py finished.")

