from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.colors import Color, black, white, red, green, orange, gray
from reportlab.lib.utils import ImageReader
from datetime import date
import os

# ---------- Utilitaires de mise en forme ----------

JOURS_FR = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]
MOIS_FR = ["janvier", "février", "mars", "avril", "mai", "juin",
           "juillet", "août", "septembre", "octobre", "novembre", "décembre"]

def format_date_fr(d: date) -> str:
    j = JOURS_FR[d.weekday()]
    return f"{j.capitalize()} {d.day} {MOIS_FR[d.month-1]} {d.year}"

def safe_draw_image(c: canvas.Canvas, path: str, x: float, y: float, w: float, h: float):
    if not path:
        c.setFillColorRGB(0.9, 0.9, 0.9)
        c.roundRect(x, y, w, h, 6, fill=True, stroke=0)
        c.setFillColor(black)
        c.setFont("Helvetica", 8)
        c.drawCentredString(x + w/2, y + h/2 - 4, "image")
        return
    try:
        c.drawImage(ImageReader(path), x, y, width=w, height=h, preserveAspectRatio=True, mask='auto')
    except Exception:
        c.setFillColorRGB(0.9, 0.9, 0.9)
        c.roundRect(x, y, w, h, 6, fill=True, stroke=0)
        c.setFillColor(black)
        c.setFont("Helvetica", 8)
        c.drawCentredString(x + w/2, y + h/2 - 4, "image")

def chip_icon(c, x, y, size, color, label, icon_path=None):
    if icon_path:
        safe_draw_image(c, icon_path, x, y, size, size)
    else:
        c.setFillColor(color)
        c.circle(x + size/2, y + size/2, size/2, fill=True, stroke=0)
    c.setFillColor(black)
    c.setFont("Helvetica", 10)
    c.drawString(x + size + 6, y + size/2 - 3, label)

def draw_header(c, title, date_str, left_logo=None, right_logo=None, page_w=A4[0], page_h=A4[1]):
    margin = 1.5 * cm
    logo_h = 2.2 * cm
    logo_w = 2.2 * cm

    # Logos
    safe_draw_image(c, left_logo, margin, page_h - margin - logo_h, logo_w, logo_h)
    safe_draw_image(c, right_logo, page_w - margin - logo_w, page_h - margin - logo_h, logo_w, logo_h)

    # ✅ Gérer les titres multi-lignes
    c.setFont("Helvetica-Bold", 16)
    c.setFillColor(black)
    text_y = page_h - margin - logo_h / 2

    for i, line in enumerate(title.splitlines()):
        c.drawCentredString(page_w / 2, text_y - (i * 18), line)  # 18 pts entre les lignes

    # Date
    c.setFont("Helvetica", 10)
    c.drawCentredString(page_w / 2, text_y - (len(title.splitlines()) * 18) - 10, date_str)

def draw_card(c, x, y, w, h, title, value_text, icon_path=None, suffix=None):
    """
    Carte modernisée :
    - Titre en haut à gauche (taille 12)
    - Valeur centrée horizontalement, en bas de la carte (taille 14)
    - Icône optionnelle en haut à droite
    """
    # --- Fond de la carte ---
    c.setFillColorRGB(0.97, 0.97, 0.97)
    c.roundRect(x, y, w, h, 10, fill=True, stroke=0)

    # --- Titre (haut gauche) ---
    c.setFillColor(black)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(x + 10, y + h - 16, title)

    # --- Icône (haut droite) ---
    if icon_path:
        icon_size = 22  # ajustable
        safe_draw_image(
            c,
            icon_path,
            x + w - icon_size - 8,  # marge à droite
            y + h - icon_size - 8,  # marge en haut
            icon_size,
            icon_size
        )

    # --- Valeur (centrée en bas) ---
    c.setFont("Helvetica-Bold", 14)
    try:
        # Si numérique → formaté avec suffixe
        text = f"{float(value_text):.0f}{suffix if suffix else ''}"
    except (ValueError, TypeError):
        text = str(value_text)

    # Position verticale : 25% de la hauteur
    c.drawCentredString(x + w / 2, y + 0.25 * h, text)

# ---------- Génération du rapport ----------

