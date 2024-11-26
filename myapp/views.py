
# Import Django utilities for rendering templates, redirecting URLs, and handling HTTP responses.
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.http import JsonResponse

# Import authentication and authorization utilities to manage user sessions and access control.
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

# Import Django's messaging framework to provide feedback to users about actions (e.g., errors, success messages).
from django.contrib import messages

# Import email utilities to send emails from within Django.
from email.mime.text import MIMEText

# Import Django utilities to manage and manipulate template contexts and content safely.

# Import model and utility functions specific to the application for managing scans and validations.
from myapp.validators import CustomPasswordValidator

# Import standard libraries and third-party libraries for additional functionalities.
import random
import smtplib
import logging

# Import Django's exception classes to handle specific exceptions such as validation errors.
from django.core.exceptions import ValidationError

# Import Django utility to fetch an object from the database or raise a 404 error if not found.
from django.shortcuts import get_object_or_404

from django.db import connection

import os  # Asegúrate de importar el módulo os
from dotenv import load_dotenv


# Set up logging for error tracking and debugging.
logger = logging.getLogger(__name__)
# Cargar las variables de entorno desde el archivo .env


import json
from django.http import JsonResponse
from django.core.files.storage import FileSystemStorage
from PIL import Image
from ultralytics import YOLO
from io import BytesIO
import base64
from django.conf import settings
load_dotenv()
from django.views.decorators.csrf import csrf_exempt


# Views for the application

# View function to handle the home page request. Simply renders the 'home.html' template.
def home(request):
    # Simple view that renders the home page template
    return render(request, 'home.html')

# View function for the 'About' page, rendering the 'about.html' template.
def about(request):
    # Simple view that renders the about page template
    return render(request, 'about.html')

# This handels the registration process of users via form submissions.
def register(request):
    # This check if the form was submitted using POST method.
    if request.method == 'POST':
        # This Extract data from form fields submitted by the user.
        username = request.POST.get('username')
        password = request.POST.get('password1')
        email = request.POST.get('email')
        confirm_password = request.POST.get('password2')
      
        # This validate that all fields contain data.
        if not (username and password and email):
            messages.error(request, "Missing fields in the form.")
            return render(request, 'register.html')

        # Check if passwords match
        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, 'register.html')

        # Initialize and apply custom password validator
        password_validator = CustomPasswordValidator()
        try:
            # This will raise a ValidationError if the password fails any checks
            password_validator.validate(password)
        except ValidationError as e:
            messages.error(request, str(e))
            return render(request, 'register.html')

        # This attempt to create a new user and send a verification email.
        try:
            user = User.objects.create_user(username=username, email=email)
            user.set_password(password)  # This ensures that the password is correctly set & Securely set user's password.
            user.is_active = True  # The user will not be active until they verify their email.
            user.save() # This saves the user object in the database.
            login(request, user) 
            messages.success(request, 'Email verified successfully!')
            return redirect('homekpi')
        
        except Exception as e:
            messages.error(request, f'Registration failed: {e}')
            # If not a POST request, just show the registration form.
            return render(request, 'register.html')
    else:
        return render(request, 'register.html')
  
# Cargar el modelo YOLO
#model = YOLO("model.pt")  # Asegúrate de tener el modelo pt en el directorio adecuado
# Obtener la ruta del modelo en la carpeta estática
#model_path = os.path.join(settings.BASE_DIR, 'myapp','static', 'bestecoseg.pt')
#model = YOLO(model_path)  # Cargar el modelo desde static


