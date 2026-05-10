import os, json, base64, cgi, io
from http.server import BaseHTTPRequestHandler
import resend

RESEND_API_KEY = os.environ.get("RESEND_API_KEY", "")
FROM_EMAIL     = os.environ.get("FROM_EMAIL", "CBC Solicitudes <onboarding@resend.dev>")
TO_EMAIL       = os.environ.get("TO_EMAIL", "")
CC_EMAIL       = os.environ.get("CC_EMAIL", "")
resend.api_key = RESEND_API_KEY

def build_html(data, fiscal_name, recibo_name):
    return f"""<!DOCTYPE html><html><head><meta charset='UTF-8'></head>
<body style='margin:0;padding:0;background:#f0f4fa;font-family:Arial,sans-serif;'>
<table width='100%' cellpadding='0' cellspacing='0' style='padding:32px 0;'>
<tr><td align='center'>
<table width='600' cellpadding='0' cellspacing='0' style='background:#fff;border-radius:16px;overflow:hidden;'>
<tr><td style='background:linear-gradient(135deg,#061a4a,#0a4fc4);padding:32px;'>
  <h1 style='margin:0;color:#fff;font-size:22px;'>Cliente nuevo CBC</h1>
  <p style='margin:8px 0 0;color:rgba(255,255,255,0.65);font-size:13px;'>Ref: {data['referencia']} · {data['fecha_registro']}</p>
</td></tr>
<tr><td style='padding:28px 32px 0;'>
  <p style='margin:0 0 14px;color:#0a4fc4;font-size:13px;font-weight:700;border-bottom:2px solid #e8edf5;padding-bottom:8px;'>DATOS DEL NEGOCIO</p>
  <table width='100%'>
    <tr><td style='padding:6px 0;color:#8a99bb;font-size:12px;width:160px;'>Propietario</td><td style='color:#0d1b3e;font-size:14px;'>{data['nombre_propietario']}</td></tr>
    <tr><td style='padding:6px 0;color:#8a99bb;font-size:12px;'>Negocio</td><td style='color:#0d1b3e;font-size:14px;'>{data['nombre_negocio']}</td></tr>
    <tr><td style='padding:6px 0;color:#8a99bb;font-size:12px;'>Direccion</td><td style='color:#0d1b3e;font-size:14px;'>{data['direccion']}</td></tr>
    <tr><td style='padding:6px 0;color:#8a99bb;font-size:12px;'>Telefono</td><td style='color:#0d1b3e;font-size:14px;'>{data['telefono']}</td></tr>
    <tr><td style='padding:6px 0;color:#8a99bb;font-size:12px;'>Correo</td><td style='color:#0d1b3e;font-size:14px;'>{data['correo_negocio']}</td></tr>
  </table>
</td></tr>
<tr><td style='padding:24px 32px 0;'>
  <p style='margin:0 0 14px;color:#0a4fc4;font-size:13px;font-weight:700;border-bottom:2px solid #e8edf5;padding-bottom:8px;'>UBICACION</p>
  <table width='100%'>
    <tr><td style='padding:6px 0;color:#8a99bb;font-size:12px;width:160px;'>Latitud</td><td style='color:#0d1b3e;font-size:14px;'>{data['latitud']}</td></tr>
    <tr><td style='padding:6px 0;color:#8a99bb;font-size:12px;'>Longitud</td><td style='color:#0d1b3e;font-size:14px;'>{data['longitud']}</td></tr>
    <tr><td style='padding:6px 0;color:#8a99bb;font-size:12px;'>Mapa</td><td style='font-size:14px;'><a href='{data['link_mapa']}' style='color:#0a4fc4;'>Ver en Google Maps</a></td></tr>
  </table>
</td></tr>
<tr><td style='padding:24px 32px 32px;'>
  <p style='margin:0 0 14px;color:#0a4fc4;font-size:13px;font-weight:700;border-bottom:2px solid #e8edf5;padding-bottom:8px;'>INFORMACION FISCAL</p>
  <table width='100%'>
    <tr><td style='padding:6px 0;color:#8a99bb;font-size:12px;width:160px;'>Tipo</td><td style='color:#0d1b3e;font-size:14px;'>{data['tipo_facturacion']}</td></tr>
    <tr><td style='padding:6px 0;color:#8a99bb;font-size:12px;'>Documento</td><td style='color:#0d1b3e;font-size:14px;'>{data['documento_requerido']}</td></tr>
    <tr><td style='padding:6px 0;color:#8a99bb;font-size:12px;'>Archivo fiscal</td><td style='color:#0d1b3e;font-size:14px;'>{fiscal_name}</td></tr>
    <tr><td style='padding:6px 0;color:#8a99bb;font-size:12px;'>Recibo</td><td style='color:#0d1b3e;font-size:14px;'>{recibo_name}</td></tr>
  </table>
</td></tr>
</table></td></tr></table></body></html>"""

class handler(BaseHTTPRequestHandler):
    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def _respond(self, status, payload):
        self.send_response(status)
        self._cors()
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(payload).encode())

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors()
        self.end_headers()

    def do_GET(self):
        self._respond(200, {"status": "API CBC activa", "version": "2.0-resend"})

    def do_POST(self):
        if not RESEND_API_KEY:
            return self._respond(500, {"ok": False, "error": "RESEND_API_KEY no configurada"})
        try:
            ctype = self.headers.get("Content-Type", "")
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length)
            fp = io.BytesIO(body)
            env = {"REQUEST_METHOD": "POST", "CONTENT_TYPE": ctype, "CONTENT_LENGTH": str(length)}
            form = cgi.FieldStorage(fp=fp, environ=env, keep_blank_values=True)

            campos = ["referencia","nombre_propietario","nombre_negocio","direccion",
                      "telefono","correo_negocio","latitud","longitud","link_mapa",
                      "tipo_facturacion","documento_requerido","fecha_registro"]
            data = {}
            for c in campos:
                data[c] = form.getvalue(c) or ""

            attachments = []
            fiscal_name = "—"
            recibo_name = "—"
            for field, label in [("archivo_fiscal","fiscal"),("archivo_recibo","recibo")]:
                if field in form and form[field].filename:
                    item = form[field]
                    content = item.file.read()
                    attachments.append({
                        "filename": item.filename,
                        "content": base64.b64encode(content).decode("ascii"),
                    })
                    if label == "fiscal": fiscal_name = item.filename
                    else: recibo_name = item.filename

            params = {
                "from": FROM_EMAIL,
                "to": [TO_EMAIL],
                "subject": f"Cliente nuevo CBC - {data['nombre_negocio']}",
                "html": build_html(data, fiscal_name, recibo_name),
                "reply_to": data["correo_negocio"],
            }
            if CC_EMAIL:
                params["cc"] = [CC_EMAIL]
            if attachments:
                params["attachments"] = attachments

            result = resend.Emails.send(params)
            return self._respond(200, {"ok": True, "id": str(result)})

        except Exception as e:
            return self._respond(500, {"ok": False, "error": f"{type(e).__name__}: {str(e)}"})
