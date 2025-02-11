# Create_comics_android
Приложение для создания комиксов на андроид


## Инструкция по сборке

1. **Подготовка окружения**:
   - Убедитесь, что у вас установлена Ubuntu версии ниже 20.
   - Распакуйте архив `not_buildet` в выбранную папку.

2. **Установка необходимых зависимостей**:
   Откройте терминал в папке с распакованным проектом и выполните следующие команды:

   ```bash
   sudo apt update
   sudo apt install -y git zip unzip openjdk-17-jdk python3-pip autoconf libtool pkg-config zlib1g-dev libncurses5-dev libncursesw5-dev libtinfo5 cmake libffi-dev libssl-dev
   pip3 install --user --upgrade Cython==0.29.33 virtualenv
   sudo apt install openjdk-17-jdk
   pip3 install --user --upgrade buildozer
   export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
   buildozer -v android debug
    
