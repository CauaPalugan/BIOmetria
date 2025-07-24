const video = document.getElementById('videoElement');
const canvas = document.getElementById('canvas');
const captureBtn = document.getElementById('captureBtn');
const capturedImage = document.getElementById('capturedImage');
const imagemBase64Input = document.getElementById('imagemBase64Input');
const cadastroForm = document.getElementById('cadastroForm');
const messageDiv = document.getElementById('message');

// Pedir permissão para acessar a webcam
navigator.mediaDevices.getUserMedia({ video: true })
    .then(function(stream) {
        video.srcObject = stream;
        video.play(); // Iniciar a reprodução do vídeo
    })
    .catch(function(err) {
        console.error("Erro ao acessar a webcam: " + err);
        messageDiv.textContent = "Erro ao acessar a webcam. Por favor, verifique as permissões.";
        messageDiv.classList.add('text-danger');
    });

captureBtn.addEventListener('click', function() {
    // Desenhar o frame atual do vídeo no canvas
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    canvas.getContext('2d').drawImage(video, 0, 0, canvas.width, canvas.height);

    // Obter a imagem em Base64
    const imageDataURL = canvas.toDataURL('image/jpeg', 0.9); // Qualidade 0.9
    capturedImage.src = imageDataURL;
    capturedImage.style.display = 'block';

    // Preencher o campo hidden do formulário
    imagemBase64Input.value = imageDataURL;
    messageDiv.textContent = "Imagem capturada! Preencha os dados e clique em Cadastrar.";
    messageDiv.classList.remove('text-success', 'text-danger'); // Remove classes de sucesso/erro
});

cadastroForm.addEventListener('submit', function(event) {
    event.preventDefault(); 

    messageDiv.textContent = "Enviando dados...";
    messageDiv.classList.remove('text-success', 'text-danger'); 

    const formData = new FormData(cadastroForm);
    // FormData automaticamente pega os valores dos inputs do formulário

    fetch(cadastroForm.action, {
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
            console.log("Sucesso:", data);
            cadastroForm.reset(); 
            capturedImage.style.display = 'none'; 
            imagemBase64Input.value = ''; 
        } else {
            messageDiv.classList.add('text-danger'); 
            console.error("Erro:", data);
        }
    })
    .catch(error => {
        console.error('Erro na requisição:', error);
        messageDiv.textContent = "Erro na comunicação com o servidor ou resposta inválida.";
        messageDiv.classList.add('text-danger');
    });
});