"""
    JHC2HTML is software to generate a single html file with a website or game, including images and fonts.
    Copyright (C) 2021 Leonardo Wambak

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.


    Software inspired by other software initially made in java: <https://sourceforge.net/projects/spaf/>
"""


import os
import PySimpleGUI as sg
import base64


class Jch2htmlUI:
    """
    Graphical interface using PySimpleGUI library
    """
    def __init__(self):
        
        sg.theme("DarkGrey11")
        # Layot
        self.layout = [
            [sg.Text("\nEsse programa une todos os tipos de arquivos de um site ou jogo em HTML \n(Scripts, Stylesheets, imagens e fontes) em um único \narquivo HTML.\n\n\n")],
            [sg.Text("Escolher arquivo"), sg.Input(key="input",), sg.FileBrowse("Buscar", file_types=(("HTML Files", ".html"),))],
            [sg.Checkbox("Todos os aquivos para base64", key="base64", default=True)],
            [sg.Text("*Marque essa opção se deseja transformar todos os arquivos em Base64\n (caminhos de arquivos dentro de uma variável javaScript\n não serão trocados).\n")],
            [sg.InputText(visible=False, enable_events=True, key="path"), sg.FileSaveAs("Salvar HTML", file_types=(("HTML Files", ".html"),))]
        ]
        # Janela
        self.window = sg.Window("JCH2HTML", self.layout, element_justification='c')

    def main(self):

        while True:
            self.event, self.values = self.window.read()
            
            if self.event == sg.WIN_CLOSED:
                break

            elif self.event == "path" and self.values["path"] != "":
                self.file_input = self.values["input"]
                self.output = self.values["path"]
                
                try:
                    self.file = Jhc2Html()
                    self.packed = self.file.pack(self.file_input, self.output, self.values["base64"])
                except OSError:
                    sg.Popup("Occoreu um erro na compactação do seu arquivo, certifique-se que o arquivo foi selecionado corretamente!")
                else:
                    #Cria um arquivo com o contedo empacotado
                    self.file_packed = open(self.output, "w+")
                    self.file_packed.write(self.packed)
                    self.file_packed.close()
                    
                    sg.Popup(f"Arquivo salvo em:\n\n{self.output}")


