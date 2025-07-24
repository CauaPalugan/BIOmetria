const video = document.getElementById('videoElement');
const canvas = document.getElementById('canvas');
const captureBtn = document.getElementById('captureBtn');
const capturedImage = document.getElementById('capturedImage');
const imagemBase64Input = document.getElementById('imagemBase64Input');
const loginForm = document.getElementById('loginForm'); // Referência ao novo formulário
const messageDiv = document.getElementById('message');

// Pedir permissão para acessar a webcam
navigator.mediaDevices.getUserMedia({ video: true })
    .then(function(stream) {
        video.srcObject = stream;
        video.play();
    })
    .catch(function(err) {
        console.error("Erro ao acessar a webcam: " + err);
        messageDiv.textContent = "Erro ao acessar a webcam. Por favor, verifique as permissões.";
        messageDiv.classList.add('text-danger');
    });

captureBtn.addEventListener('click', function() {
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    canvas.getContext('2d').drawImage(video, 0, 0, canvas.width, canvas.height);

    const imageDataURL = canvas.toDataURL('image/jpeg', 0.9);
    capturedImage.src = imageDataURL;
    capturedImage.style.display = 'block';

    imagemBase64Input.value = imageDataURL;
    messageDiv.textContent = "Imagem capturada! Clique em Entrar para validar.";
    messageDiv.classList.remove('text-success', 'text-danger');
});

loginForm.addEventListener('submit', function(event) {
    event.preventDefault();

    if (!imagemBase64Input.value) {
        messageDiv.textContent = "Por favor, capture uma imagem para realizar o login biométrico.";
        messageDiv.classList.add('text-danger');
        return;
    }

    messageDiv.textContent = "Validando biometria...";
    messageDiv.classList.remove('text-success', 'text-danger');

    const formData = new FormData(loginForm);

    fetch(loginForm.action, {
        method: 'POST',
        body: formData,
    })
    .then(response => {
        const contentType = response.headers.get("content-type");
        if (contentType && contentType.indexOf("application/json") !== -1) {
            return response.json();
        } else {
            throw new Error('Resposta não é JSON. Verifique o console do servidor Django.');
        }
    })
    .then(data => {
        messageDiv.textContent = data.message;
        if (data.status === 'success') {
            messageDiv.classList.add('text-success');
            console.log("Login Biométrico Sucesso:", data);
            // Redirecionar para a página inicial ou dashboard após o login
            window.location.href = data.redirect_url || '/'; // Redireciona para / ou o que vier do backend
        } else {
            messageDiv.classList.add('text-danger');
            console.error("Login Biométrico Erro:", data);
        }
    })
    .catch(error => {
        console.error('Erro na requisição de login:', error);
        messageDiv.textContent = "Erro na comunicação com o servidor ou resposta inválida.";
        messageDiv.classList.add('text-danger');
    });
});