WillowBot-Draynor (Human-like)

Requisitos

- Python 3.9+
- Windows 10/11
- Bibliotecas: opencv-python, numpy, pyautogui, pillow, pynput, keyboard

Instalação

- python -m pip install opencv-python numpy pyautogui pillow pynput keyboard

Estrutura

- core/: movement, vision, actions, behavior, dashboard, scheduler, window
- strategies/: generic_chop_and_bank.py
- configs/: JSONs data-driven por localização/skill
- assets/: templates (trees/, banks/, ui/)
- logs/: sessões e scheduler

Execução

- Adicione templates reais em assets/ conforme seu cliente OSRS.
- Execute diretamente:
- python main.py
- Ou especifique um JSON:
- python main.py --config configs/draynor_willows.json

Detecção de Janela e Resolução

- O bot detecta automaticamente a janela ativa do cliente OSRS.
- Todos os ROIs e waypoints são relativos à janela, funcionando em qualquer resolução.
- Matching usa múltiplas escalas de template para robustez.

Configuração (exemplo reduzido)

- {
-   "location": "Draynor Village",
-   "tree_type": "Willow",
-   "tree_templates": ["assets/trees/willow_*.png"],
-   "tree_search_region": [0.05, 0.05, 0.5, 0.5],
-   "bank_waypoints": [[0.39, 0.39], [0.37, 0.42], [0.36, 0.45]],
-   "return_waypoints": [[0.34, 0.46], [0.35, 0.44]],
-   "mouse_profile": "natural_curved",
-   "template_scales": [0.9, 1.0, 1.1]
- }

Parada de Emergência

- Feche a janela do cliente ou interrompa o processo do Python.

Observações

- Ajuste thresholds no JSON conforme seus templates/skins.
- Overlay simples exibe status e contador de logs; expandir conforme necessidade.
