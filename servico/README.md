# StreamDock K1 PRO - Serviço Systemd

## Descrição

Serviço systemd que executa o script Python `k1_pro.py`, responsável por
controlar o dispositivo StreamDock K1 PRO no Linux.

A simulação de teclas é feita via `python-evdev`, que injeta eventos de
teclado diretamente no uinput do kernel Linux, sem dependências externas
como xdotool ou ydotool.

### Arquivos

| Arquivo                | Descrição                                              |
|------------------------|--------------------------------------------------------|
| `start_streamdock.sh`  | Wrapper que inicia o `k1_pro.py`                       |
| `streamdock.service`   | Unit file do systemd (serviço de usuário)              |

---

## Pré-requisitos

### 1. Dependências do sistema

```bash
# Python e bibliotecas HID
sudo apt install -y python3 python3-pip libudev-dev libusb-1.0-0-dev libhidapi-libusb0

# pactl (controle de volume — geralmente já instalado)
sudo apt install -y pulseaudio-utils
```

### 2. Dependências Python

```bash
cd Python-SDK
pip install -r requirements.txt
```

> O `requirements.txt` deve incluir `evdev` (simulação de teclas via uinput).

### 3. Permissões de dispositivo

O StreamDock K1 PRO precisa de acesso ao `/dev/hidraw*` e o `python-evdev`
precisa de acesso ao `/dev/uinput`. Crie as regras udev:

```bash
# Regra para o StreamDock (vendor 6603 = K1 PRO)
echo 'KERNEL=="hidraw*", ATTRS{idVendor}=="6603", MODE="0666", GROUP="plugdev"' | \
    sudo tee /etc/udev/rules.d/99-streamdock.rules

# Regra para uinput (python-evdev)
echo 'KERNEL=="uinput", GROUP="input", MODE="0660"' | \
    sudo tee /etc/udev/rules.d/99-uinput.rules

# Recarrega as regras
sudo udevadm control --reload-rules
sudo udevadm trigger
```

### 4. Grupos do usuário

```bash
# Adiciona o usuário ao grupo input (necessário para python-evdev/uinput)
sudo usermod -aG input $USER

# Adiciona o usuário ao grupo plugdev (necessário para hidraw)
sudo usermod -aG plugdev $USER
```

> **Importante:** Faça logout e login novamente para que as mudanças de grupo
> tenham efeito.

---

## Instalação

### Passo 1 — Tornar o script executável

```bash
chmod +x servico/start_streamdock.sh
```

### Passo 2 — Ajustar o caminho no `.service`

Edite `servico/streamdock.service` e substitua o caminho no `ExecStart`
pelo caminho **absoluto** do `start_streamdock.sh` na sua máquina:

```ini
ExecStart=/home/SEU_USUARIO/StreamDock-Device-SDK/servico/start_streamdock.sh
```

### Passo 3 — Copiar o `.service` para o systemd do usuário

```bash
mkdir -p ~/.config/systemd/user
cp servico/streamdock.service ~/.config/systemd/user/
```

### Passo 4 — Recarregar, ativar e iniciar

```bash
# Recarrega as units do systemd
systemctl --user daemon-reload

# Ativa o serviço para iniciar automaticamente no login
systemctl --user enable streamdock.service

# Inicia o serviço agora
systemctl --user start streamdock.service
```

### Passo 5 — Verificar

```bash
systemctl --user status streamdock.service
```

Saída esperada:

```
● streamdock.service - StreamDock K1 PRO Controller
     Loaded: loaded (~/.config/systemd/user/streamdock.service; enabled)
     Active: active (running)
```

---

## Comandos úteis

| Comando | Descrição |
|---------|-----------|
| `systemctl --user start streamdock.service` | Inicia o serviço |
| `systemctl --user stop streamdock.service` | Para o serviço |
| `systemctl --user restart streamdock.service` | Reinicia o serviço |
| `systemctl --user status streamdock.service` | Verifica o status |
| `systemctl --user enable streamdock.service` | Ativa início automático no login |
| `systemctl --user disable streamdock.service` | Desativa início automático |
| `journalctl --user -u streamdock.service -f` | Logs em tempo real |
| `journalctl --user -u streamdock.service --no-pager` | Logs completos |

---

## Desinstalação

```bash
# Para e desativa o serviço
systemctl --user stop streamdock.service
systemctl --user disable streamdock.service

# Remove o arquivo de serviço
rm ~/.config/systemd/user/streamdock.service

# Recarrega o systemd
systemctl --user daemon-reload
```

---

## Solução de problemas

### O serviço não inicia

```bash
# Verifique os logs
journalctl --user -u streamdock.service --no-pager -n 50
```

### "Permission denied" no `/dev/uinput`

O `python-evdev` precisa de acesso ao `/dev/uinput` para injetar eventos
de teclado.

```bash
# Confirme que o usuário está no grupo input
groups $USER | grep input

# Se não estiver, adicione e faça logout/login
sudo usermod -aG input $USER

# Confirme que a regra udev existe
cat /etc/udev/rules.d/99-uinput.rules
```

### "Permission denied" no `/dev/hidraw*`

```bash
# Confirme que a regra udev existe
cat /etc/udev/rules.d/99-streamdock.rules

# Verifique as permissões do dispositivo
ls -la /dev/hidraw*

# Recarregue as regras se necessário
sudo udevadm control --reload-rules
sudo udevadm trigger
```

### Dispositivo não encontrado

```bash
# Verifique se o K1 PRO está conectado via USB
lsusb | grep 6603

# Verifique se o hidraw foi criado
ls -la /dev/hidraw*
```

### Teclas não são enviadas

```bash
# Verifique se /dev/uinput existe e tem permissões corretas
ls -la /dev/uinput

# Teste manualmente via Python
python3 -c "
from evdev import UInput, ecodes
ui = UInput()
ui.write(ecodes.EV_KEY, 30, 1)  # press 'a'
ui.syn()
ui.write(ecodes.EV_KEY, 30, 0)  # release 'a'
ui.syn()
print('OK — tecla a enviada')
"
```

### Variáveis de ambiente da sessão gráfica

O serviço de usuário (`--user`) herda automaticamente `DISPLAY`,
`XDG_RUNTIME_DIR` e `DBUS_SESSION_BUS_ADDRESS` da sessão gráfica.
Se o `pactl` (controle de volume) não funcionar, verifique:

```bash
# Dentro do serviço, as variáveis devem estar definidas
systemctl --user show-environment | grep -E "DISPLAY|XDG_RUNTIME|DBUS"
```
