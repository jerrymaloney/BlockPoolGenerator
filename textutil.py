#!/usr/bin/python3.8
# thanks to http://two.pairlist.net/pipermail/reportlab-users/2009-April/008171.html via https://stackoverflow.com/questions/13061545/rotated-document-with-reportlab-vertical-text/40349017
from reportlab.platypus.flowables import Flowable
from reportlab.platypus import Paragraph

class verticalText(Flowable):
  '''Rotates a text in a table cell.'''

  def __init__(self, text):
    Flowable.__init__(self)
    self.text = text

  def draw(self):
    canvas = self.canv
    canvas.rotate(90)
    fs = canvas._fontsize
    canvas.translate(1, -fs/1.2)  # canvas._leading?
    canvas.drawString(0, 0, self.text)

  def wrap(self, aW, aH):
    canv = self.canv
    fn, fs = canv._fontname, canv._fontsize
    return canv._leading, 1 + canv.stringWidth(self.text, fn, fs)

class fitToSpace(Paragraph):
  # thanks to https://stackoverflow.com/questions/14719194/resize-reportlab-platypus-paragraph-flowable
  ''' stuff '''
  def __init__(self, p, aW, aH):
    Paragraph.__init__(self)
  
  def fitToSpace(self, p, aW, aH):
      """
      Determines if inputted text fits in the space given for a paragraph
      and if it doesn't, reduces the font-size until it does.
  
      """
      w,h = p.wrap(COLWIDTH, ROWHEIGHT) # find required space
      if w<=aW and h<=aH:
          # return font size to apply it to the para again
          print("final font_size: %d" % p.style.fontSize)
          return p # now render the paragraph in the doctemplate
      else: 
          p.style.fontSize -= 1
          w,h = p.wrap(aW, aH)
          fitToSpace(w,h,aW,aH,p)