class Jhc2Html:
    """
    Main class with all methods to pack all css and javascript files into one
    html file
    """

    def pack(self, file_input, output, base64):
        """
        Returns the contents of the packaged html file

        :param file_input: Html file path
        :param output: Path of the file to be written
        :param base64: (bool)
        :return: String with all bundled files
        """

        #lê o arquivo
        packed = open(file_input, "r").read()
        #obtem a raiz do arquivo
        path = os.path.dirname(os.path.realpath(file_input)) + "/"
        #empacota os arquivos 
        packed = self.pack_styles(packed, path, base64)
        packed = self.pack_scripts(packed, path)

        if base64:
            packed = self.pack_images(packed, path)

        return packed


    def pack_styles(self, html, path, base64):
        """
        Returns the replaced content of all <link/> tags by the content of the css file.

        :param html: Content of html file
        :param path: Html file path
        :param base64: (bool)
        :return: String with css wrapped
        """
        packed_styles = html
        styles = html.split("<link")
        for style in styles:
            if "href=" and "stylesheet" in style:
                style = style.split(">")[0]
                rel = style.split("href=")[1].replace("\'", "\"").split("\"")[1]
                if len(rel) > 0 and not rel.startswith("http:") and not rel.startswith("https:") and not rel.startswith("file:") and not rel.startswith("data:"):
                    path_css = os.path.dirname(os.path.realpath(path + rel)) + "/"
                    css = open(path + rel, "r").read()
                    
                    if base64:
                        css = self.pack_base64(css, path_css)
                        
                    packed_styles = packed_styles.replace("<link" + style + ">", "\n<style>\n" + css + "\n</style>\n")
                
            
        return packed_styles


    def pack_base64(self, css, path):
        """
        Returns content of css with all images replaced by Base64

        :param css: Contents of css file
        :param path: Css file path
        :return: Css bundled with Base64 images
        """
        packed_base64 = css
        base64 = css.split("url")
        for i in range(len(base64)):
            url = base64[i]
            if url.startswith("("):
                url = base64[i].split(")")[0]
                url = url[1:]
                ref = url
                if ref.startswith("\"") or ref.startswith("'"):
                    ref = ref.replace("\'", "\"").split("\"")[1]
                
                if len(ref) > 0 and not ref.startswith("data:") and not ref.startswith("http:") and not ref.startswith("https:") and not ref.startswith("file:"):
                    packed_base64 = packed_base64.replace(url, "\"" + self.file_to_base64(path + ref) + "\"")
        
        return packed_base64

    
    def file_to_base64(self, path):
        """
        File Converter for Base64.
        Returns a base64 with the specific type of file extension.

        :param path: Path of the file to be decoded
        :return: Base64
        """
        types = [
            (".jpeg", "data:image/jpeg;base64,"),
            (".jpg", "data:image/jpeg;base64,"),
            (".gif", "data:image/gif;base64,"),
            (".png", "data:image/png;base64,"),
            (".ico", "data:image/ico;base64,"),
            (".svg", "data:image/svg;base64,"),
            (".html", "data:text/html;base64,"),
            (".htm", "data:text/html;base64,"),
            (".js", "data:text/javascript;base64,"),
            (".css", "data:text/css;base64,"),
            (".xml", "data:text/xml;base64,"),
            (".json", "data:text/json;base64,"),
            (".ttf", "data:font/opentype;base64,"),
            (".woff", "data:font/woff;base64,")
        ]

        with open(path, "rb") as image_file:
            b64 = base64.b64encode(image_file.read())
            b64 = b64.decode("utf-8")

            for type_extension in types:
                if os.path.basename(path).endswith(type_extension[0]):
                    b64 = type_extension[1] + b64


        return b64


    def pack_scripts(self, html, path):
        """
        It does the same as pack_script, but it replaces the <script> tags with the
        content of the js file.
        
        :param html: Contents of html file
        :param path: html file path
        :return: String with bundled js

        """
        packed_scripts = html
        scripts = html.split("<script")
        for script in scripts:
            if "src=" in script:
                script = script.split("></script>")[0]
                src = script.split("src=")[1].replace("\'", "\"").split("\"")[1]

                if len(src) > 0 and not src.startswith("http:") and not src.startswith("https:") and not src.startswith("file:") and not src.startswith("data:"):
                    path_js = os.path.dirname(os.path.realpath(path + src)) + "/"
                    js = open(path + src, "r").read()
                    
                    packed_scripts = packed_scripts.replace("<script" + script + "></script>", "\n<script>\n" + js + "\n</script>\n")
                
            
        return packed_scripts

    def pack_images(self, html, path):
        """
        Search for icons and images within the html and change them all to Base64.
        Returns the html ready to be written to a file.

        :param html: Content html
        :param path: Html file path
        :return: Html packaged
        """
        packed_html = html
        #Icons
        icons = html.split("<link")
        for icon in icons:
            style = icon.split(">")[0]
            if "href=" and "shortcut icon" in style:
                ref = style.split("href=")[1].replace("\'","\"").split("\"")[1]
                if len(ref) > 0 and not ref.startswith("http:") and not ref.startswith("https:") and not ref.startswith("file:") and not ref.startswith("data:"):
                    fileB64 = self.file_to_base64(path + ref)
                    packed_html = packed_html.replace(ref, fileB64)
    
        images = html.split("<img")
        for image in images:
            script = image.split(">")[0]
            if "src=" in script:
                ref = script.split("src=")[1].replace("\'", "\"").split("\"")[1]
                if len(ref) > 0 and not ref.startswith("http:") and not ref.startswith("https:") and not ref.startswith("file:") and not ref.startswith("data:"):
                    packed_html = packed_html.replace(ref, self.file_to_base64(path + ref))

        return packed_html



window = Jch2htmlUI()
window.main()