from pyalura import Course
from pydm import PyDM
import requests_cache

url = "https://app.aluracursos.com/course/java-trabajando-lambdas-streams-spring-framework/task/87011"
course = Course(url)


for item in course.iter_items():
    content = item.get_content()
    print(
        f"""
          item.url: {item.url}
          item.title: {item.title}
          item.index: {item.index}
          item.type: {item.type}
          section: {item.section.name}          
          has_content: {bool(content['content'])}
          is_video: {bool(content['videos'])}      
          """
    )
    download_drr = content["videos"]["hd"]["mp4"]
    with requests_cache.disabled():
        pydm = PyDM(download_drr)
        pydm.download()
