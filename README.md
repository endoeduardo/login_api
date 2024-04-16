# API LOGIN

Um estudo sobre construção de API usando o Flask.

O projeto consiste em construir uma API que realiza o login de usuários e permite o gerenciamento do banco de usuários, como registrar e deletar usuários.

## Instruções para rodar
- Necessita de ter o docker instalado.

Este comando geralmente funciona sem problemas
```powershell
docker compose up
```

Esse comando força o docker a criar uma imagem nova, as vezes o docker não reconhece que o código fonte foi alterado e não atualiza a imagem já criada.
```powershell
docker compose up --build
```