@csrf_exempt
def analizar_imagen(request):
    if request.method == 'POST' and 'imagen' in request.FILES:
        model_path = os.path.join(settings.BASE_DIR, 'myapp', 'static', 'bestecoseg.pt')
        model = YOLO(model_path)
        # Usar getlist para obtener todas las imágenes enviadas bajo el mismo Key
        imagenes = request.FILES.getlist('imagen')  
        print(f"Total imágenes recibidas: {len(imagenes)}")  # Verificar cuántas imágenes llegaron

        results_list = []  # Lista para almacenar los resultados de todas las imágenes

        # Iterar sobre todas las imágenes recibidas
        for imagen_file in imagenes:
            print(f"Procesando imagen: {imagen_file.name}")  # Nombre del archivo procesado

            # Leer la imagen en memoria
            img = Image.open(BytesIO(imagen_file.read()))

            # Convertir a RGB si es necesario
            if img.mode != "RGB":
                img = img.convert("RGB")

            # Analizar la imagen con el modelo YOLO
            results = model(img)

            # Extraer detecciones de la imagen
            detections = []
            for result in results:
                for box in result.boxes:
                    xyxy = box.xyxy[0].cpu().numpy()  # Convertir las coordenadas en un array NumPy
                    detections.append({
                        'x_min': float(xyxy[0]),  # Coordenada izquierda
                        'y_min': float(xyxy[1]),  # Coordenada superior
                        'x_max': float(xyxy[2]),  # Coordenada derecha
                        'y_max': float(xyxy[3]),  # Coordenada inferior
                        'confidence': float(box.conf[0]),  # Confianza del modelo
                        'class': int(box.cls[0]),  # Clase detectada
                    })

            # Generar la imagen procesada (con las detecciones dibujadas)
            processed_image = results[0].plot()

            # Convertir la imagen original a base64
            original_buffered = BytesIO()
            img.save(original_buffered, format="JPEG")
            original_img_str = base64.b64encode(original_buffered.getvalue()).decode("utf-8")

            # Convertir la imagen procesada a base64
            processed_buffered = BytesIO()
            img_with_boxes = Image.fromarray(processed_image)
            img_with_boxes.save(processed_buffered, format="JPEG")
            processed_img_str = base64.b64encode(processed_buffered.getvalue()).decode("utf-8")

            # Agregar los resultados de esta imagen a la lista
            results_list.append({
                'detections': detections,
                'original_image': original_img_str,
                'processed_image': processed_img_str,
            })

        # Devolver los resultados de todas las imágenes
        return JsonResponse({'images': results_list})

    else:
        print("No se recibieron imágenes.")  # Indicar si no llegaron imágenes
        return JsonResponse({'error': 'No images provided'}, status=400)

def KPIhome(request):
    return render(request, 'homekpi.html')


STATIC_DATABASE_SCHEMA = """
    Tabla: myapp_persona
      - nombre (CharField)
      - apellidos (CharField)
      - sexo (CharField)
      - fnac (DateField)
      - telefono (CharField)
      - rol (CharField)
      - especialidad (CharField)

    Tabla: myapp_test
      - nombre (CharField)
      - fecha (DateField)
      - fecha_entrega (DateField)
      - estado (CharField)
      - observaciones (TextField)
      - calificacion (IntegerField)
      - categoria (ForeignKey)
      - cliente (ForeignKey)
      - personal (ForeignKey)
      """

    
def execute_sql_query(query):
    try:
        # Ejecutar la consulta SQL generada por la IA
        with connection.cursor() as cursor:
            cursor.execute(query)
            result = cursor.fetchall()  # Obtener los resultados de la consulta
        return result
    except Exception as e:
        print(f"Error al ejecutar la consulta SQL: {e}")
        return None



# this handles the verification of email through a code sent to the user.
def verify_email(request):
    # this checks if the current request method is POST, meansing data has been submitted to the server.
    if request.method == 'POST':
        # Retrieve code from user input and session.
        user_input_code = request.POST.get('code')
        verification_code = request.session.get('verification_code')
        user_id = request.session.get('user_id')

        # this is Logging session and verification data - attempt details for debugging purposes
        logger.info(f"Verifying email: session data - user ID {user_id}, code {verification_code}")

        # this validates that all required information (code, and user ID) is present.
        if not all([user_input_code, verification_code, user_id]):
            messages.error(request, "Missing information required for verification.")
            return redirect('register')

        # Log available users in database for debugging
        users = User.objects.all()
        logger.info(f"Available users: {[user.username for user in users]}")

        try:
            # This attempts to fetch the user based on the user ID stored in the session.
            user = get_object_or_404(User, id=user_id)
            # this checks if the input code matches the session code.
            if user_input_code == str(verification_code):
                user.is_active = True #this marks the user as active (successfull email verification)
                user.save() # this saves the user and updates to the database.
                # this logs the user in automatically after email verification.
                login(request, user) 
                # this clears the session of the verification data to prevent reuse. 
                del request.session['verification_code']
                del request.session['user_id']
                # this then notifies the user of successful email verification and redirect to the 'scanner' view.
                messages.success(request, 'Email verified successfully!')
                return redirect('scanner')
            else:
                # If verification codes do not match, render the verification page with an error.
                messages.error(request, 'Invalid verification code.')
                return render(request, 'verify_email.html')
        except User.DoesNotExist:
            # this handles the case where the user ID does not correspond to any user in the database.
            messages.error(request, "No such user exists.")
            return redirect('register')
        except Exception as e:
            # this catchs all other exceptions and log them, providing a generic error message to the user.
            messages.error(request, f"Error during verification: {e}")
            return render(request, 'verify_email.html')
    else:
        # If the request method is not POST, simply render the email verification page.
        return render(request, 'verify_email.html')


