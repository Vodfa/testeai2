# Trader IA (estilo Freqtrade)

Aplicativo desktop em Python com GUI para:

- Configurar parâmetros da estratégia (par, timeframe, threshold, valor etc.).
- Rodar uma IA heurística para prever chance de alta do preço.
- Abrir a corretora em navegador embutido para automação de trade.
- Definir tempo máximo de execução da IA.
- Rodar em modo **dry-run** (simulação) para validação segura.

> ⚠️ Aviso: este projeto é educacional e não garante lucro.

## Requisitos

- Python 3.11+
- Windows (para gerar `.exe`) ou Linux/macOS para desenvolvimento

## Instalação e ambiente virtual

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows
pip install -r requirements.txt
```

## Execução

```bash
python -m app.main
```

## Testes

```bash
python -m unittest discover -s tests -v
```

## Como gerar `.exe` (Windows)

### Opção 1: comando direto

```bash
pyinstaller --noconfirm --windowed --name trader_ia --collect-all PySide6 app/main.py
```

O executável será criado em `dist/trader_ia.exe`.

### Opção 2: arquivo `.bat`

Crie `build_windows.bat` com:

```bat
@echo off
pyinstaller --noconfirm --windowed --name trader_ia --collect-all PySide6 app/main.py
echo Build finalizado. Arquivo em dist\trader_ia.exe
```

## Observações sobre trade automático

- Em `dry-run`, o app só simula ordens no log.
- Em modo real, o app executa um script JS simples para tentar clicar em botão da página.
- Cada corretora pode ter HTML diferente; talvez seja necessário ajustar seletores.
