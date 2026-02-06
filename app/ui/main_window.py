from __future__ import annotations

from datetime import datetime

from PySide6.QtCore import QTimer, QUrl
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import (
    QCheckBox,
    QDoubleSpinBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QPlainTextEdit,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from app.core.bot import BotConfig, TradingBotEngine
from app.core.freqtrade_data import DEFAULT_FREQTRADE_TRADES_URL, FreqtradeDataAnalyzer


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Trader IA - Estilo Freqtrade")
        self.resize(1200, 700)

        self.bot: TradingBotEngine | None = None
        self.freqtrade_baseline_bias = 0.0
        self.freqtrade_analyzer = FreqtradeDataAnalyzer()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._on_tick)

        central = QWidget()
        self.setCentralWidget(central)
        root = QHBoxLayout(central)

        # Left side controls
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        form = QFormLayout()

        self.symbol_input = QLineEdit("BTCUSDT")
        self.interval_input = QLineEdit("5m")
        self.candle_limit_input = QSpinBox()
        self.candle_limit_input.setRange(30, 1000)
        self.candle_limit_input.setValue(200)

        self.threshold_input = QDoubleSpinBox()
        self.threshold_input.setRange(0.0, 1.0)
        self.threshold_input.setSingleStep(0.01)
        self.threshold_input.setValue(0.62)

        self.poll_seconds_input = QSpinBox()
        self.poll_seconds_input.setRange(5, 3600)
        self.poll_seconds_input.setValue(30)

        self.amount_input = QDoubleSpinBox()
        self.amount_input.setRange(1, 1_000_000)
        self.amount_input.setValue(50)

        self.runtime_limit_input = QSpinBox()
        self.runtime_limit_input.setRange(0, 10_000)
        self.runtime_limit_input.setValue(0)
        self.runtime_limit_label = QLabel("(0 = sem limite)")

        self.trade_url_input = QLineEdit("https://www.binance.com/en/trade/BTC_USDT")
        self.freqtrade_url_input = QLineEdit(DEFAULT_FREQTRADE_TRADES_URL)

        self.dry_run_check = QCheckBox("Dry-run (não envia ordem real)")
        self.dry_run_check.setChecked(True)

        form.addRow("Par:", self.symbol_input)
        form.addRow("Timeframe:", self.interval_input)
        form.addRow("Qtd candles:", self.candle_limit_input)
        form.addRow("Threshold compra:", self.threshold_input)
        form.addRow("Intervalo de análise (s):", self.poll_seconds_input)
        form.addRow("Valor por ordem:", self.amount_input)
        form.addRow("Tempo máximo (min):", self.runtime_limit_input)
        form.addRow("", self.runtime_limit_label)
        form.addRow("URL da corretora:", self.trade_url_input)
        form.addRow("URL dataset Freqtrade:", self.freqtrade_url_input)
        form.addRow("", self.dry_run_check)

        left_layout.addLayout(form)

        buttons_layout = QHBoxLayout()
        self.start_btn = QPushButton("Iniciar IA")
        self.stop_btn = QPushButton("Parar IA")
        self.stop_btn.setEnabled(False)
        self.load_browser_btn = QPushButton("Carregar Corretora")
        self.load_freqtrade_btn = QPushButton("Carregar baseline Freqtrade")
        buttons_layout.addWidget(self.start_btn)
        buttons_layout.addWidget(self.stop_btn)
        buttons_layout.addWidget(self.load_browser_btn)
        buttons_layout.addWidget(self.load_freqtrade_btn)
        left_layout.addLayout(buttons_layout)

        self.log = QPlainTextEdit()
        self.log.setReadOnly(True)
        left_layout.addWidget(self.log)

        # Right side embedded browser
        self.browser = QWebEngineView()

        root.addWidget(left_widget, 1)
        root.addWidget(self.browser, 2)

        self.start_btn.clicked.connect(self.start_bot)
        self.stop_btn.clicked.connect(self.stop_bot)
        self.load_browser_btn.clicked.connect(self.load_broker)
        self.load_freqtrade_btn.clicked.connect(self.load_freqtrade_baseline)

    def _append_log(self, message: str) -> None:
        stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.log.appendPlainText(f"[{stamp}] {message}")

    def load_broker(self) -> None:
        self.browser.setUrl(QUrl(self.trade_url_input.text()))
        self._append_log("Corretora carregada no navegador embutido.")

    def load_freqtrade_baseline(self) -> None:
        try:
            trades = self.freqtrade_analyzer.load_trades_from_github(self.freqtrade_url_input.text().strip())
            baseline = self.freqtrade_analyzer.build_baseline(trades)
            self.freqtrade_baseline_bias = baseline.market_bias
            self._append_log(
                "Baseline Freqtrade carregada: "
                f"trades={baseline.total_trades}, winrate={baseline.win_rate:.2%}, "
                f"expectancy={baseline.expectancy:.4f}, bias={baseline.market_bias:+.3f}"
            )
        except Exception as exc:
            self._append_log(f"Falha ao carregar baseline Freqtrade: {exc}")

    def start_bot(self) -> None:
        try:
            config = BotConfig(
                symbol=self.symbol_input.text().strip().upper(),
                interval=self.interval_input.text().strip(),
                candle_limit=self.candle_limit_input.value(),
                buy_threshold=self.threshold_input.value(),
                poll_seconds=self.poll_seconds_input.value(),
                trade_amount=self.amount_input.value(),
                dry_run=self.dry_run_check.isChecked(),
                max_runtime_minutes=self.runtime_limit_input.value(),
                market_bias=self.freqtrade_baseline_bias,
            )
            self.bot = TradingBotEngine(config, self._append_log, self.execute_trade)
            self.bot.start()
            self.timer.start(config.poll_seconds * 1000)
            self.start_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)
            self._append_log("Loop de análise iniciado.")
        except Exception as exc:
            QMessageBox.critical(self, "Erro ao iniciar", str(exc))

    def stop_bot(self) -> None:
        if self.bot:
            self.bot.stop()
        self.timer.stop()
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self._append_log("Loop de análise encerrado.")

    def _on_tick(self) -> None:
        if not self.bot:
            return
        try:
            self.bot.tick()
            if not self.bot.running:
                self.stop_bot()
        except Exception as exc:
            self._append_log(f"Falha no ciclo: {exc}")

    def execute_trade(self, symbol: str, amount: float, dry_run: bool) -> None:
        if dry_run:
            self._append_log(f"[DRY-RUN] Compra simulada: {symbol} com valor {amount:.2f}")
            return

        script = """
            const buyButton = document.querySelector('button[type="button"], button');
            if (buyButton) { buyButton.click(); true; } else { false; }
        """

        def on_js_done(result: bool) -> None:
            if result:
                self._append_log(f"Ordem de compra enviada para {symbol} (valor aprox. {amount:.2f}).")
            else:
                self._append_log("Não foi possível localizar botão de compra automaticamente.")

        self.browser.page().runJavaScript(script, on_js_done)
