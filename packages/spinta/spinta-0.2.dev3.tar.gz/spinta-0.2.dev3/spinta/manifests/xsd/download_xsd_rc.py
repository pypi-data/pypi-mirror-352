# import requests
#
# from lxml import html
#
# root_url = "https://ws.registrucentras.lt/broker/info.php"
#
# response = requests.get(root_url)
#
# document_list = html.fromstring(response.text)
#
# urls = document_list.xpath("//*[contains(@href, 'out')]")
#
# for url in urls:
#     url = url.attrib["href"]
#     response = requests.get(f"https://ws.registrucentras.lt{url}")
#     file_name = f'../../../xsds/rc{url.split("=")[1].split("&")[0]}.xsd'
#     with open(file_name, "w") as file:
#         file.write(response.text)
#     print(url)
#
#
# jar_url = "https://ws.registrucentras.lt/broker/xsd.klasif.php?kla_grupe=JAR"
#
# ntr_url = "https://ws.registrucentras.lt/broker/xsd.klasif.php?kla_grupe=NTR"
#
# klasif_urls = [jar_url, ntr_url]
#
# response = requests.get(jar_url)
#
# document_list = html.fromstring(response.text)
#
# urls = document_list.xpath("//*[contains(@href, 'kla_kodas')]")
#
# for url in urls:
#     url = url.attrib["href"]
#     response = requests.get(f"https://ws.registrucentras.lt{url}")
#     file_name = f'../../../xsds/rc_jar_klasif_{url.split("=")[2]}.xsd'
#     with open(file_name, "w") as file:
#         file.write(response.text)
#     print(url)
#
#
# response = requests.get(ntr_url)
#
# document_list = html.fromstring(response.text)
#
# urls = document_list.xpath("//*[contains(@href, 'kla_kodas')]")
#
# for url in urls:
#     url = url.attrib["href"]
#     response = requests.get(f"https://ws.registrucentras.lt{url}")
#     file_name = f'../../../xsds/rc_ntr_klasif_{url.split("=")[2]}.xsd'
#     with open(file_name, "w") as file:
#         file.write(response.text)
#     print(url)
#
# response = requests.get(f"https://ws.registrucentras.lt/broker/xsd.jadis.php?f=jadis-israsas.xsd")
# file_name = f'../../../xsds/rc_jadis-israsas.xsd'
# with open(file_name, "w") as file:
#     file.write(response.text)
#
# response = requests.get(f"https://ws.registrucentras.lt/broker/xsd.jadis.php?f=jadis-sarasas.xsd")
# file_name = f'../../../xsds/rc_jadis-sarasas.xsd'
# with open(file_name, "w") as file:
#     file.write(response.text)
#
# response = requests.get(f"https://ws.registrucentras.lt/broker/xsd.jadis.php?f=jadis-dalyvio-israsas.xsd")
# file_name = f'../../../xsds/rc_jadis-dalyvio-israsas.xsd'
# with open(file_name, "w") as file:
#     file.write(response.text)
#
