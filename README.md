# BIOmetria - Sistema de Autenticação Facial com Controle de Acesso por Cargo

## 🚀 Sobre o Projeto

O BIOmetria é um sistema web desenvolvido em Django que implementa método de autenticação biométrica facial, utilizando a inteligência de modelos OpenCV. Além da segurança no login, o projeto oferece um controle de acesso baseado no cargo do usuário, garantindo que diferentes níveis de hierarquia (Estagiário, Analista e Coordenador) tenham permissão para acessar funcionalidades específicas do sistema.

Este projeto faz parte de um trabalho acadêmico com foco na aplicação de tecnologias de visão computacional e gerenciamento de permissões em um contexto de sistema de informação, utilizando o tema de **Meio Ambiente** para contextualizar as funcionalidades.

## ✨ Funcionalidades Principais

* **Cadastro de Usuários com Biometria Facial:** Os usuários podem se registrar no sistema capturando uma imagem facial que é processada para extrair um "embedding" (vetor numérico de características faciais).
* **Login Biométrico Facial:** A autenticação é realizada comparando a imagem facial capturada no momento do login com os dados biométricos armazenados, utilizando um algoritmo de distância euclidiana para verificar a similaridade.
* **Controle de Acesso por Cargo:**
    * **Todos os Usuários (Estagiário, Analista, Coordenador):** Acesso ao Dashboard geral e à tela de Monitoramento Básico.
    * **Analistas e Coordenadores:** Acesso a ferramentas e relatórios de Análise Detalhada.
    * **Coordenadores:** Acesso exclusivo a funcionalidades críticas de Gerenciamento de Projetos.
* **Páginas Temáticas:** Telas de exemplo com foco em monitoramento e gestão ambiental.
* **Sistema de Logout:** Funcionalidade para encerrar a sessão do usuário.

## 🛠️ Tecnologias Utilizadas

* **Backend:** Python 3.x, Django
* **Frontend:** HTML5, CSS3, JavaScript
* **Estilização:** Bootstrap 5
* **Biometria/Visão Computacional:** OpenCV (com modelos DNN pré-treinados para detecção e reconhecimento facial)
* **Banco de Dados:** SQLite3 (padrão do Django para desenvolvimento)
