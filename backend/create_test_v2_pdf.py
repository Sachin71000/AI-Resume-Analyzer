from fpdf import FPDF

pdf = FPDF()
pdf.add_page()
pdf.set_font("Helvetica", size=12)
pdf.cell(200, 10, txt="John Doe", ln=1)
pdf.cell(200, 10, txt="Senior React Developer", ln=1)
pdf.cell(200, 10, txt="Skills: React, Node.js, Python, Flask, TypeScript, Docker, Kubernetes, AWS", ln=1)
pdf.cell(200, 10, txt="I possess several years of experience building scalable web applications.", ln=1)
pdf.cell(200, 10, txt="Led the migration to microservices on AWS.", ln=1)
pdf.output("C:\\Users\\sachi\\AAT\\test_resume_v2.pdf")
print("PDF v2 created.")
