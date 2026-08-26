"""
Diagnostico completo de audio do Neymar IA.

Roda FORA do PyCharm (duplo clique ou "python teste_audio.py" no cmd)
para descobrir exatamente qual microfone e qual host de audio (WASAPI,
MME, DirectSound...) funcionam nesse computador/sessao do Windows.

Copie TODA a saida e envie de volta para analise.
"""

import sounddevice as sd

print("=" * 70)
print("DIAGNOSTICO DE AUDIO - NEYMAR IA")
print("=" * 70)

print("\nPortAudio:", sd._libname)

print("\n--- HOST APIS DISPONIVEIS ---")
for i, hostapi in enumerate(sd.query_hostapis()):
    print(f"[{i}] {hostapi['name']}  "
          f"(dispositivo de entrada padrao: {hostapi['default_input_device']})")

print("\n--- TODOS OS DISPOSITIVOS ---")
dispositivos = sd.query_devices()
for i, d in enumerate(dispositivos):
    tipo = []
    if d["max_input_channels"] > 0:
        tipo.append("ENTRADA")
    if d["max_output_channels"] > 0:
        tipo.append("SAIDA")
    print(f"[{i}] {d['name']}  | {'/'.join(tipo) or 'nenhum'} "
          f"| canais_in={d['max_input_channels']} "
          f"| taxa_padrao={d['default_samplerate']} "
          f"| hostapi={d['hostapi']}")

print("\nDispositivo de entrada padrao do sistema (indice):", sd.default.device[0])
print("Dispositivo de saida padrao do sistema (indice):", sd.default.device[1])

print("\n" + "=" * 70)
print("TESTANDO GRAVACAO EM CADA MICROFONE / TAXA")
print("=" * 70)

taxas = [16000, 48000, 44100, 32000, 22050, 8000]

algum_funcionou = False

for i, d in enumerate(dispositivos):
    if d["max_input_channels"] <= 0:
        continue

    print(f"\n>>> Dispositivo [{i}] {d['name']} "
          f"(hostapi: {sd.query_hostapis(d['hostapi'])['name']})")

    for taxa in taxas:
        try:
            audio = sd.rec(
                int(0.5 * taxa),
                samplerate=taxa,
                channels=1,
                dtype="int16",
                device=i,
            )
            sd.wait()
            print(f"    OK  -> {taxa} Hz funcionou! "
                  f"(pico do sinal: {int(abs(audio).max())})")
            algum_funcionou = True
        except Exception as e:
            print(f"    FALHOU -> {taxa} Hz: {type(e).__name__}: {e}")

print("\n" + "=" * 70)
if algum_funcionou:
    print("RESULTADO: pelo menos um dispositivo/taxa funcionou (ver 'OK' acima).")
else:
    print("RESULTADO: NENHUM dispositivo/taxa funcionou nesta sessao.")
print("=" * 70)

input("\nPressione ENTER para fechar...")
