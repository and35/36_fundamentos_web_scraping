import requests
import lxml.html as html
import datetime
import os

# tambien usare datetime para medir el timpo de ejecucion
start_time = datetime.datetime.now()
# url
home_page = 'https://www.larepublica.co/'
# expresiones
xpath_urls = '//a[contains(@class,"kicker")]/@href'
xpath_title =  '//div[@class="mb-auto" or @class="col order-2"]/h2/span/text()' #'//div[@class="mb-auto"]/h2/span/text()'
xpath_summary = '//div[@class="lead"]/p/text()'
xpath_body = '//div[@class="html-content"]/p[not(@class)]/text()'


# funcion para: validar link y limpiar el html para el scraping con la expresion
def parse(link): #parsed = preprocesar = analizar 
    # buneas practicas: creamos un try except para validar el status_code del link sea = 200 (validar el link)
    try:
        response = requests.get(link) # A. se hace una peticion para obtener el documento html de link
        if response.status_code == 200:
            # B. response.content: regresa el contenido html 
            # decode: transforma caracteres especiales en un formato que pueda manejar python
            html_content = response.content.decode('utf8')
            return html.fromstring(html_content) # C. convertimos el contenido html a un formato para aplicarle xpath   
        else: 
            raise ValueError(f'Error:{response.status_code}') # en caso de no ser code=200 aqui levanta el error 
    except ValueError as ve:
        print(ve)


# funcion para remover lista de chars indeseados de los titulos
def remove_chars(text, chars):
    for char in chars:
        text = text.replace(char, "")
    return text


# funcion para recorrer cada link de noticias y extraer titulo, resumen y body para guardarlo en un .txt
def save_notice(links, today):
    for n, link in enumerate(links[0:3]):
        """print(link) el output hasta aqui es una lista de links donde podriamos buscar palabras grep: 
        python "la_republica_scraper/scraper_rep.py" | grep harvard         recuerda que grep busca entre las lineas"""
        parsed = parse(link) # validamos y preprocesamos
        try:
            title = parsed.xpath(xpath_title)[0]  # vamos a usar el valor y no lista por eso usamos [0]  
            # removemos  chars del titulo ya que los siguientes no son soportados como nombres de documentos
            chars_to_remove = ["\n                        ", "\n                    ", '\"', "?", "¿","|"]
            title = remove_chars(title, chars_to_remove)

            summary = parsed.xpath(xpath_summary)[0]
            body = parsed.xpath(xpath_body)

            # guardamos el contenido en un archivo .txt
            with open(f'{today}/{title}.txt', 'w', encoding='utf-8') as f:
                f.write(title)
                f.write('\n\n')
                f.write(summary)
                f.write('\n\n')
                for p in body:
                    f.write(p)
                    f.write('\n')
            #os.system('cls')
            print(f'{len(links)}:{n}, title:{title}') 
        except IndexError:
            print("error en el index")
            continue # saltara al siguiente link cuando se rompa
    
def run():
    # 1. obtenemos los links de cada noticia donde se realizara el scraping 
    parsed = parse(home_page) # 1.1 validamos links y preprocesamos el html (dentro de aqui estan los pasos A,B,C)
    links_to_notices = parsed.xpath(xpath_urls) # D. pasamos la expresion de busqueda Xpath al html limpio 

    # 2. creamos una carpeta para guardar las noticias del dia de hoy 
    today = datetime.date.today().strftime("%d-%m-%Y") # libreria.crear_fecha.del_dia_de_hoy().con_el formato(d-m-a)
    if not os.path.isdir(today): # si la carpeta del dia de hoy no existe creala 
        os.mkdir(today)
    
    # 3. guardamos una por una el contenido de todas las noticias 
    save_notice(links_to_notices, today) # validamos links y preprocesamos el html

if __name__ == "__main__":
    run()
    print(f'Duracion: {(datetime.datetime.now() - start_time)}') # tiempo de ejecucion 
