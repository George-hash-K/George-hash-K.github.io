import os
from openai import OpenAI
from dotenv import load_dotenv

import re
import requests
import shutil
from git import Repo
from pathlib import Path
from bs4 import BeautifulSoup as Soup

load_dotenv()  # take environment variables



def update_blog(commit_mesage='Update blog'):
    # GitPython -- repo location
    repo = Repo(PATH_TO_BLOG_REPO)
    # git add .
    repo.git.add(all=True)
    # git commit  -m "updates blog"
    repo.index.commit(commit_mesage)
    # git push
    origin = repo.remote(name='origin')
    origin.push()

def create_new_blog(title, content, cover_image):
    cover_image = Path(cover_image)
    files = len(list(PATH_TO_CONTENT.glob("*.html")))
    new_title = f"{files+1}.html"
    path_to_new_content = PATH_TO_CONTENT/new_title
    shutil.copy(cover_image, PATH_TO_CONTENT)

    if not os.path.exists(path_to_new_content):
        # write a new html file
        with open(path_to_new_content, "w") as f:
            f.write("<!DOCTYPE html>\n")
            f.write(f"<html>\n<head>\n<title> {title} </title>\n</head>\n")
            f.write("<body>\n")
            f.write(f"<img src='{cover_image.name}' alt='Cover Image'><br />\n")
            # openai generation
            f.write(content.replace("\n", "<br />\n"))
            f.write("</body>\n")
            f.write("</html>")
            print("Blog created")
            return path_to_new_content

    else:
        raise FileExistsError("File already exists, please check again your name. Aborting!")

def check_for_duplicate_links(path_to_new_content, links):
    urls = [str(link.get("href")) for link in links]
    content_path = str(Path(*path_to_new_content.parts[-2:]))
    return content_path in urls

def write_to_index(path_to_new_content):
    with open(PATH_TO_BLOG/'index.html') as index:
        soup = Soup(index.read())
    links = soup.find_all('a')
    last_link = links[-1]

    if check_for_duplicate_links(path_to_new_content, links):
        raise ValueError("Lnk already exists")
    link_to_new_blog = soup.new_tag("a", href = Path(*path_to_new_content.parts[-2:]))
    link_to_new_blog.string = path_to_new_content.name.split('.')[0]
    last_link.insert_after(link_to_new_blog)

    with open(PATH_TO_BLOG/'index.html','w') as f:
        f.write(str(soup.prettify(formatter='html')))
def create_prompt(title):
    prompt = '''
    Biography:
    My name is Jose and I am a python instructor for coding.
    
    Blog
    Title: {}
    tags: technology, python, coding, ai, machine learning
    Summary: I talk about what the future of AI could hold for Python
    Full Text: '''.format(title)
    return prompt

def dalle2_prompt(title):
     prompt = f"3d clay render showing {title}"
     return prompt

def save_image(image_url, file_name):
    # URL --> pic.png
    image_res = requests.get(image_url,stream=True)
    if image_res.status_code == 200:
        with open(file_name, 'wb') as f:
            shutil.copyfileobj(image_res.raw,f)
    else:
        print('ERROR LOADING IMAGE')
    return image_res.status_code


### MAIN ####
client = OpenAI(
    # This is the default and can be omitted
    api_key=os.environ.get("OPENAI_API_KEY"),
)

PATH_TO_BLOG_REPO = Path('/Users/geoku/OPENAI/George-hash-K.github.io/.git')
PATH_TO_BLOG = PATH_TO_BLOG_REPO.parent
PATH_TO_CONTENT = PATH_TO_BLOG/"content"
PATH_TO_CONTENT.mkdir(exist_ok=True,parents=True)

path_to_new_content = create_new_blog('Test title','aaaaaaa','logo.png')
with open(PATH_TO_BLOG/"index.html") as index:
    soup = Soup(index.read())
write_to_index(path_to_new_content)
update_blog()

title = "The future of Python and AI"

response = client.responses.create(
    model="gpt-4o",
    input=create_prompt(title),
    temperature=1,
    top_p=1.0,
    max_output_tokens=1000  # optional, control response length
)
blog_content = response.output[0].content[0].text
image_prompt = dalle2_prompt(title)
image_response = client.images.generate(
    model="dall-e-3",  # or "dall-e-3"
    prompt=image_prompt,
    n=1,
    size="1024x1024"
)

# Get the image URL
image_url = image_response.data[0].url
print(image_url)
save_image(image_url,file_name='title2.png')

path_to_new_content = create_new_blog(title,blog_content,'title2.png')

write_to_index(path_to_new_content)

update_blog()