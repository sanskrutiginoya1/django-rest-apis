from django.apps import AppConfig

class GetcolumnsConfig(AppConfig): # create a class for the app config 
    default_auto_field = 'django.db.models.BigAutoField' # set the default auto field
    name = 'getColumns'
