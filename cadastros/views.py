import base64
import numpy as np
import cv2
import os
from django.shortcuts import render, redirect 
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from .models import PerfilUsuario
from django.conf import settings
from django.contrib.auth import login, logout 
from django.contrib.auth.decorators import login_required 


# --- VARIÁVEIS PARA CARREGAR OS MODELOS DO OPENCV ---
MODELS_DIR = os.path.join(settings.BASE_DIR, 'modelsOpenCV')

FACE_DETECTOR_MODEL_PROTOTXT = os.path.join(MODELS_DIR, 'deploy.prototxt')
FACE_DETECTOR_MODEL_CAFFEMODEL = os.path.join(MODELS_DIR, 'res10_300x300_ssd_iter_140000.caffemodel')

FACE_RECOGNIZER_MODEL_T7 = os.path.join(MODELS_DIR, 'openface.nn4.small2.v1.t7')

net_detector = None
net_recognizer = None

try:
    net_detector = cv2.dnn.readNetFromCaffe(FACE_DETECTOR_MODEL_PROTOTXT, FACE_DETECTOR_MODEL_CAFFEMODEL)
    net_recognizer = cv2.dnn.readNetFromTorch(FACE_RECOGNIZER_MODEL_T7)
    print("Modelos de detecção e reconhecimento facial do OpenCV carregados com sucesso.")
except Exception as e:
    print(f"ERRO CRÍTICO ao carregar modelos do OpenCV: {e}")
    print("Verifique se os arquivos de modelo estão na pasta 'modelsOpenCV' na raiz do projeto e não estão corrompidos.")
    print(f"Caminhos esperados: {FACE_DETECTOR_MODEL_PROTOTXT}, {FACE_DETECTOR_MODEL_CAFFEMODEL}, {FACE_RECOGNIZER_MODEL_T7}")

# Função auxiliar para verificar permissão de cargo
def check_cargo_permission(user, required_roles):
    if not user.is_authenticated:
        return False
    try:
        # Pega o cargo do PerfilUsuario
        user_cargo = user.perfilusuario.cargo
        return user_cargo in required_roles
    except PerfilUsuario.DoesNotExist:
        return False

