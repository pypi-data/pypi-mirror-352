import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from .Terminal import Terminal

class Email(Terminal):
    """ Clase para manejar eventos relacionados con el envío de correos electrónicos. """

    def __init__(self, dev: bool = False):
        """
        Inicializa la clase Email con un diccionario de configuración vacío.
        """
        super().__init__(dev=dev)
        self._configuracion = {
            "smtp_server": "",
            "smtp_port": 0,
            "smtp_username": "",
            "smtp_password": "",
            "entorno": "test",  # test, qa, productivo
            "nombre_aprendizaje": ""
        }
        self._cuerpo_email = ""

    # Métodos para configurar y obtener valores de configuración
    def set_configuracion(self, clave_o_diccionario, valor=None):
        """
        Establece valores en la configuración del correo.

        :param clave_o_diccionario: Puede ser un diccionario con múltiples claves y valores o una clave específica.
        :param valor: Valor a asignar si se proporciona una clave específica.
        """
        if isinstance(clave_o_diccionario, dict):
            for clave, val in clave_o_diccionario.items():
                if clave in self._configuracion:
                    self._configuracion[clave] = val
                else:
                    raise KeyError(f"La clave '{clave}' no es válida en la configuración.")
        elif isinstance(clave_o_diccionario, str):
            if clave_o_diccionario in self._configuracion:
                self._configuracion[clave_o_diccionario] = valor
            else:
                raise KeyError(f"La clave '{clave_o_diccionario}' no es válida en la configuración.")
        else:
            raise TypeError("El primer argumento debe ser un diccionario o una clave válida.")

    def get_configuracion(self, clave:str|None =None) -> dict|str:
        """
        Obtiene la configuración del correo. Si se proporciona una clave, devuelve el valor asociado a esa clave.
        
        :param clave: Clave específica para obtener su valor. Si no se proporciona, devuelve todo el diccionario de configuración.
        :return: Valor de la clave específica o todo el diccionario de configuración.
        """
        if clave is None:
            return self._configuracion
        elif isinstance(clave, str):
            if clave in self._configuracion:
                return self._configuracion[clave]
            else:
                raise KeyError(f"La clave '{clave}' no es válida en la configuración.")

    # Método para estructurar el cuerpo del correo
    def armar_cuerpo_email(self, titulo: str = "Titulo del mail", subtitulo: str = "Subtitulo del mail", mensaje: str = "Mensaje del mail", fecha: str = "00/00/0000", duracion: str = "00:00:00", link_boton: str = "www.example.com.ar") -> str:
        """
        Arma el cuerpo del correo electrónico en un formato estructurado.

        :param titulo: Título del mensaje.
        :param subtitulo: Subtítulo del mensaje.
        :param mensaje: Mensaje o contenido del mensaje.
        :param fecha: Fecha de ejecución.
        :param duracion: Duración de ejecución.
        """
        self._cuerpo_email = """ 
        <!--
        * This email was built using Tabular.
        * For more information, visit https://tabular.email
        -->
        <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
        <html xmlns="http://www.w3.org/1999/xhtml" xmlns:v="urn:schemas-microsoft-com:vml" xmlns:o="urn:schemas-microsoft-com:office:office" lang="en">
        <head>
        <title></title>
        <meta charset="UTF-8" />
        <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
        <!--[if !mso]>-->
        <meta http-equiv="X-UA-Compatible" content="IE=edge" />
        <!--<![endif]-->
        <meta name="x-apple-disable-message-reformatting" content="" />
        <meta content="target-densitydpi=device-dpi" name="viewport" />
        <meta content="true" name="HandheldFriendly" />
        <meta content="width=device-width" name="viewport" />
        <meta name="format-detection" content="telephone=no, date=no, address=no, email=no, url=no" />
        <style type="text/css">
        table {{
        border-collapse: separate;
        table-layout: fixed;
        mso-table-lspace: 0pt;
        mso-table-rspace: 0pt
        }}
        table td {{
        border-collapse: collapse
        }}
        .ExternalClass {{
        width: 100%
        }}
        .ExternalClass,
        .ExternalClass p,
        .ExternalClass span,
        .ExternalClass font,
        .ExternalClass td,
        .ExternalClass div {{
        line-height: 100%
        }}
        body, a, li, p, h1, h2, h3 {{
        -ms-text-size-adjust: 100%;
        -webkit-text-size-adjust: 100%;
        }}
        html {{
        -webkit-text-size-adjust: none !important
        }}
        body, #innerTable {{
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale
        }}
        #innerTable img+div {{
        display: none;
        display: none !important
        }}
        img {{
        Margin: 0;
        padding: 0;
        -ms-interpolation-mode: bicubic
        }}
        h1, h2, h3, p, a {{
        line-height: inherit;
        overflow-wrap: normal;
        white-space: normal;
        word-break: break-word
        }}
        a {{
        text-decoration: none
        }}
        h1, h2, h3, p {{
        min-width: 100%!important;
        width: 100%!important;
        max-width: 100%!important;
        display: inline-block!important;
        border: 0;
        padding: 0;
        margin: 0
        }}
        a[x-apple-data-detectors] {{
        color: inherit !important;
        text-decoration: none !important;
        font-size: inherit !important;
        font-family: inherit !important;
        font-weight: inherit !important;
        line-height: inherit !important
        }}
        u + #body a {{
        color: inherit;
        text-decoration: none;
        font-size: inherit;
        font-family: inherit;
        font-weight: inherit;
        line-height: inherit;
        }}
        a[href^="mailto"],
        a[href^="tel"],
        a[href^="sms"] {{
        color: inherit;
        text-decoration: none
        }}
        </style>
        <style type="text/css">
        @media (min-width: 481px) {{
        .hd {{ display: none!important }}
        }}
        </style>
        <style type="text/css">
        @media (max-width: 480px) {{
        .hm {{ display: none!important }}
        }}
        </style>
        <style type="text/css">
        @media (max-width: 480px) {{
        .t25{{mso-line-height-alt:0px!important;line-height:0!important;display:none!important}}.t26{{padding-left:30px!important;padding-bottom:40px!important;padding-right:30px!important}}.t23{{width:353px!important}}.t6{{padding-bottom:20px!important}}.t5{{line-height:28px!important;font-size:26px!important;letter-spacing:-1.04px!important}}.t41{{padding:40px 30px!important}}.t16{{padding-bottom:34px!important}}.t1{{padding-bottom:50px!important}}.t3{{width:80px!important}}
        }}
        </style>
        <!--[if !mso]>-->
        <link href="https://fonts.googleapis.com/css2?family=Albert+Sans:wght@300;500;700;800&amp;display=swap" rel="stylesheet" type="text/css" />
        <!--<![endif]-->
        <!--[if mso]>
        <xml>
        <o:OfficeDocumentSettings>
        <o:AllowPNG/>
        <o:PixelsPerInch>96</o:PixelsPerInch>
        </o:OfficeDocumentSettings>
        </xml>
        <![endif]-->
        </head>
        <body id="body" class="t47" style="min-width:100%;Margin:0px;padding:0px;background-color:#ffffff;"><div class="t46" style="background-color:#ffffff;"><table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" align="center"><tr><td class="t45" style="font-size:0;line-height:0;mso-line-height-rule:exactly;background-color:#ffffff;" valign="top" align="center">
        <!--[if mso]>
        <v:background xmlns:v="urn:schemas-microsoft-com:vml" fill="true" stroke="false">
        <v:fill color="#ffffff"/>
        </v:background>
        <![endif]-->
        <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" align="center" id="innerTable"><tr><td><div class="t25" style="mso-line-height-rule:exactly;mso-line-height-alt:45px;line-height:45px;font-size:1px;display:block;">&nbsp;&nbsp;</div></td></tr><tr><td align="center">
        <table class="t29" role="presentation" cellpadding="0" cellspacing="0" style="Margin-left:auto;Margin-right:auto;"><tr><td width="600" class="t28" style="background-color:#FFFFFF;border:1px solid #EE7421;width:600px;">
        <table class="t27" role="presentation" cellpadding="0" cellspacing="0" width="100%" style="width:100%;"><tr><td class="t26" style="padding:0 50px 60px 50px;"><table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="width:100% !important;"><tr><td align="left">
        <table class="t4" role="presentation" cellpadding="0" cellspacing="0" style="Margin-right:auto;"><tr><td width="130" class="t3" style="width:130px;">
        <table class="t2" role="presentation" cellpadding="0" cellspacing="0" width="100%" style="width:100%;"><tr><td class="t1"><div style="font-size:0px;"><img class="t0" style="display:block;border:0;height:auto;width:100%;Margin:0;max-width:100%;" width="130" height="130" alt="" src="https://4a3afa9a-a9b8-403a-9124-551dc70b40ab.b-cdn.net/e/36c703cb-3c91-46e3-8637-21618e6e1427/8e10c59f-ed34-42bf-8ab8-464534929e65.png"/></div></td></tr></table>
        </td></tr></table>
        </td></tr><tr><td align="center">
        <table class="t9" role="presentation" cellpadding="0" cellspacing="0" style="Margin-left:auto;Margin-right:auto;"><tr><td width="498" class="t8" style="width:600px;">
        <table class="t7" role="presentation" cellpadding="0" cellspacing="0" width="100%" style="width:100%;"><tr><td class="t6" style="padding:0 0 25px 0;"><h1 class="t5" style="margin:0;Margin:0;font-family:Albert Sans,BlinkMacSystemFont,Segoe UI,Helvetica Neue,Arial,sans-serif;line-height:41px;font-weight:800;font-style:normal;font-size:39px;text-decoration:none;text-transform:none;letter-spacing:-1.56px;direction:ltr;color:#5D9731;text-align:left;mso-line-height-rule:exactly;mso-text-raise:1px;">{titulo}</h1></td></tr></table>
        </td></tr></table>
        </td></tr><tr><td align="center">
        <table class="t14" role="presentation" cellpadding="0" cellspacing="0" style="Margin-left:auto;Margin-right:auto;"><tr><td width="498" class="t13" style="width:600px;">
        <table class="t12" role="presentation" cellpadding="0" cellspacing="0" width="100%" style="width:100%;"><tr><td class="t11" style="padding:0 0 22px 0;"><p class="t10" style="margin:0;Margin:0;font-family:Albert Sans,BlinkMacSystemFont,Segoe UI,Helvetica Neue,Arial,sans-serif;line-height:22px;font-weight:500;font-style:normal;font-size:14px;text-decoration:none;text-transform:none;letter-spacing:-0.56px;direction:ltr;color:#F9B90E;text-align:left;mso-line-height-rule:exactly;mso-text-raise:2px;">{subtitulo}&nbsp;</p></td></tr></table>
        </td></tr></table>
        </td></tr><tr><td align="center">
        <table class="t19" role="presentation" cellpadding="0" cellspacing="0" style="Margin-left:auto;Margin-right:auto;"><tr><td width="498" class="t18" style="width:600px;">
        <table class="t17" role="presentation" cellpadding="0" cellspacing="0" width="100%" style="width:100%;"><tr><td class="t16" style="padding:0 0 45px 0;"><p class="t15" style="margin:0;Margin:0;font-family:Albert Sans,BlinkMacSystemFont,Segoe UI,Helvetica Neue,Arial,sans-serif;line-height:22px;font-weight:500;font-style:normal;font-size:14px;text-decoration:none;text-transform:none;letter-spacing:-0.56px;direction:ltr;color:#333333;text-align:left;mso-line-height-rule:exactly;mso-text-raise:2px;">{mensaje}<br/>&#xFEFF; [{fecha}] Duraci&#xF3;n de la ejecuci&#xF3;n: {duracion}<br/>&#xFEFF;</p></td></tr></table>
        </td></tr></table>
        </td></tr><tr><td align="left">
        <table class="t24" role="presentation" cellpadding="0" cellspacing="0" style="Margin-right:auto;"><tr><td width="250" class="t23" style="background-color:#EE7421;overflow:hidden;width:250px;border-radius:44px 44px 44px 44px;">
        <table class="t22" role="presentation" cellpadding="0" cellspacing="0" width="100%" style="width:100%;"><tr><td class="t21" style="text-align:center;line-height:44px;mso-line-height-rule:exactly;mso-text-raise:10px;"><a class="t20" href="{link_boton}" style="display:block;margin:0;Margin:0;font-family:Albert Sans,BlinkMacSystemFont,Segoe UI,Helvetica Neue,Arial,sans-serif;line-height:44px;font-weight:800;font-style:normal;font-size:12px;text-decoration:none;text-transform:uppercase;letter-spacing:2.4px;direction:ltr;color:#F8F8F8;text-align:center;mso-line-height-rule:exactly;mso-text-raise:10px;" target="_blank">Ver reporte</a></td></tr></table>
        </td></tr></table>
        </td></tr></table></td></tr></table>
        </td></tr></table>
        </td></tr><tr><td align="center">
        <table class="t44" role="presentation" cellpadding="0" cellspacing="0" style="Margin-left:auto;Margin-right:auto;"><tr><td width="600" class="t43" style="background-color:#EE7421;width:600px;">
        <table class="t42" role="presentation" cellpadding="0" cellspacing="0" width="100%" style="width:100%;"><tr><td class="t41" style="padding:48px 50px 48px 50px;"><table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="width:100% !important;"><tr><td align="center">
        <table class="t34" role="presentation" cellpadding="0" cellspacing="0" style="Margin-left:auto;Margin-right:auto;"><tr><td width="500" class="t33" style="width:600px;">
        <table class="t32" role="presentation" cellpadding="0" cellspacing="0" width="100%" style="width:100%;"><tr><td class="t31"><p class="t30" style="margin:0;Margin:0;font-family:Albert Sans,BlinkMacSystemFont,Segoe UI,Helvetica Neue,Arial,sans-serif;line-height:22px;font-weight:700;font-style:normal;font-size:16px;text-decoration:none;text-transform:none;direction:ltr;color:#FDFDFD;text-align:center;mso-line-height-rule:exactly;mso-text-raise:2px;">Grupo Los Grobo - Sistemas IT - RPA</p></td></tr></table>
        </td></tr></table>
        </td></tr><tr><td align="center">
        <table class="t40" role="presentation" cellpadding="0" cellspacing="0" style="Margin-left:auto;Margin-right:auto;"><tr><td width="500" class="t39" style="width:600px;">
        <table class="t38" role="presentation" cellpadding="0" cellspacing="0" width="100%" style="width:100%;"><tr><td class="t37"><p class="t36" style="margin:0;Margin:0;font-family:Albert Sans,BlinkMacSystemFont,Segoe UI,Helvetica Neue,Arial,sans-serif;line-height:22px;font-weight:300;font-style:normal;font-size:12px;text-decoration:none;text-transform:none;direction:ltr;color:#FDFDFD;text-align:center;mso-line-height-rule:exactly;mso-text-raise:3px;"><a class="t35" href="https://tabular.email" style="margin:0;Margin:0;font-weight:300;font-style:normal;text-decoration:none;direction:ltr;color:#FDFDFD;mso-line-height-rule:exactly;" target="_blank">Contacto &#x2022; Sugerencias &#x2022; Problemas</a></p></td></tr></table>
        </td></tr></table>
        </td></tr></table></td></tr></table>
        </td></tr></table>
        </td></tr></table></td></tr></table></div><div class="gmail-fix" style="display: none; white-space: nowrap; font: 15px courier; line-height: 0;">&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;</div></body>
        </html>
        """.format(titulo=titulo, subtitulo=subtitulo, mensaje=mensaje, fecha=fecha, duracion=duracion, link_boton=link_boton)
        
        return self._cuerpo_email

    def _armar_asunto(self, exito: bool = True) -> str:
        """
        Arma el asunto del correo según el entorno, el tipo de resultado y el nombre del aprendizaje.
        """
        entorno_value = self.get_configuracion("entorno")
        entorno = str(entorno_value).lower()
        nombre = self.get_configuracion("nombre_aprendizaje")
        if entorno == "test":
            if exito:
                return f"🧪 GLGRPA TEST | {nombre}"
            else:
                return f"❌ GLGRPA TEST | ERROR | {nombre}"
        elif entorno == "qa":
            if exito:
                return f"🥁 GLGRPA QA | {nombre}"
            else:
                return f"❌ GLGRPA QA | {nombre}"
        else:  # productivo
            if exito:
                return f"🟢 GLGRPA | {nombre}"
            else:
                return f"🔴 GLGRPA | {nombre}"

    # Método de envío de correo
    def enviar_email(self, destinatarios: list, asunto: str, adjunto=None) -> bool:
        """
        Envía un correo electrónico personalizado.

        :param destinatarios: Lista de direcciones de correo electrónico de los destinatarios.
        :param asunto: Asunto del correo electrónico.
        :param adjunto: Mensaje o contenido del correo electrónico (opcional).
        :return: True si el correo se envió correctamente, False en caso contrario.
        """
        try:
            # Configuración del servidor SMTP
            smtp_server = str(self.get_configuracion("smtp_server"))
            smtp_port_value = self.get_configuracion("smtp_port")
            if isinstance(smtp_port_value, dict):
                raise TypeError("El valor de 'smtp_port' no puede ser un diccionario.")
            smtp_port = int(smtp_port_value)
            smtp_username = str(self.get_configuracion("smtp_username"))
            smtp_password = str(self.get_configuracion("smtp_password"))

            # Crear el mensaje
            msg = MIMEMultipart()
            msg['From'] = smtp_username
            msg['To'] = ", ".join(destinatarios)
            msg['Subject'] = asunto

            # Adjuntar el cuerpo del correo
            if adjunto is not None:
                cuerpo_email = adjunto
            else:
                cuerpo_email = self.armar_cuerpo_email()
            msg.attach(MIMEText(cuerpo_email, 'html'))

            # Conectar y enviar el correo
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(smtp_username, smtp_password)
                server.send_message(msg)

            return True
        except Exception as e:
            self.mostrar(f"Error al enviar el correo: {e}", True)
            raise TypeError("Error al enviar correo.")

    def enviar_email_exito(self, destinatarios: list, mensaje: str = "El proceso finalizó correctamente.", fecha: str|None = None, duracion: str|None = None, link_boton: str = "www.example.com.ar") -> bool:
        """
        Envía un correo estandarizado de éxito según el entorno y el nombre del aprendizaje.

        :param destinatarios: Lista de destinatarios.
        :param mensaje: Mensaje principal.
        :param fecha: Fecha de ejecución (opcional, por defecto actual).
        :param duracion: Duración de ejecución (opcional).
        :param link_boton: Link para el botón del correo.
        :return: True si el correo se envió correctamente.
        """
        asunto = self._armar_asunto(exito=True)
        if fecha is None:
            fecha = self.obtener_hora_actual("%d/%m/%Y")
        if duracion is None:
            duracion = "00:00:00"
        cuerpo = self.armar_cuerpo_email(
            titulo="Ejecución exitosa",
            subtitulo="El proceso finalizó correctamente.",
            mensaje=mensaje,
            fecha=fecha,
            duracion=duracion,
            link_boton=link_boton
        )
        return self.enviar_email(destinatarios, asunto, cuerpo)

    def enviar_email_error(self, destinatarios: list, mensaje: str = "El proceso finalizó con errores.", fecha: str|None = None, duracion: str|None = None, link_boton: str = "www.example.com.ar") -> bool:
        """
        Envía un correo estandarizado de error según el entorno y el nombre del aprendizaje.

        :param destinatarios: Lista de destinatarios.
        :param mensaje: Mensaje principal.
        :param fecha: Fecha de ejecución (opcional, por defecto actual).
        :param duracion: Duración de ejecución (opcional).
        :param link_boton: Link para el botón del correo.
        :return: True si el correo se envió correctamente.
        """
        asunto = self._armar_asunto(exito=False)
        if fecha is None:
            fecha = self.obtener_hora_actual("%d/%m/%Y")
        if duracion is None:
            duracion = "00:00:00"
        cuerpo = self.armar_cuerpo_email(
            titulo="Ejecución con errores",
            subtitulo="El proceso finalizó con errores.",
            mensaje=mensaje,
            fecha=fecha,
            duracion=duracion,
            link_boton=link_boton
        )
        return self.enviar_email(destinatarios, asunto, cuerpo)