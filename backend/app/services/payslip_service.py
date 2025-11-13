"""
PayslipService for UNS-ClaudeJP 5.4.1
Professional PDF payslip generation service with ReportLab
"""

import logging
from datetime import datetime
from typing import Optional
from io import BytesIO
from decimal import Decimal

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch, cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer

from app.models.models import Employee, SalaryCalculation

logger = logging.getLogger(__name__)


class PayslipService:
    """Generador de nóminas PDF profesionales"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
        
    def _setup_custom_styles(self):
        self.styles.add(ParagraphStyle(
            name='PayslipTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#1e3a8a'),
            alignment=TA_CENTER,
            spaceAfter=12,
            fontName='Helvetica-Bold'
        ))
        
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=12,
            textColor=colors.HexColor('#1e40af'),
            spaceAfter=8,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        ))
    
    async def generate_payslip(
        self, 
        employee: Employee,
        salary: SalaryCalculation,
        company_name: str = "UNS-ClaudeJP"
    ) -> bytes:
        """Genera un PDF de nómina profesional"""
        try:
            logger.info(f"Generating payslip for {employee.hakenmoto_id}")
            
            buffer = BytesIO()
            doc = SimpleDocTemplate(
                buffer,
                pagesize=A4,
                rightMargin=1.5*cm,
                leftMargin=1.5*cm,
                topMargin=2*cm,
                bottomMargin=2*cm,
                title=f"Payslip_{employee.hakenmoto_id}_{salary.year}{salary.month:02d}"
            )
            
            story = []
            
            # Header
            title = Paragraph(
                "COMPROBANTE DE PAGO / PAYSLIP<br/>給与明細書",
                self.styles['PayslipTitle']
            )
            story.append(title)
            story.append(Spacer(1, 0.1*inch))
            
            subtitle = Paragraph(
                f"<b>{company_name}</b><br/>人材派遣会社",
                self.styles['SectionHeader']
            )
            subtitle.alignment = TA_CENTER
            story.append(subtitle)
            story.append(Spacer(1, 0.3*inch))
            
            # Employee info
            section = Paragraph("INFORMACIÓN DEL EMPLEADO", self.styles['SectionHeader'])
            story.append(section)
            
            emp_data = [
                ["ID:", f"{employee.hakenmoto_id}"],
                ["Nombre:", f"{employee.full_name_kanji}"],
                ["Período:", f"{salary.year}年{salary.month}月"],
            ]
            
            emp_table = Table(emp_data, colWidths=[5*cm, 12*cm])
            emp_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e0e7ff')),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('LEFTPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 5),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ]))
            story.append(emp_table)
            story.append(Spacer(1, 0.3*inch))
            
            # Hours breakdown
            section = Paragraph("DESGLOSE DE HORAS", self.styles['SectionHeader'])
            story.append(section)
            
            hours_data = [
                ["Concepto", "Horas", "Monto"]
            ]
            
            if salary.total_regular_hours:
                hours_data.append([
                    "Regulares", 
                    f"{float(salary.total_regular_hours):.1f}h",
                    self._format_currency(salary.base_salary or 0)
                ])
            
            if salary.total_overtime_hours:
                hours_data.append([
                    "Extras (25%)", 
                    f"{float(salary.total_overtime_hours):.1f}h",
                    self._format_currency(salary.overtime_pay or 0)
                ])
            
            if salary.total_night_hours:
                hours_data.append([
                    "Nocturnas", 
                    f"{float(salary.total_night_hours):.1f}h",
                    self._format_currency(salary.night_pay or 0)
                ])
            
            if salary.total_holiday_hours:
                hours_data.append([
                    "Festivas (35%)", 
                    f"{float(salary.total_holiday_hours):.1f}h",
                    self._format_currency(salary.holiday_pay or 0)
                ])
            
            if salary.bonus:
                hours_data.append(["Bono Mensual", "-", self._format_currency(salary.bonus)])
            
            if salary.gasoline_allowance:
                hours_data.append(["Gasolina", "-", self._format_currency(salary.gasoline_allowance)])
            
            hours_data.append(["SUBTOTAL", "", self._format_currency(salary.gross_salary or 0)])
            
            hours_table = Table(hours_data, colWidths=[6*cm, 3*cm, 5*cm])
            hours_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3a8a')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#dbeafe')),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                ('LEFTPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 5),
            ]))
            story.append(hours_table)
            story.append(Spacer(1, 0.3*inch))
            
            # Deductions
            section = Paragraph("DEDUCCIONES", self.styles['SectionHeader'])
            story.append(section)
            
            deductions = (salary.apartment_deduction or 0) + (salary.other_deductions or 0)
            
            deductions_data = [
                ["Concepto", "Monto"],
            ]
            
            if salary.apartment_deduction:
                deductions_data.append(["Apartamento", self._format_currency(salary.apartment_deduction)])
            
            if salary.other_deductions:
                deductions_data.append(["Otros", self._format_currency(salary.other_deductions)])
            
            deductions_data.append(["TOTAL", self._format_currency(deductions)])
            
            deductions_table = Table(deductions_data, colWidths=[10*cm, 5*cm])
            deductions_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#991b1b')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#fee2e2')),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                ('LEFTPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 5),
            ]))
            story.append(deductions_table)
            story.append(Spacer(1, 0.3*inch))
            
            # Summary
            section = Paragraph("RESUMEN FINAL", self.styles['SectionHeader'])
            story.append(section)
            
            summary_data = [
                ["Salario Bruto", self._format_currency(salary.gross_salary or 0)],
                ["Deducciones", f"-{self._format_currency(deductions)}"],
                ["SALARIO NETO", self._format_currency(salary.net_salary or 0)],
            ]
            
            summary_table = Table(summary_data, colWidths=[10*cm, 5*cm])
            summary_table.setStyle(TableStyle([
                ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
                ('BACKGROUND', (0, 2), (-1, 2), colors.HexColor('#10b981')),
                ('TEXTCOLOR', (0, 2), (-1, 2), colors.whitesmoke),
                ('FONTNAME', (0, 2), (-1, 2), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 2), (-1, 2), 12),
                ('BOX', (0, 0), (-1, 2), 1.5, colors.HexColor('#1e3a8a')),
                ('LEFTPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
            ]))
            story.append(summary_table)
            
            story.append(Spacer(1, 0.5*inch))
            footer = Paragraph(
                f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')} | "
                "Documento Confidencial",
                self.styles['Normal']
            )
            footer.alignment = TA_CENTER
            story.append(footer)
            
            doc.build(story)
            pdf_bytes = buffer.getvalue()
            buffer.close()
            
            logger.info(f"Payslip generated: {len(pdf_bytes)} bytes")
            return pdf_bytes
            
        except Exception as e:
            logger.error(f"Error generating payslip: {str(e)}")
            raise ValueError(f"Failed to generate payslip: {str(e)}")
    
    def _format_currency(self, amount: float) -> str:
        if amount is None:
            return "¥0"
        if isinstance(amount, Decimal):
            amount = float(amount)
        return f"¥{amount:,.0f}"