@csrf_exempt
def cadastrar_biometria(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        name = request.POST.get('name')
        cargo = request.POST.get('cargo')
        imagem_base64 = request.POST.get('imagem_base64')

        print(f"Recebido username: {username}")
        print(f"Recebido nome: {name}")
        print(f"Recebido cargo: {cargo}")
        print(f"Tamanho da imagem_base64 recebida: {len(imagem_base64) if imagem_base64 else '0'} bytes")

        # --- Validações ---
        if not all([username, password, password2, name, cargo]):
            return JsonResponse({'status': 'error', 'message': 'Por favor, preencha todos os campos obrigatórios.'})

        if password != password2:
            return JsonResponse({'status': 'error', 'message': 'As senhas não coincidem.'})

        if User.objects.filter(username=username).exists():
            return JsonResponse({'status': 'error', 'message': 'Nome de usuário já existe.'})

        face_encoding = None 

        # Processamento da biometria apenas se uma imagem foi enviada
        if imagem_base64:
            if net_detector is None or net_recognizer is None:
                return JsonResponse({'status': 'error', 'message': 'Erro interno do servidor: Modelos de reconhecimento facial não carregados. Não foi possível processar a biometria.'})
            try:
                format, imgstr = imagem_base64.split(';base64,')
                decoded_image = base64.b64decode(imgstr)
                np_array = np.frombuffer(decoded_image, np.uint8)
                img_np = cv2.imdecode(np_array, cv2.IMREAD_COLOR)

                if img_np is None:
                    return JsonResponse({'status': 'error', 'message': 'Não foi possível decodificar a imagem biométrica. Formato inválido?'})

                (h, w) = img_np.shape[:2]
                blob = cv2.dnn.blobFromImage(cv2.resize(img_np, (300, 300)), 1.0, (300, 300), (104.0, 177.0, 123.0))

                net_detector.setInput(blob)
                detections = net_detector.forward()

                face_detected = False
                for i in range(0, detections.shape[2]):
                    confidence = detections[0, 0, i, 2]

                    if confidence > 0.5:
                        box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                        (startX, startY, endX, endY) = box.astype("int")

                        face = img_np[startY:endY, startX:endX]
                        (fH, fW) = face.shape[:2]

                        if fW < 20 or fH < 20:
                            continue

                        face_blob = cv2.dnn.blobFromImage(face, 1.0 / 255, (96, 96), (0, 0, 0), swapRB=True, crop=False)
                        net_recognizer.setInput(face_blob)
                        vec = net_recognizer.forward()

                        face_encoding = vec.flatten().tobytes()
                        face_detected = True
                        break

                if not face_detected:
                    return JsonResponse({'status': 'error', 'message': 'Nenhum rosto detectado na imagem biométrica ou rosto muito pequeno. Tente novamente com boa iluminação e centralize o rosto.'})

            except Exception as e:
                print(f"Erro ao processar imagem biométrica: {e}")
                return JsonResponse({'status': 'error', 'message': f'Erro ao processar a imagem biométrica: {str(e)}'})

        # Se chegou até aqui, os dados básicos são válidos e a biometria foi processada
        try:
            user = User.objects.create_user(username=username, password=password)
            PerfilUsuario.objects.create(
                usuario=user,
                name=name,
                cargo=cargo,
                dados_biometricos=face_encoding
            )

            print("Usuário, biometria, nome e cargo cadastrados com sucesso!")
            return JsonResponse({'status': 'success', 'message': 'Cadastro realizado com sucesso!'})

        except Exception as e:
            print(f"Erro ao salvar usuário no banco de dados: {e}")
            return JsonResponse({'status': 'error', 'message': f'Erro interno ao cadastrar usuário: {str(e)}'})

    return render(request, 'cadastro.html')

@csrf_exempt
def validar_biometria(request):
    if request.method == 'POST':
        imagem_base64 = request.POST.get('imagem_base64')

        if not imagem_base64:
            return JsonResponse({'status': 'error', 'message': 'Nenhuma imagem enviada para validação.'})

        if net_detector is None or net_recognizer is None:
            return JsonResponse({'status': 'error', 'message': 'Erro interno do servidor: Modelos de reconhecimento facial não carregados.'})

        try:
            format, imgstr = imagem_base64.split(';base64,')
            decoded_image = base64.b64decode(imgstr)
            np_array = np.frombuffer(decoded_image, np.uint8)
            img_np = cv2.imdecode(np_array, cv2.IMREAD_COLOR)

            if img_np is None:
                return JsonResponse({'status': 'error', 'message': 'Não foi possível decodificar a imagem de login.'})

            (h, w) = img_np.shape[:2]
            blob = cv2.dnn.blobFromImage(cv2.resize(img_np, (300, 300)), 1.0, (300, 300), (104.0, 177.0, 123.0))

            net_detector.setInput(blob)
            detections = net_detector.forward()

            login_face_encoding = None
            for i in range(0, detections.shape[2]):
                confidence = detections[0, 0, i, 2]
                if confidence > 0.5:
                    box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                    (startX, startY, endX, endY) = box.astype("int")

                    face = img_np[startY:endY, startX:endX]
                    (fH, fW) = face.shape[:2]
                    if fW < 20 or fH < 20:
                        continue

                    face_blob = cv2.dnn.blobFromImage(face, 1.0 / 255, (96, 96), (0, 0, 0), swapRB=True, crop=False)
                    net_recognizer.setInput(face_blob)
                    vec = net_recognizer.forward()
                    login_face_encoding = vec.flatten() # Manter como numpy array para comparação
                    break

            if login_face_encoding is None:
                return JsonResponse({'status': 'error', 'message': 'Nenhum rosto detectado na imagem de login. Tente novamente.'})

            # --- Lógica de Comparação dos Embeddings ---
            # Percorrer todos os perfis de usuário com biometria cadastrada
            # .select_related('usuario') faz um JOIN para carregar o objeto User junto, evitando N+1 queries
            perfis_com_biometria = PerfilUsuario.objects.exclude(dados_biometricos__isnull=True).select_related('usuario')

            SIMILARITY_THRESHOLD = 0.65

            for perfil in perfis_com_biometria:
                # Converter os dados_biometricos do BD de volta para numpy array
                stored_encoding = np.frombuffer(perfil.dados_biometricos, dtype=np.float32)

                distance = np.linalg.norm(login_face_encoding - stored_encoding)

                # Usar perfil.usuario.username para garantir que o objeto User foi carregado
                print(f"Comparando com {perfil.usuario.username}: Distância = {distance:.4f}")

                if distance < SIMILARITY_THRESHOLD:
                    user = perfil.usuario
                    login(request, user)
                    print(f"Login bem-sucedido para o usuário: {user.username}")
                    return JsonResponse({'status': 'success', 'message': 'Login biométrico bem-sucedido!', 'redirect_url': '/dashboard/'})

            return JsonResponse({'status': 'error', 'message': 'Rosto não reconhecido. Por favor, tente novamente ou cadastre-se.'})

        except Exception as e:
            print(f"Erro no processo de validação biométrica: {e}")
            return JsonResponse({'status': 'error', 'message': f'Erro interno no servidor: {str(e)}'})

    return render(request, 'validacao.html')

@login_required(login_url='/cadastros/validacao/') 
def dashboard_view(request):
    return render(request, 'dashboard.html')

@login_required(login_url='/cadastros/validacao/')
def monitoramento_basico_view(request):
    return render(request, 'monitoramento_basico.html')

@login_required(login_url='/cadastros/validacao/')
def analise_detalhada_view(request):
    if check_cargo_permission(request.user, ['analista', 'coordenador']):
        return render(request, 'analise_detalhada.html')
    else:
        return HttpResponse("Acesso Negado: Você não tem permissão para acessar esta página.", status=403)

@login_required(login_url='/cadastros/validacao/')
def gerenciamento_projetos_view(request):
    if check_cargo_permission(request.user, ['coordenador']):
        return render(request, 'gerenciamento_projetos.html')
    else:
        return HttpResponse("Acesso Negado: Esta página é exclusiva para Coordenadores.", status=403)

@login_required(login_url='/cadastros/validacao/') 
def user_logout(request):
    logout(request)
    return redirect('validar_biometria') 