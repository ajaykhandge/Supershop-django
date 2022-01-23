from .models import Category


#context processor make the data available to all the project and 
#must be registered in the settings.py 

def menu_links(request):
    categories = Category.objects.all()
    
    return dict(links = categories)