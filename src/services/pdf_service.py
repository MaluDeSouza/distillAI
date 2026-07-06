import io
import os
import re
from fpdf import FPDF
from src.schemas.distiller import DistillerResponse

class PDFReportTemplate(FPDF):
    def __init__(self):
        super().__init__()
        
        # Mapeia dinamicamente o caminho absoluto da pasta src/assets/
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        regular_font_path = os.path.join(base_dir, "assets", "Roboto-Regular.ttf")
        bold_font_path = os.path.join(base_dir, "assets", "Roboto-Bold.ttf")
        
        # Registra as fontes locais no fpdf2
        self.add_font("Roboto", "", regular_font_path)
        self.add_font("Roboto", "B", bold_font_path)
        
    def header(self):
        self.set_font("Roboto", "B", 10)
        self.set_text_color(120, 120, 120)
        self.cell(0, 10, "MANUAL DE PROCEDIMENTOS OPERACIONAIS - DISTILLAI", border=False, ln=True, align="C")
        self.line(10, 20, 200, 20)
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font("Roboto", "", 8) 
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f"Página {self.page_no()}", align="C")

class PdfExportService:
    def _clean_whitespace(self, text: str) -> str:
        """Limpa as quebras de linha e previne estouro de largura."""
        if not text:
            return ""
        
        text = str(text)
        
        # 1. Filtra lixo invisível do Unicode
        text = re.sub(r'[\u200b\u200c\u200d\ufeff]', '', text)
        
        # 2. Achata espaços e quebras
        text = re.sub(r'\s+', ' ', text).strip()
        
        # 3. CORREÇÃO DA LARGURA: Força espaço a cada 40 caracteres (70 estourava a margem!)
        text = re.sub(r'([^\s]{40})', r'\1 ', text)
        
        return text

    def _safe_write(self, pdf: FPDF, height: int, text: str):
        """
        Método blindado com Tolerância a Falhas (Graceful Degradation).
        Se a string for radioativa e quebrar o fpdf2, o lote não é abortado.
        """
        clean_text = self._clean_whitespace(text)
        try:
            # Tenta desenhar o texto normalmente
            pdf.multi_cell(0, height, clean_text)
        except Exception:
            # Se o fpdf2 engasgar, resetamos a posição do cursor (X) para a margem padrão (15mm)
            pdf.set_x(15) 
            
            # Fallback 1: Removemos todos os acentos e caracteres especiais, forçando ASCII puro
            fallback_text = clean_text.encode("ascii", "ignore").decode("ascii")
            
            try:
                pdf.multi_cell(0, height, fallback_text + " [Formatação adaptada]")
            except Exception:
                # Fallback 2: Se até o ASCII falhar, salvamos o documento omitindo apenas o trecho bugado
                pdf.set_x(15)
                pdf.multi_cell(0, height, "[Trecho omitido: incompatibilidade com renderizador PDF]")

    def generate_pdf(self, data: DistillerResponse) -> io.BytesIO:
        pdf = PDFReportTemplate()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)

        for kb in data.knowledge_bases:
            # Categoria
            pdf.set_font("Roboto", "B", 14)
            pdf.set_text_color(0, 51, 102)
            self._safe_write(pdf, 10, f"CATEGORIA: {kb.categoria.upper()}")
            pdf.ln(4)

            for proc in kb.procedimentos:
                # Sintoma
                pdf.set_font("Roboto", "B", 12)
                pdf.set_text_color(30, 30, 30)
                self._safe_write(pdf, 8, f"Sintoma: {proc.sintoma}")
                
                # Diagnóstico Base
                pdf.set_font("Roboto", "", 11)
                pdf.set_text_color(80, 80, 80)
                self._safe_write(pdf, 6, f"Diagnóstico Base: {proc.diagnostico}")
                pdf.ln(3)

                # Soluções
                pdf.set_text_color(0, 0, 0)
                for i, passo in enumerate(proc.solucao_passo_a_passo, 1):
                    self._safe_write(pdf, 7, f"  {i}. {passo}")
                pdf.ln(4)

                # Transbordo
                pdf.set_font("Roboto", "B", 10)
                pdf.set_text_color(204, 0, 0)
                self._safe_write(pdf, 7, f"TRANSBORDO: {proc.quando_chamar_humano}")
                
                pdf.ln(8)
            
            pdf.ln(10)

        pdf_bytes = io.BytesIO()
        pdf.output(pdf_bytes)
        pdf_bytes.seek(0)
        
        return pdf_bytes