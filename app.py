@app.route("/download-pdf")
def download_pdf():
    url = request.args.get("site", "").strip()
    if not url:
        return "No URL provided", 400

    u = url if url.startswith("http") else "https://" + url
    checks, err = audit(u)
    if err:
        return f"Error scanning site: {err}", 500

    passed = sum(1 for c in checks if c[1])
    score = round(passed / len(checks) * 100) if checks else 0

    class AuditPDF(FPDF):
        def header(self):
            self.set_fill_color(34, 211, 238)
            self.rect(0, 0, 210, 32, 'F')
            
            self.set_y(7)
            self.set_x(15)
            self.set_font('Helvetica', 'B', 22)
            self.set_text_color(255, 255, 255)
            self.cell(0, 10, 'NIKHILBUILDS', 0, 1, 'L')
            
            self.set_x(15)
            self.set_font('Helvetica', '', 11)
            self.cell(0, 8, 'Website Health Audit Report', 0, 1, 'R')
            
            self.ln(10)

        def footer(self):
            pass  # Empty footer - CTA box will handle it

    try:
        pdf = AuditPDF()
        pdf.add_page()
        pdf.set_margins(15, 38, 15)
        pdf.set_auto_page_break(auto=False, margin=0)
        
        # 1. Website Info
        pdf.set_font('Helvetica', '', 11)
        pdf.set_text_color(100, 100, 100)
        pdf.cell(0, 7, f"Website: {u}", 0, 1)
        pdf.cell(0, 7, f"Audit Date: {datetime.now().strftime('%d %B %Y')}", 0, 1)
        pdf.ln(5)
        
        # 2. Score Box
        score_color = (34, 197, 94) if score >= 70 else (234, 179, 8) if score >= 40 else (239, 68, 68)
        box_bg = (240, 253, 250) if score >= 70 else (254, 252, 232) if score >= 40 else (254, 242, 242)
        
        pdf.set_fill_color(*box_bg)
        pdf.set_draw_color(34, 211, 238)
        pdf.set_line_width(0.5)
        pdf.rect(15, pdf.get_y(), 180, 30, 'DF')
        
        pdf.set_font('Helvetica', 'B', 11)
        pdf.set_text_color(100, 100, 100)
        pdf.set_x(15)
        pdf.cell(0, 8, "OVERALL HEALTH SCORE", 0, 1, 'C')
        
        pdf.set_font('Helvetica', 'B', 28)
        pdf.set_text_color(*score_color)
        pdf.set_x(15)
        pdf.cell(0, 14, f"{score} / 100", 0, 1, 'C')
        
        pdf.ln(8)
        
        # 3. Section Title
        pdf.set_font('Helvetica', 'B', 14)
        pdf.set_text_color(34, 211, 238)
        pdf.cell(0, 8, "DETAILED ANALYSIS", 0, 1)
        pdf.set_draw_color(34, 211, 238)
        pdf.set_line_width(1)
        pdf.line(15, pdf.get_y(), 90, pdf.get_y())
        pdf.ln(5)
        
        # 4. Checks
        for name, ok, detail, fix, icon in checks:
            status = "PASS" if ok else "FAIL"
            status_color = (34, 197, 94) if ok else (239, 68, 68)
            
            pdf.set_font('Helvetica', 'B', 11)
            pdf.set_text_color(*status_color)
            pdf.cell(25, 8, f"[{status}]", 0, 0)
            
            pdf.set_font('Helvetica', 'B', 12)
            pdf.set_text_color(30, 30, 30)
            pdf.cell(0, 8, name, 0, 1)
            
            pdf.set_font('Helvetica', '', 11)
            pdf.set_text_color(100, 100, 100)
            clean_detail = _pdf_text(str(detail))[:70]
            pdf.set_x(15)
            pdf.cell(0, 6, f"Result: {clean_detail}", 0, 1)
            
            if not ok:
                pdf.set_x(15)
                pdf.set_font('Helvetica', 'I', 11)
                pdf.set_text_color(239, 68, 68)
                clean_fix = _pdf_text(str(fix))[:80]
                pdf.cell(0, 6, f"Fix: {clean_fix}", 0, 1)
            
            pdf.ln(4)
        
        # 5. MERGED CTA + FOOTER BOX (at bottom)
        pdf.set_y(257)  # Fixed at bottom
        pdf.set_fill_color(34, 211, 238)
        pdf.rect(15, pdf.get_y(), 180, 30, 'F')
        
        pdf.set_font('Helvetica', 'B', 13)
        pdf.set_text_color(0, 0, 0)
        pdf.set_x(15)
        pdf.cell(0, 10, "Need help fixing these issues?", 0, 1, 'C')
        
        pdf.set_font('Helvetica', '', 12)
        pdf.set_text_color(0, 0, 0)
        pdf.set_x(15)
        pdf.cell(0, 10, "hello@nikhilbuilds.com | nikhilbuilds.com", 0, 1, 'C')

        pdf_bytes = pdf.output()
        safe_filename = u.replace("https://", "").replace("http://", "").replace("/", "_").replace(":", "")[:30]
        
        return send_file(
            io.BytesIO(pdf_bytes),
            mimetype="application/pdf",
            as_attachment=True,
            download_name=f"SiteCheck_{safe_filename}.pdf",
        )
    except Exception as e:
        return "PDF generation error: " + str(e), 500