# this function sends a verification email with SMTP protocol.
def send_verification_email(user, verification_code):
    # this checks if the user object has an email attribute that's not empty
    if not user.email:
        # this logs an error if the user object doesn't have an email address
        logger.error("No email address provided for user.")
        # means the user will exit the function returning False (email could not be sent)
        return False

    try:
        # this formats the message string with the verification code included
        message = f'Your verification code is: {verification_code}'
        # this makes a MIMEText object to specify the contents, type, and encoding of the email        
        msg = MIMEText(message, 'plain', 'utf-8')  
        # sets the subject line of the email
        msg['Subject'] = 'Verify Your Email'
        # sets the sender's email address
        msg['From'] = 'proyectostito12@gmail.com'
        # sets the recipient's email address
        msg['To'] = user.email

        # Logging the email details to ensure correctness
        logger.info(f"Email details: From: {msg['From']}, To: {msg['To']}")

        # this is to set up the SMTP server and establish a connection to the SMTP server at the specified address and port
        s = smtplib.SMTP('smtp.gmail.com', 587)
        s.starttls()  # Start TLS for security & Encrypt connection for security.
        s.login('proyectostito12@gmail.com', 'hnovcndqjdatddun')   # Log into the email server.
        s.sendmail(msg['From'], [msg['To']], msg.as_string()) # Send the email.
        s.quit() # this is to terminate the connection to the server.
        # this shows the successful sending of the email
        logger.info(f"Email sent to {user.email} with verification code {verification_code}")
        # this returns True indicating the email was successfully sent
        return True
    except Exception as e:
        # this catchs any exceptions during the email sending process and log an error
        logger.error(f"Failed to send email to {user.email}: {e}")
        # this return False indicating that sending the email failed
        return False

# This handles user login, authenticating credentials against the database.
def user_login(request):
    # This handles user login - checks if the current request is a POST request. 
    # This is necessary because sensitive data such as usernames and passwords 
    # should be sent via POST requests to ensure they are not visible in the URL.
    if request.method == "POST":
        # this retrieves the username and password from the POST request. 
       
        # these are expected to be provided by a login form where users enter their credentials.
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # this Uses Django's built-in `authenticate` method to verify the credentials. 
        # If the credentials are valid, it returns a User object. Otherwise, it returns None.
        user = authenticate(username=username, password=password) # Authenticate user.
        if user:
            # the `login` function from Django's auth module is called with the request and User object. 
            # this officially logs the user into the system, creating the appropriate session data.
            login(request, user) # Log the user in.
            # After successful login, redirect the user to scanner page. 
            #Here it redirects to a page named 'scanner'.
            return redirect('homekpi')
        else:
            
            # If authentication fails, display an error message and redirect back to the login form.            
            return render(request, 'login.html', {'error': 'Bad credentials, please try again'}, status=200)
    return render(request, 'login.html')

 
def custom_404(request, exception):
    return render(request, '404.html', status=404)


# logs out the user and redirects them to the home page.
def signout(request):
    # Handles user logout and redirects to home page
    logout(request) # uses logout function to terminate the user session.
    return redirect('home') # after logging out, redirect the user to the home page.

