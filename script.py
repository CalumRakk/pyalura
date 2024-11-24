from pyalura import Course

url = "https://app.aluracursos.com/course/java-api-conectandola-front-end"
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
          is_video: {bool(content['video'])}      
          """
    )
