from fastapi import FastAPI, Form, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from typing import Optional

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

GMAIL_USER = "crucer3000@gmail.com"
GMAIL_PASS = "rwhx sbpz tdfl prmm"
TO_EMAIL   = "wperla@cbc.co"
CC_EMAIL   = "sac@cbc.co"

@app.post("/api/enviar")
async def enviar(
    referencia:          str = Form(...),
    nombre_propietario:  str = Form(...),
    nombre_negocio:      str = Form(...),
    direccion:           str = Form(...),
    telefono:            str = Form(...),
    correo_negocio:      str = Form(...),
    latitud:             str = Form(...),
    longitud:            str = Form(...),
    link_mapa:           str = Form(...),
    tipo_facturacion:    str = Form(...),
    documento_requerido: str = Form(...),
    fecha_registro:      str = Form(...),
    archivo_fiscal:      Optional[UploadFile] = File(None),
    archivo_recibo:      Optional[UploadFile] = File(None),
):
    subject = f"Cliente nuevo CBC - Solicitud de facturacion: {nombre_negocio}"
    archivo_fiscal_nombre = archivo_fiscal.filename if archivo_fiscal else "—"
    archivo_recibo_nombre = archivo_recibo.filename if archivo_recibo else "—"

    html = f"""<!DOCTYPE html><html><head><meta charset='UTF-8'></head>
<body style='margin:0;padding:0;background:#f0f4fa;font-family:Arial,sans-serif;'>
<table width='100%' cellpadding='0' cellspacing='0' style='padding:32px 0;'>
<tr><td align='center'>
<table width='600' cellpadding='0' cellspacing='0' style='background:#fff;border-radius:16px;overflow:hidden;'>
<tr><td style='background:linear-gradient(135deg,#061a4a,#0a4fc4);padding:32px;'>
  <p style='margin:0 0 6px;color:rgba(255,255,255,0.7);font-size:12px;'>CARE Platform · CBC</p>
  <h1 style='margin:0;color:#fff;font-size:22px;'>Cliente nuevo CBC</h1>
  <p style='margin:8px 0 0;color:rgba(255,255,255,0.65);font-size:13px;'>Ref: {referencia} · {fecha_registro}</p>
</td></tr>
<tr><td style='padding:28px 32px 0;'>
  <p style='margin:0 0 14px;color:#0a4fc4;font-size:13px;font-weight:700;border-bottom:2px solid #e8edf5;padding-bottom:8px;'>DATOS DEL NEGOCIO</p>
  <table width='100%'>
    <tr><td style='padding:6px 0;color:#8a99bb;font-size:12px;width:160px;'>Propietario</td><td style='color:#0d1b3e;font-size:14px;'>{nombre_propietario}</td></tr>
    <tr><td style='padding:6px 0;color:#8a99bb;font-size:12px;'>Negocio</td><td style='color:#0d1b3e;font-size:14px;'>{nombre_negocio}</td></tr>
    <tr><td style='padding:6px 0;color:#8a99bb;font-size:12px;'>Direccion</td><td style='color:#0d1b3e;font-size:14px;'>{direccion}</td></tr>
    <tr><td style='padding:6px 0;color:#8a99bb;font-size:12px;'>Telefono</td><td style='color:#0d1b3e;font-size:14px;'>{telefono}</td></tr>
    <tr><td style='padding:6px 0;color:#8a99bb;font-size:12px;'>Correo</td><td style='color:#0d1b3e;font-size:14px;'>{correo_negocio}</td></tr>
  </table>
</td></tr>
<tr><td style='padding:24px 32px 0;'>
  <p style='margin:0 0 14px;color:#0a4fc4;font-size:13px;font-weight:700;border-bottom:2px solid #e8edf5;padding-bottom:8px;'>UBICACION</p>
  <table width='100%'>
    <tr><td style='padding:6px 0;color:#8a99bb;font-size:12px;width:160px;'>Latitud</td><td style='color:#0d1b3e;font-size:14px;'>{latitud}</td></tr>
    <tr><td style='padding:6px 0;color:#8a99bb;font-size:12px;'>Longitud</td><td style='color:#0d1b3e;font-size:14px;'>{longitud}</td></tr>
    <tr><td style='padding:6px 0;color:#8a99bb;font-size:12px;'>Mapa</td><td style='font-size:14px;'><a href='{link_mapa}' style='color:#0a4fc4;'>Ver en Google Maps</a></td></tr>
  </table>
</td></tr>
<tr><td style='padding:24px 32px 32px;'>
  <p style='margin:0 0 14px;color:#0a4fc4;font-size:13px;font-weight:700;border-bottom:2px solid #e8edf5;padding-bottom:8px;'>INFORMACION FISCAL</p>
  <table width='100%'>
    <tr><td style='padding:6px 0;color:#8a99bb;font-size:12px;width:160px;'>Tipo</td><td style='color:#0d1b3e;font-size:14px;'>{tipo_facturacion}</td></tr>
    <tr><td style='padding:6px 0;color:#8a99bb;font-size:12px;'>Documento</td><td style='color:#0d1b3e;font-size:14px;'>{documento_requerido}</td></tr>
    <tr><td style='padding:6px 0;color:#8a99bb;font-size:12px;'>Archivo fiscal</td><td style='color:#0d1b3e;font-size:14px;'>{archivo_fiscal_nombre}</td></tr>
    <tr><td style='padding:6px 0;color:#8a99bb;font-size:12px;'>Recibo agua/luz</td><td style='color:#0d1b3e;font-size:14px;'>{archivo_recibo_nombre}</td></tr>
  </table>
</td></tr>
</table></td></tr></table></body></html>"""

    msg = MIMEMultipart()
    msg['From']    = f"Solicitud Pepsi CBC <{GMAIL_USER}>"
    msg['To']      = TO_EMAIL
    msg['Cc']      = CC_EMAIL
    msg['Subject'] = subject
    msg.attach(MIMEText(html, 'html'))

    for upload in [archivo_fiscal, archivo_recibo]:
        if upload and upload.filename:
            data = await upload.read()
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(data)
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename="{upload.filename}"')
            msg.attach(part)

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(GMAIL_USER, GMAIL_PASS)
            smtp.sendmail(GMAIL_USER, [TO_EMAIL, CC_EMAIL], msg.as_string())
        return {"ok": True, "message": "Correo enviado correctamente"}
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/enviar")
def health():
    return {"status": "API CBC activa"}
