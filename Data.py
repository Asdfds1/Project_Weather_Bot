import Class_enumeration
import pyowm
import requests
res = requests.Request()



my_own_api_keys = '3312c2119a953eb32f6b08d28ff5fcf3'
token_to_api = '6237774497:AAFm-re6JjGqlNXXSoYw8rHZkIyjcKGPXLo'
owm = pyowm.OWM(my_own_api_keys)
actual_status = Class_enumeration.enumeration.free
city = ''
categories = ['T-shirt/top', 'Trouser', 'Pullover', 'Dress', 'Coat',
              'Sandal', 'Shirt', 'Sneaker', 'Bag', 'Ankle boot']