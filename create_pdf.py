
import glob
from fpdf import FPDF

images = glob.glob("../data/C*/output/*.png")
images_sort = sorted(images)
pdf = FPDF()
for image in images_sort:
    pdf.add_page()
    pdf.image(image, 10, 10, 200)
pdf.output("../yourfile.pdf")

