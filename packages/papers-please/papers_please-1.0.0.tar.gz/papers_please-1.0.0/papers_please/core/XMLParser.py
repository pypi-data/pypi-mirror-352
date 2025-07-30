import xml.etree.ElementTree as ET

class XMLParser:
    def __init__(self, xml_path: str):
        self.xml_path = xml_path

    def extrair_artigos_bibtex(self) -> list[str]:
        tree = ET.parse(self.xml_path)
        root = tree.getroot()

        artigos_bibtex = []
        for artigo in root.findall(".//ARTIGO-PUBLICADO"):
            dados_basicos = artigo.find("DADOS-BASICOS-DO-ARTIGO")
            detalhamento = artigo.find("DETALHAMENTO-DO-ARTIGO")
            if dados_basicos is None or detalhamento is None:
                continue

            titulo = dados_basicos.attrib.get("TITULO-DO-ARTIGO", "")
            ano = dados_basicos.attrib.get("ANO-DO-ARTIGO", "")
            idioma = dados_basicos.attrib.get("IDIOMA", "")
            doi = dados_basicos.attrib.get("DOI", "")
            revista = detalhamento.attrib.get("TITULO-DO-PERIODICO-OU-REVISTA", "")
            volume = detalhamento.attrib.get("VOLUME", "")
            pagina_ini = detalhamento.attrib.get("PAGINA-INICIAL", "")
            pagina_fim = detalhamento.attrib.get("PAGINA-FINAL", "")
            issn = detalhamento.attrib.get("ISSN", "")

            autores = artigo.findall("AUTORES")
            nomes = [a.attrib.get("NOME-COMPLETO-DO-AUTOR") for a in autores]
            autor_bibtex = " and ".join(nomes)

            bibtex = f"""@article{{{nomes[0].split()[0].lower()}{ano},
  author = {{{autor_bibtex}}},
  title = {{{titulo}}},
  journal = {{{revista}}},
  year = {{{ano}}},
  volume = {{{volume}}},
  pages = {{{pagina_ini}--{pagina_fim}}},
  doi = {{{doi}}},
  issn = {{{issn}}},
  language = {{{idioma}}}
}}"""
            artigos_bibtex.append(bibtex)

        return artigos_bibtex

    def gerar_bibtex(self, output_path: str):
        artigos_bibtex = self.extrair_artigos_bibtex()
        with open(output_path, "w", encoding="utf-8") as f:
            for artigo in artigos_bibtex:
                f.write(artigo + "\n\n")
        print(f"Arquivo BibTeX gerado com sucesso em: {output_path}")
