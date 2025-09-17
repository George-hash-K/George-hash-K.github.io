import os
from openai import OpenAI
from dotenv import load_dotenv

import re
import requests
import shutil
from git import Repo
from pathlib import Path


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


### MAIN ####
client = OpenAI(
    # This is the default and can be omitted
    api_key=os.environ.get("OPENAI_API_KEY"),
)

PATH_TO_BLOG_REPO = Path('/Users/geoku/OPENAI/George-hash-K.github.io/.git')
PATH_TO_BLOG = PATH_TO_BLOG_REPO.parent
PATH_TO_CONTENT = PATH_TO_BLOG/"content"
PATH_TO_CONTENT.mkdir(exist_ok=True,parents=True)

random_text_string = 'jkfdjzzzzzzfjdkj'

with open(PATH_TO_BLOG/"index.html", 'w') as f:
    f.write(random_text_string)

update_blog()

# response = client.responses.create(
#     model="gpt-4o",
#     input=recipe,
#     temperature=1,
#     top_p=1.0,
#     max_output_tokens=500  # optional, control response length
# )

