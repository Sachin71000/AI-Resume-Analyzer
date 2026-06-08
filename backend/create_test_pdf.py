from fpdf import FPDF

pdf = FPDF()
pdf.add_page()
pdf.set_font("Helvetica", size=12)
pdf.cell(200, 10, txt="John Doe", ln=1)
pdf.cell(200, 10, txt="React Developer", ln=1)
pdf.cell(200, 10, txt="Skills: React, Node.js, Python, Flask, TypeScript, Docker", ln=1)
pdf.cell(200, 10, txt="I possess several years of experience building scalable web applications.", ln=1)
pdf.output("C:\\Users\\sachi\\AAT\\test_resume.pdf")
print("PDF created.")
