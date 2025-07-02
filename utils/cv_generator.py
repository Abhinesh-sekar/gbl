# utils/cv_generator.py
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
import os
from datetime import datetime

def generate_cv_pdf(user_data):
    """Generate a professional CV PDF from user data"""
    
    # Create temp directory if it doesn't exist
    temp_dir = "temp"
    os.makedirs(temp_dir, exist_ok=True)
    
    # Generate filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"cv_temp_{timestamp}.pdf"
    filepath = os.path.join(temp_dir, filename)
    
    # Create PDF document
    doc = SimpleDocTemplate(
        filepath,
        pagesize=A4,
        rightMargin=0.75*inch,
        leftMargin=0.75*inch,
        topMargin=0.75*inch,
        bottomMargin=0.75*inch
    )
    
    # Define styles
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=20,
        spaceAfter=30,
        alignment=TA_CENTER,
        textColor=colors.darkblue
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=10,
        spaceBefore=20,
        textColor=colors.darkblue,
        borderWidth=1,
        borderColor=colors.darkblue,
        borderPadding=5,
        backColor=colors.lightgrey
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=8,
        alignment=TA_JUSTIFY
    )
    
    # Build story (content)
    story = []
    
    # Header with name
    story.append(Paragraph(user_data['name'].upper(), title_style))
    story.append(Spacer(1, 12))
    
    # Personal Information Section
    story.append(Paragraph("PERSONAL INFORMATION", heading_style))
    
    personal_info = [
        ["Date of Birth:", user_data['dob'].strftime("%d/%m/%Y")],
        ["Phone Number:", user_data['phone']],
        ["Father's Name:", user_data['father_name']],
    ]
    
    if user_data['is_married'] == "Married":
        personal_info.append(["Marital Status:", "Married"])
        personal_info.append(["Husband's Name:", user_data['husband_name']])
    else:
        personal_info.append(["Marital Status:", "Single"])
    
    personal_table = Table(personal_info, colWidths=[2*inch, 4*inch])
    personal_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.lightgrey]),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(personal_table)
    story.append(Spacer(1, 20))
    
    # Education Section
    story.append(Paragraph("EDUCATIONAL QUALIFICATIONS", heading_style))
    
    education_data = [["Qualification", "Institution/Board", "Year", "Specialization"]]
    
    # Order education from highest to lowest
    education_order = ["PG (Master's)", "UG (Bachelor's)", "Diploma", "12th", "10th"]
    
    for level in education_order:
        if level in user_data['education']:
            edu = user_data['education'][level]
            education_data.append([
                level,
                edu['institution'],
                str(edu['year']),
                edu.get('specialization', 'N/A')
            ])
    
    education_table = Table(education_data, colWidths=[1.5*inch, 2.5*inch, 1*inch, 2*inch])
    education_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(education_table)
    story.append(Spacer(1, 20))
    
    # Work Experience Section
    if user_data['work_experience']:
        story.append(Paragraph("WORK EXPERIENCE", heading_style))
        
        for i, exp in enumerate(user_data['work_experience']):
            # Company and position
            exp_header = f"<b>{exp['position']}</b> at <b>{exp['company']}</b>"
            story.append(Paragraph(exp_header, normal_style))
            
            # Duration
            duration = f"Duration: {exp['start_date'].strftime('%m/%Y')} - {exp['end_date'].strftime('%m/%Y')}"
            story.append(Paragraph(duration, normal_style))
            
            # Responsibilities
            if exp['responsibilities']:
                story.append(Paragraph(f"<b>Key Responsibilities:</b>", normal_style))
                story.append(Paragraph(exp['responsibilities'], normal_style))
            
            if i < len(user_data['work_experience']) - 1:
                story.append(Spacer(1, 15))
        
        story.append(Spacer(1, 20))
    
    # Footer
    story.append(Spacer(1, 30))
    footer_text = f"CV generated on {datetime.now().strftime('%d/%m/%Y')}"
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=9,
        alignment=TA_CENTER,
        textColor=colors.grey
    )
    story.append(Paragraph(footer_text, footer_style))
    
    # Build PDF
    doc.build(story)
    
    return filepath