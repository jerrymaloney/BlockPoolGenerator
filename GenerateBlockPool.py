#!/usr/bin/python3.8
import random, sys, csv, getopt
from tabulate import tabulate
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.enums import TA_CENTER
from textutil import verticalText, fitToSpace


# constants
TOPTEAMTEXT=""
TOPTEAMTEXTCOLOR=colors.blue
TOPTEAMBGCOLOR=colors.yellow
SIDETEAMTEXT=""
SIDETEAMTEXTCOLOR=colors.white
SIDETEAMBGCOLOR=colors.green
BLOCKTEXTCOLOR=colors.black
BLOCKBGCOLOR=colors.white
LABELTEXTSIZE=30
BLOCKTEXTSIZE=12
COLWIDTH=60
ROWHEIGHT=38

# styler
POOLTABLESTYLE=[
  ('BACKGROUND',(0,0),(-1,-1),BLOCKBGCOLOR),
  ('TEXTCOLOR', (0,0),(-1,-1),BLOCKTEXTCOLOR),
  ('SIZE',      (0,0),(-1,-1),BLOCKTEXTSIZE),
  ('GRID',      (0,0),(-1,-1),0.5,colors.black),
  ('ALIGN',     (0,0),(-1,-1),'CENTER'),
  ('VALIGN',    (0,0),(-1,-1),'MIDDLE'),
  
  ('BACKGROUND',(0,0),(-1, 0),TOPTEAMBGCOLOR),
  ('TEXTCOLOR', (0,0),(-1, 0),TOPTEAMTEXTCOLOR),
  ('SIZE',      (0,0),(-1, 0),LABELTEXTSIZE),
  ('VALIGN',    (0,0),(-1, 0),'TOP'),
  ('BACKGROUND',(1,1),(-1, 1),TOPTEAMBGCOLOR),
  ('TEXTCOLOR', (1,1),(-1, 1),TOPTEAMTEXTCOLOR),
  ('SIZE',      (1,1),(-1, 1),LABELTEXTSIZE),
  ('VALIGN',    (1,1),(-1, 1),'TOP'),
  ('SPAN',      (2,0),(-1, 0)),
  
  ('BACKGROUND',(0,2),( 1,-1),SIDETEAMBGCOLOR),
  ('TEXTCOLOR', (0,2),( 1,-1),SIDETEAMTEXTCOLOR),
  ('SIZE',      (0,2),( 1,-1),LABELTEXTSIZE),
  ('ALIGN',     (0,2),( 1,-1),'LEFT'),
  ('VALIGN',    (0,2),( 1,-1),'MIDDLE'),
  ('VALIGN',    (1,2),( 1,-1),'TOP'),
  ('SPAN',      (0,2),( 0,-1)),
  
  ('BACKGROUND',(0,0),( 1, 1),colors.lightgrey),
  ('SPAN',      (0,0),( 1, 1))
]


# read CLI argument
ERROR_MISSINGPARAMS='-I infile and -O outfile arguments are required'
inFile=''
outFile=''
try:
  opts, args=getopt.getopt(sys.argv[1:], 'i:o:')
except:
  print('ERROR: %s' % ERROR_MISSINGPARAMS)
  exit(-1)

for opt, arg in opts:
  if opt=='-i':
    inFile=arg
  elif opt=='-o':
    outFile=arg
    if outFile[-4:] != '.pdf':
      outFile=outFile+'.pdf'
if inFile=='' or outFile=='':
  print('ERROR: %s' % ERROR_MISSINGPARAMS)
  exit(-1)

# load csv file into a list
# format of input file must be:
# 'Name','Chosen Block (optional)','Email'
wrapStyle=getSampleStyleSheet()["BodyText"]
wrapStyle.alignment = TA_CENTER
names=[]
blockChoices=[]
emails=[]
with open(inFile) as csvFile:
  csvReader=csv.reader(csvFile, delimiter=',', quotechar="'")
  for row in csvReader:
    names.append(Paragraph(row[0], wrapStyle))
    blockChoices.append(row[1])
    emails.append(row[2])

# create blocks
blocks=[[0 for x in range(10)] for y in range(10)]

