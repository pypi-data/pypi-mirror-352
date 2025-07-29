from http.server import HTTPServer
from http.server import BaseHTTPRequestHandler
from string import Template
import re
import os
import click


class CustomHTTPServer(HTTPServer):
    def __init__(self, server_address, RequestHandlerClass, html):
        super().__init__(server_address, RequestHandlerClass)
        self.html = html


class CustomHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(self.server.html.encode())
            return

        path = "./" + self.path[1:]
        if os.path.exists(path):
            self.send_response(200)
            if path.endswith(".css"):
                self.send_header("Content-type", "text/css; charset=utf-8")
            elif path.endswith(".woff2"):
                self.send_header("Content-type", "font/woff2")
            else:
                self.send_header("Content-type", "text/plain; charset=utf-8")
            self.end_headers()
            with open(path, "rb") as f:
                self.wfile.write(f.read())
            return

        self.send_response(404)
        self.end_headers()
        self.wfile.write(b"File Not Found")


TEMPLATE = Template(
    """\
<html lang="ja">
  <head>
    <title>fontsplitta test</title>
    <meta charset="UTF-8" />
    <link rel="stylesheet" type="text/css" href="${css_file}" />
    <style>
      body {
        font-family: "${font_family}";
        font-size: 48px;
      }
    </style>
  </head>
  <body>
    あのイーハトーヴォのすきとおった風、<br />
    夏でも底に冷たさをもつ青いそら、<br />
    うつくしい森で飾られたモリーオ市、<br />
    郊外のぎらぎらひかる草の波。
  </body>
</html>
"""
)


def generate_html(css_file: str):
    with open(css_file, "r") as file:
        content = file.read()
    pattern = r"^\s*font-family:\s+\"([^\"]+)\";$"
    font_family = re.search(pattern, content, flags=re.MULTILINE).group(1)

    return TEMPLATE.substitute(font_family=font_family, css_file=css_file)


@click.command()
@click.option("--addr", type=str, default="localhost")
@click.option("--port", type=int, default=8080)
@click.option("--css_file", type=str, default="output/font-face.css")
def test_server(addr: str, port: int, css_file: str):
    html = generate_html(css_file)
    with CustomHTTPServer((addr, port), CustomHTTPRequestHandler, html) as httpd:
        print(f"Serving on http://{addr}:{port}/")
        httpd.serve_forever()
