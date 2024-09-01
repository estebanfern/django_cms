#!/bin/sh

python manage.py migrate
python manage.py test

# Verificar si las pruebas pasaron
if [ $? -eq 0 ]; then
    # Si las pruebas pasan, continuar con el release

    # Verificar si se proporcionó un número de versión
    if [ -z "$1" ]; then
        echo "Por favor, proporciona un número de versión. Uso: ./release.sh <versión>"
        exit 1
    fi

    # Crear un tag con la versión proporcionada
    VER=$1
    git tag -a $VER -m "CMS Release $VER"

    # Empujar el tag al repositorio remoto
    git push origin $VER

    echo "Release $VER creado y empujado exitosamente."
else
    echo "Las pruebas fallaron. No se realizará el release."
    exit 1
fi