# assign names to chosen blocks
for (nameindex, blocknum) in enumerate(blockChoices):
  if blocknum != '':
    chosenBlockIndex=int(blocknum)-1  # minus 1 because humans start counting at 1, not 0
    chosenBlockRowIndex=int(chosenBlockIndex/10)
    chosenBlockColIndex=int(chosenBlockIndex%10)
    blocks[chosenBlockRowIndex][chosenBlockColIndex]=names[nameindex]
# remove assigned names from the list of entrants in reverse in a separate iteration to avoid messing up the indices
for (nameindex, blocknum) in reversed(list(enumerate(blockChoices))):
  if blocknum != '':
    del names[nameindex]

# randomly assign remaining names to blocks
for i in range(10):
  for j in range(10):
    if blocks[i][j] == 0:
      nameIndex=random.randint(0,len(names)-1)
      blocks[i][j] = names[nameIndex]
      del names[nameIndex]

# randomly assign digits 0-9 to columns
numberPool=[0,1,2,3,4,5,6,7,8,9]
columnNumberLabels=[0 for x in range(10)]
for i in range(10):
  colIndex=random.randint(0,len(numberPool)-1)
  columnNumberLabels[i] = numberPool[colIndex]
  del numberPool[colIndex]

# randomly assign digits 0-9 to rows
numberPool=[0,1,2,3,4,5,6,7,8,9]
rowNumberLabels=[0 for x in range(10)]
for i in range(10):
  rowIndex=random.randint(0,len(numberPool)-1)
  rowNumberLabels[i] = numberPool[rowIndex]
  del numberPool[rowIndex]

# check generated blocks against original list of entrants
blocksAsDict={}
rowIndex=0
for row in blocks:
  colIndex=0
  for block in row:
    humanOrdinal = rowIndex*10 + colIndex + 1
    blocksAsDict[humanOrdinal]=block.text
    colIndex += 1
  rowIndex += 1
with open(inFile) as csvFile:
  csvReader=csv.reader(csvFile, delimiter=',', quotechar="'")
  for row in csvReader:
    if row[1] != '':
      desiredBlock=row[1]
      entrantName=row[0]
      if entrantName != blocksAsDict[int(desiredBlock)]:
        sys.exit('ERROR: mismatch\nThe pool has ' + blocksAsDict[int(desiredBlock)] + ' at block ' + desiredBlock + ', but it should be ' + entrantName + '.')


if False:
# output pool to text
  print(tabulate(blocks, headers=columnNumberLabels, showindex=rowNumberLabels))
  print(blocks)

# output pool to pdf
tableWithNumbers=[['','',TOPTEAMTEXT]]  # each list in this list of lists is a row of the output table
colNumbersRow=["",""]
sideTeamNameAddedToOutput=False
for item in columnNumberLabels:
  colNumbersRow.append(item)
tableWithNumbers.append(colNumbersRow)
for row in range(len(blocks)):
  newRow=['']
  if not sideTeamNameAddedToOutput:
    newRow=[verticalText(SIDETEAMTEXT)]
    sideTeamNameAddedToOutput=True
  newRow.append(rowNumberLabels[row])
  for block in blocks[row]:
    newRow.append(block)
  tableWithNumbers.append(newRow)

doc = SimpleDocTemplate(outFile, pagesize=landscape(letter))
outputTable = [] # container for the 'Flowable' objects
blockTable=Table(tableWithNumbers,
  colWidths=[COLWIDTH/1.5,COLWIDTH/2,COLWIDTH,COLWIDTH,COLWIDTH,COLWIDTH,COLWIDTH,COLWIDTH,COLWIDTH,COLWIDTH,COLWIDTH,COLWIDTH],
  rowHeights=[ROWHEIGHT,ROWHEIGHT,ROWHEIGHT,ROWHEIGHT,ROWHEIGHT,ROWHEIGHT,ROWHEIGHT,ROWHEIGHT,ROWHEIGHT,ROWHEIGHT,ROWHEIGHT,ROWHEIGHT]
)

blockTable.setStyle(TableStyle(POOLTABLESTYLE))
outputTable.append(blockTable)

doc.build(outputTable)  # write the document to disk
