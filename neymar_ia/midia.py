import pyautogui


def pausar():
    pyautogui.press("playpause")
    return "Pausando."


def continuar():
    pyautogui.press("playpause")
    return "Continuando."


def proximo():
    pyautogui.press("nexttrack")
    return "Indo para o próximo episódio."


def anterior():
    pyautogui.press("prevtrack")
    return "Voltando para o episódio anterior."


def avancar():
    # A maioria dos players usa a seta direita para avançar
    pyautogui.press("right")
    pyautogui.press("right")
    pyautogui.press("right")
    return "Avançando."


def voltar():
    # A maioria dos players usa a seta esquerda para voltar
    pyautogui.press("left")
    pyautogui.press("left")
    return "Voltando."


def aumentar_volume():
    pyautogui.press("volumeup")
    return "Aumentando o volume."


def diminuir_volume():
    pyautogui.press("volumedown")
    return "Diminuindo o volume."


def mutar():
    pyautogui.press("volumemute")
    return "Mutando o volume."