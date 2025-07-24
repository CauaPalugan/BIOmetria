const video = document.getElementById('videoElement');
const canvas = document.getElementById('canvas');
const captureBtn = document.getElementById('captureBtn');
const capturedImage = document.getElementById('capturedImage');
const imagemBase64Input = document.getElementById('imagemBase64Input');
const cadastroForm = document.getElementById('cadastroForm');
const messageDiv = document.getElementById('message'); // Div onde as mensagens serão exibidas

// Pedir permissão para acessar a webcam
navigator.mediaDevices.getUserMedia({ video: true })
    .then(function(stream) {
        video.srcObject = stream;
        video.play(); // Iniciar a reprodução do vídeo
    })
    .catch(function(err) {
        console.error("Erro ao acessar a webcam: " + err);
        messageDiv.textContent = "Erro ao acessar a webcam. Por favor, verifique as permissões.";
        messageDiv.classList.add('text-danger'); // Usa classe do Bootstrap para erro
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
    event.preventDefault(); // Impedir o envio padrão do formulário

    // A biometria é opcional, então não precisa verificar imagemBase64Input.value aqui.
    // A validação de campos obrigatórios será feita no backend.

    messageDiv.textContent = "Enviando dados...";
    messageDiv.classList.remove('text-success', 'text-danger'); // Limpa classes anteriores

    const formData = new FormData(cadastroForm);
    // FormData automaticamente pega os valores dos inputs do formulário

    fetch(cadastroForm.action, {
        method: 'POST',
        body: formData,
    })
    .then(response => {
        // Verifica se a resposta é JSON antes de tentar parsing
        const contentType = response.headers.get("content-type");
        if (contentType && contentType.indexOf("application/json") !== -1) {
            return response.json();
        } else {
            // Se não for JSON, algo inesperado aconteceu no backend (ex: erro 500 sem JSON)
            throw new Error('Resposta não é JSON. Verifique o console do servidor Django.');
        }
    })
    .then(data => {
        messageDiv.textContent = data.message; // Exibe a mensagem do backend
        if (data.status === 'success') {
            messageDiv.classList.add('text-success'); // Adiciona classe Bootstrap de sucesso
            console.log("Sucesso:", data);
            // Você pode redirecionar ou limpar o formulário aqui
            // window.location.href = '/cadastros/validacao/';
            cadastroForm.reset(); // Limpa o formulário após o sucesso
            capturedImage.style.display = 'none'; // Esconde a imagem capturada
            imagemBase64Input.value = ''; // Limpa o input hidden
        } else {
            messageDiv.classList.add('text-danger'); // Adiciona classe Bootstrap de erro
            console.error("Erro:", data);
        }
    })
    .catch(error => {
        console.error('Erro na requisição:', error);
        messageDiv.textContent = "Erro na comunicação com o servidor ou resposta inválida.";
        messageDiv.classList.add('text-danger');
    });
});