def generate_hrv_report(
    output_pdf_path: str,
    report_date: date,
    athletes: list,
    left_logo_path=None,
    right_logo_path=None,
    daily_chart_path=None,
    legend_icons=None,
):
    os.makedirs(os.path.dirname(output_pdf_path), exist_ok=True)
    c = canvas.Canvas(output_pdf_path, pagesize=A4)
    page_w, page_h = A4
    margin = 1.5 * cm

    # ---------- PAGE DE GARDE ----------
    title = "Rapport ASM Natation\nVariabilité Fréquence Cardiaque"
    draw_header(c, title, format_date_fr(report_date), left_logo_path, right_logo_path, page_w, page_h)


    # Graphique quotidien agrandi
    chart_w = page_w - 2 * margin
    chart_h = 15 * cm
    chart_x = margin
    chart_y = page_h - (margin + 3.2 * cm + 40 + chart_h)
    safe_draw_image(c, daily_chart_path, chart_x, chart_y, chart_w, chart_h)

    # Séparation
    c.setStrokeColor(gray)
    c.setLineWidth(0.5)
    c.line(margin, chart_y - 20, page_w - margin, chart_y - 20)

    # Bloc légende
    legend_y = chart_y - 3.5 * cm - 0.8 * cm
    if legend_icons is None:
        legend_icons = {}

    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(black)
    c.drawString(margin * 2, legend_y + 2.5 * cm, "Légende :")

    chip_icon(c, margin, legend_y + 1.2 * cm, 14, red, "Cycle menstruel", legend_icons.get("menstruation"))
    chip_icon(c, margin + 6 * cm, legend_y + 1.2 * cm, 14, green, "OK", legend_icons.get("ok"))
    chip_icon(c, margin + 10.5 * cm, legend_y + 1.2 * cm, 14, orange, "Vigilance", legend_icons.get("vigilance"))
    chip_icon(c, margin + 15 * cm, legend_y + 1.2 * cm, 14, red, "Danger", legend_icons.get("danger"))

    c.showPage()

    # ---------- PAGES ATHLÈTES ----------
    for a in athletes:
        nom = a.get("Nom", "Athlète")
        d_str = format_date_fr(report_date)

        # Titre
        c.setFont("Helvetica-Bold", 16)
        c.setFillColor(black)
        c.drawString(margin, page_h - margin - 10, f"Rapport Individuel de {nom}")
        c.setFont("Helvetica", 10)
        c.drawString(margin, page_h - margin - 26, d_str)

        # === Cartes organisées en 3 colonnes ===
        card_h = 1.8 * cm
        col_gap = 0.8 * cm
        col_w = (page_w - 2 * margin - 2 * col_gap) / 3  # 3 colonnes
        top_y = page_h - margin - 26 - 2 * cm

        col1_x = margin
        col2_x = margin + col_w + col_gap
        col3_x = margin + 2 * (col_w + col_gap)

        # --- Icônes ---
        heart_icon = "./icons/rythme-cardiaque (1).png"
        perf_icons = {
            "% Réserve": "./icons/boulon.png",
            "% Régénération": "./icons/regeneration.png",
            "% Capacité Effort": "./icons/intensite.png",
        }

        # --- Colonne 1 : FC Couché / FC Debout ---
        draw_card(c, col1_x, top_y - card_h, col_w, card_h,
                "FC Couché", a.get("FC Couché", 0), icon_path=heart_icon)
        draw_card(c, col1_x, top_y - 2 * card_h - 0.4 * cm, col_w, card_h,
                "FC Debout", a.get("FC Debout", 0), icon_path=heart_icon)

        # --- Colonne 2 : Réserve / Régénération ---
        draw_card(c, col2_x, top_y - card_h, col_w, card_h,
                "% Réserve", a.get("% Réserve", 0), icon_path=perf_icons.get("% Réserve"), suffix="%")
        draw_card(c, col2_x, top_y - 2 * card_h - 0.4 * cm, col_w, card_h,
                "% Régénération", a.get("% Régénération", 0), icon_path=perf_icons.get("% Régénération"), suffix="%")

        # --- Colonne 3 : Capacité d'effort ---
        draw_card(c, col3_x, top_y - card_h, col_w, card_h,
                "% Capacité Effort", a.get("% Capacité Effort", 0), icon_path=perf_icons.get("% Capacité Effort"), suffix="%")

        # ✅ Nouvelle variable cohérente pour placer les graphiques en dessous
        cards_bottom_y = top_y - 2 * card_h - 0 * cm

        # === Graphiques côte à côte ===
        gap = 0.6 * cm
        charts_h = 6.5 * cm
        charts_w = (page_w - 2 * margin - gap) / 2
        charts_y = cards_bottom_y - 2 * cm - charts_h  # ✅ utilise cards_bottom_y

        # draw_card(c, margin, charts_y + charts_h + 0.5 * cm, charts_w, 0.6 * cm, "", "")
        safe_draw_image(c, a.get("chart_left"), margin, charts_y, charts_w, charts_h)
        safe_draw_image(c, a.get("chart_right"), margin + charts_w + gap, charts_y, charts_w, charts_h)

        # === Bloc Recommandations + Commentaires ===
        rec_y = charts_y - 3.5 * cm - 1 * cm  # ↳ ajoute une marge de 30 px (~0.8 cm)
        block_h = 4.0 * cm
        block_w = page_w - 2 * margin

        # Fond de la carte
        c.setFillColorRGB(0.97, 0.97, 0.97)
        c.roundRect(margin, rec_y, block_w, block_h, 12, fill=True, stroke=1)

        # Titre "Recommandations"
        c.setFont("Helvetica-Bold", 11)
        c.setFillColor(black)
        c.drawString(margin + 0.6 * cm, rec_y + block_h - 16, "Recommandations")

        # Définir les zones gauche / droite
        left_w = 4.5 * cm
        right_x = margin + left_w + 0.3 * cm

        # Trait de séparation vertical
        c.setStrokeColorRGB(0.6, 0.6, 0.6)
        c.setLineWidth(1)
        c.line(right_x, rec_y + 0.5 * cm, right_x, rec_y + block_h - 0.5 * cm)

        # === Colonne gauche : icône + label ===
        statut = (a.get("Recommandations") or "OK").strip().lower()
        status_map = {
            "ok": ("OK", green, legend_icons.get("ok")),
            "vigilance": ("Vigilance", orange, legend_icons.get("vigilance")),
            "danger": ("Danger", red, legend_icons.get("danger")),
        }
        label_statut, color_statut, icon_statut = status_map.get(statut, ("OK", green, legend_icons.get("ok")))

        # Icône centrée verticalement dans la colonne gauche
        icon_size = 40
        icon_x = margin + (left_w - icon_size) / 2
        icon_y = rec_y + (block_h - icon_size) / 2
        safe_draw_image(c, icon_statut, icon_x, icon_y, icon_size, icon_size)

        # Texte du statut sous l’icône
        c.setFont("Helvetica-Bold", 12)
        c.setFillColor(black)
        c.drawCentredString(margin + left_w / 2, rec_y + 0.4 * cm, label_statut)

        # === Colonne droite : commentaires ===
        comm_x = right_x + 0.5 * cm
        comm_w = page_w - comm_x - margin
        comments = a.get("Commentaires", "").strip()

        c.setFont("Helvetica", 11)
        c.setFillColor(black)

        # --- Fonction utilitaire : couper automatiquement le texte ---
        def wrap_text(text, font_name, font_size, max_width):
            words = text.split()
            lines = []
            line = ""
            for word in words:
                test_line = (line + " " + word).strip()
                if c.stringWidth(test_line, font_name, font_size) <= max_width:
                    line = test_line
                else:
                    lines.append(line)
                    line = word
            if line:
                lines.append(line)
            return lines

        # --- Découper et afficher ---
        lines = wrap_text(comments, "Helvetica", 11, comm_w - 10)
        text_y = rec_y + block_h - 18
        for ln in lines[:6]:  # max 6 lignes
            c.drawString(comm_x, text_y, ln)
            text_y -= 13

         # === Si Menstruation : icône + message en bas du bloc ===
        if a.get("Menstruation", False):
            menstruation_icon = legend_icons.get("menstruation", "./icons/menstruation.png")

            # Taille et position
            icon_size = 16
            msg_y = rec_y + 6  # marge depuis le bas du bloc
            msg_x_center = margin + block_w / 2  # centré horizontalement

            # Icône à gauche du texte
            icon_x = msg_x_center - 75 # icône à gauche du texte
            icon_y = msg_y - 2
            safe_draw_image(c, menstruation_icon, icon_x, icon_y, icon_size, icon_size)

            # Texte d’avertissement
            c.setFont("Helvetica-Bold", 10)
            c.setFillColor(red)
            c.drawCentredString(msg_x_center + 10, msg_y + 3, "Attention : Menstruations")

    c.save()
    print(f"✅ Rapport sauvegardé : {output_pdf_path}")
