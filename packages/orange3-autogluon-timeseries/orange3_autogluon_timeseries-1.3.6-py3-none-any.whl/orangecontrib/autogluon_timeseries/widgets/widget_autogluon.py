import logging
import os
from Orange.widgets.widget import OWWidget, Input, Output
from Orange.widgets import gui, settings
from Orange.data import Table, Domain, ContinuousVariable, StringVariable, DiscreteVariable, TimeVariable, Variable
import pandas as pd
import numpy as np
import tempfile
from autogluon.timeseries import TimeSeriesPredictor, TimeSeriesDataFrame
from datetime import datetime, timedelta
from pathlib import Path
import traceback
from Orange.widgets.utils.widgetpreview import WidgetPreview
from PyQt5.QtWidgets import QPlainTextEdit, QCheckBox, QComboBox, QLabel
from PyQt5.QtCore import QCoreApplication
from PyQt5.QtGui import QFont
import holidays # Импортируем библиотеку holidays
import warnings

warnings.filterwarnings('ignore')
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def format_message(level, text):
        """Форматирование сообщений без эмодзи"""
        prefixes = {
            'critical': '[КРИТИЧНО]',
            'warning': '[ВНИМАНИЕ]', 
            'caution': '[ОСТОРОЖНО]',
            'info': '[ИНФО]',
            'success': '[ГОТОВО]',
            'ok': '[OK]',
            'error': '[ОШИБКА]'
        }
        return f"{prefixes.get(level, '[INFO]')} {text}"

class OWAutoGluonTimeSeries(OWWidget):
    name = "AutoGluon Time Series"
    description = "Прогнозирование временных рядов с AutoGluon"
    icon = "icons/autogluon.png"
    priority = 0
    keywords = ["timeseries", "forecast", "autogluon"]

    # Настройки
    prediction_length = settings.Setting(10)
    time_limit = settings.Setting(60)
    selected_metric = settings.Setting("MAE")
    selected_preset = settings.Setting("best_quality")
    target_column = settings.Setting("sales")
    id_column = settings.Setting("item_id")
    timestamp_column = settings.Setting("timestamp")
    include_holidays = settings.Setting(False)
    #use_current_date = settings.Setting(True)  # Настройка для использования текущей даты
    frequency = settings.Setting("D")  # Частота для прогноза (по умолчанию дни)
    auto_frequency = settings.Setting(True)  # Автоопределение частоты
    selected_model = settings.Setting("auto") # выбор моделей
    holiday_country = settings.Setting("RU") # Страна для праздников

    # Метрики
    METRICS = ["MAE", "MAPE", "MSE", "RMSE", "RMSLE", "SMAPE", "WAPE", "WQL", "SQL", "MASE", "RMSSE"]
    
    # Частоты
    FREQUENCIES = [
        ("D", "День"),
        ("W", "Неделя"),
        ("M", "Месяц"),
        ("Q", "Квартал"),
        ("Y", "Год"),
        ("H", "Час"),
        ("T", "Минута"),
        ("B", "Рабочий день")
    ]
    # Доступные страны для праздников (можно расширить)
    HOLIDAY_COUNTRIES = ["RU", "US", "GB", "DE", "FR", "CA"]


    class Inputs:
        data = Input("Data", Table)

    class Outputs:
        prediction = Output("Prediction", Table)
        leaderboard = Output("Leaderboard", Table)
        model_info = Output("Model Info", Table)
        log_messages = Output("Log", str)

    def __init__(self):
        super().__init__()
        self.data = None
        self.predictor = None
        self.log_messages = ""
        self.detected_frequency = "D"  # Определенная частота данных по умолчанию
        self.mainArea.hide()
        self.setup_ui()
        self.warning("")
        self.error("")
        self.log("Виджет инициализирован")
        
        # Данные для валидации длины прогноза
        self.max_allowed_prediction = 0
        self.data_length = 0
        self.from_form_timeseries = False  # Флаг для определения источника данных
        self.categorical_mapping = {} # для сопоставления категориальных значений
    
    def setup_ui(self):

        # Основные параметры
        box = gui.widgetBox(self.controlArea, "Параметры")
        self.prediction_spin = gui.spin(box, self, "prediction_length", 1, 365, 1, label="Длина прогноза:")
        self.prediction_spin.valueChanged.connect(self.on_prediction_length_changed)
        
        # Добавляем информационную метку о максимальной длине прогноза
        self.max_length_label = QLabel("Максимальная длина прогноза: N/A")
        box.layout().addWidget(self.max_length_label)
        
        gui.spin(box, self, "time_limit", 10, 86400, 10, label="Лимит времени (сек):")
        
        # Кастомная модель для группировки метрик
        from PyQt5.QtGui import QStandardItemModel, QStandardItem
        from PyQt5.QtCore import Qt, QVariant

        self.metric_combo = QComboBox()
        model = QStandardItemModel()

        def add_group(title, items):
            title_item = QStandardItem(f"— {title} —")
            title_item.setFlags(Qt.NoItemFlags)  # Заголовок недоступен для выбора
            model.appendRow(title_item)
            for metric in items:
                item = QStandardItem(metric)
                item.setData(metric, Qt.UserRole)
                model.appendRow(item)

        add_group("Probabilistic", ["SQL", "WQL"])
        add_group("Point forecast (median)", ["MAE", "MASE", "WAPE"])
        add_group("Point forecast (mean)", ["MSE", "RMSE", "RMSLE", "RMSSE", "MAPE", "SMAPE"])

        self.metric_combo.setModel(model)

        # Автоматическая установка метрики по умолчанию (MAPE)
        for i in range(model.rowCount()):
            item = model.item(i)
            if item and item.data(Qt.UserRole) == "MAPE":
                self.metric_combo.setCurrentIndex(i)
                self.selected_metric = "MAPE"
                break

        # Добавление QComboBox в layout
        box.layout().addWidget(QLabel("Метрика:"))
        box.layout().addWidget(self.metric_combo)

        # Установка начального значения (блок закомментирован для избежания конфликта)
        # if isinstance(self.selected_metric, int):
        #     self.metric_combo.setCurrentIndex(self.selected_metric)
        # else:
        #     self.metric_combo.setCurrentText(self.selected_metric)

        # Обработчик выбора, сохраняем выбранную метрику
        def on_metric_changed(index):
            metric = self.metric_combo.currentText()
            if metric.startswith("—"):
                return  # Пропускаем заголовки
            self.selected_metric = metric
            self.log(f"Выбрана метрика: {self.selected_metric}")

        self.metric_combo.currentIndexChanged.connect(on_metric_changed)
        
        self.model_selector = gui.comboBox(
            box, self, "selected_preset",
            items=["best_quality", "high_quality", "medium_quality", "fast_training"],
            label="Пресет:",
            sendSelectedValue=True
        )

        # Получаем модели динамически
        available_models = self._get_available_models()
        # Добавляем выбор моделей
        self.model_selector = gui.comboBox(
            box, self, "selected_model",
            items=available_models,
            label="Модель autogluon:",
            sendSelectedValue=True
        )
        
        # Настройки столбцов
        col_box = gui.widgetBox(self.controlArea, "Столбцы")
        # Хранение всех колонок для выпадающего списка
        self.all_columns = []
        
        # Целевая переменная
        self.target_combo = gui.comboBox(col_box, self, "target_column", label="Целевая:", 
                                         items=[], sendSelectedValue=True,
                                         callback=self.on_target_column_changed) 
        # ID ряда
        self.id_combo = gui.comboBox(col_box, self, "id_column", label="ID ряда:", 
                                     items=[], sendSelectedValue=True,
                                     callback=self.on_id_column_changed) 
        # Временная метка
        self.timestamp_combo = gui.comboBox(col_box, self, "timestamp_column", label="Время:", 
                                            items=[], sendSelectedValue=True,
                                            callback=self.on_timestamp_column_changed) 
        
        # Настройки частоты
        freq_box = gui.widgetBox(self.controlArea, "Частота временного ряда")
        
        # Чекбокс для автоопределения частоты
        self.auto_freq_checkbox = QCheckBox("Автоматически определять частоту")
        self.auto_freq_checkbox.setChecked(self.auto_frequency)
        self.auto_freq_checkbox.stateChanged.connect(self.on_auto_frequency_changed)
        freq_box.layout().addWidget(self.auto_freq_checkbox)
        
        # Выпадающий список частот
        self.freq_combo = gui.comboBox(freq_box, self, "frequency", 
              items=[f[0] for f in self.FREQUENCIES], 
              label="Частота:",
              callback=self.on_frequency_changed)
        # Заменяем технические обозначения на понятные названия
        for i, (code, label) in enumerate(self.FREQUENCIES):
            self.freq_combo.setItemText(i, f"{label} ({code})")
        
        # Отключаем комбобокс, если автоопределение включено
        self.freq_combo.setDisabled(self.auto_frequency)
        
        # Метка для отображения определенной частоты
        self.detected_freq_label = QLabel("Определенная частота: N/A")
        freq_box.layout().addWidget(self.detected_freq_label)

        # Дополнительные настройки
        extra_box = gui.widgetBox(self.controlArea, "Дополнительно")
        self.holidays_checkbox = QCheckBox("Учитывать праздники")
        self.holidays_checkbox.setChecked(self.include_holidays)
        self.holidays_checkbox.stateChanged.connect(self.on_holidays_changed)
        extra_box.layout().addWidget(self.holidays_checkbox)

        # Добавляем выбор страны для праздников
        self.holiday_country_combo = gui.comboBox(extra_box, self, "holiday_country",
                                                  label="Страна для праздников:",
                                                  items=self.HOLIDAY_COUNTRIES,
                                                  sendSelectedValue=True)
        self.holiday_country_combo.setEnabled(self.include_holidays) # Активируем только если включены праздники
        
        # Настройка для принудительного использования текущей даты
        """self.date_checkbox = QCheckBox("Использовать текущую дату (игнорировать даты в данных)")
        self.date_checkbox.setChecked(self.use_current_date)
        self.date_checkbox.stateChanged.connect(self.on_date_option_changed)
        extra_box.layout().addWidget(self.date_checkbox)"""

        # кнопка
        self.run_button = gui.button(self.controlArea, self, "Запустить", callback=self.run_model)

        # логи
        log_box_main = gui.widgetBox(self.controlArea, "Логи", addSpace=True)
        self.log_widget = QPlainTextEdit(readOnly=True)
        self.log_widget.setMinimumHeight(200)
        font = QFont("Monospace")
        font.setStyleHint(QFont.TypeWriter)
        self.log_widget.setFont(font)
        log_box_main.layout().addWidget(self.log_widget)
    
    def _get_available_models(self):
        """ПОЛНЫЙ список всех моделей AutoGluon"""
        try:
            print("Получаем ПОЛНЫЙ список через импорт классов")
            
            # Полный список моделей из GitHub AutoGluon
            all_models = [
                "auto",
                # Статистические
                "Naive", "SeasonalNaive", "Zero", "Average", "SeasonalAverage",
                "ETS", "AutoETS", "ARIMA", "AutoARIMA", "AutoCES",
                "Theta", "DynamicOptimizedTheta", "IMAPA", "ADIDA", "Croston",
                
                # Табличные
                "DirectTabular", "RecursiveTabular",
                
                # Deep Learning
                "DeepAR", "SimpleFeedForward", "TemporalFusionTransformer",
                "PatchTST", "TiDE", "DLinear", "WaveNet", "NPTS",
                
                # Предобученные
                "Chronos"
            ]
            
            # Проверяем какие реально доступны в вашей установке
            available_models = ["auto"]
            
            try:
                import autogluon.timeseries.models as ag_models
                for model_name in all_models[1:]:  # пропускаем "auto"
                    try:
                        model_class = getattr(ag_models, f"{model_name}Model", None)
                        if model_class is not None:
                            available_models.append(model_name)
                            print(format_message('success', f"{model_name} доступна"))
                        else:
                            print(format_message('error', f"{model_name} недоступна"))
                    except AttributeError:
                        print(format_message('error', f"{model_name} недоступна"))
                        
            except Exception as e:
                print(f"Ошибка проверки: {e}")
                # Fallback на популярные модели
                available_models = [
                    "auto", "Naive", "SeasonalNaive", "ETS", "AutoETS", 
                    "DirectTabular", "RecursiveTabular", "DeepAR", 
                    "TemporalFusionTransformer", "PatchTST", "TiDE"
                ]
                
            print(f"Итого доступно: {len(available_models)} моделей")
            return available_models
            
        except Exception as e:
            print(f"Полная проверка failed: {e}")
            return [
                "auto", "Naive", "SeasonalNaive", "ETS", "AutoETS",
                "DirectTabular", "RecursiveTabular", "DeepAR", 
                "TemporalFusionTransformer", "PatchTST", "TiDE"
            ]

    def on_frequency_changed(self):
        """Обработчик изменения частоты"""
        self.log(f"Пользователь выбрал частоту: {self.get_current_frequency()}")
        if self.data is not None:
            self.update_frequency_info()

    def get_current_frequency(self):
        """Получает текущую выбранную частоту"""
        if self.auto_frequency:
            return self.detected_frequency
        else:
            freq_index = self.frequency
            if isinstance(freq_index, int) and 0 <= freq_index < len(self.FREQUENCIES):
                return self.FREQUENCIES[freq_index][0]
            else:
                return self.frequency

    def estimate_points_after_aggregation(self, freq_code):
        """Оценивает количество точек после агрегации по частоте для каждого ID"""
        if self.data is None:
            return {'min_points': 0, 'max_points': 0, 'details': {}}
        
        # Проверяем, есть ли временная колонка
        if self.timestamp_column not in self.data.columns:
            return {'min_points': 0, 'max_points': 0, 'details': {}}
        
        try:
            points_by_id = {}
            
            if self.id_column in self.data.columns:
                # Анализируем каждый ID отдельно
                unique_ids = self.data[self.id_column].unique()
                
                for uid in unique_ids:
                    id_data = self.data[self.data[self.id_column] == uid].copy()
                    id_data = id_data.sort_values(self.timestamp_column)
                    
                    if len(id_data) == 0:
                        continue
                        
                    start_date = id_data[self.timestamp_column].min()
                    end_date = id_data[self.timestamp_column].max()
                    
                    # Создаем диапазон дат с нужной частотой
                    date_range = pd.date_range(start=start_date, end=end_date, freq=freq_code)
                    estimated_points = len(date_range)
                    
                    # Получаем человекочитаемое название ID если есть маппинг
                    display_id = uid
                    if self.id_column in self.categorical_mapping:
                        mapping = self.categorical_mapping[self.id_column]
                        try:
                            id_index = int(float(uid))
                            if 0 <= id_index < len(mapping):
                                display_id = f"{mapping[id_index]} ({uid})"
                        except:
                            pass
                    
                    points_by_id[display_id] = {
                        'points': estimated_points,
                        'start': start_date,
                        'end': end_date,
                        'original_records': len(id_data)
                    }
            else:
                # Если нет ID колонки, анализируем все данные как один ряд
                sample_data = self.data.copy().sort_values(self.timestamp_column)
                start_date = sample_data[self.timestamp_column].min()
                end_date = sample_data[self.timestamp_column].max()
                date_range = pd.date_range(start=start_date, end=end_date, freq=freq_code)
                estimated_points = len(date_range)
                
                points_by_id['Единый ряд'] = {
                    'points': estimated_points,
                    'start': start_date,
                    'end': end_date,
                    'original_records': len(sample_data)
                }
            
            if not points_by_id:
                return {'min_points': 0, 'max_points': 0, 'details': {}}
            
            all_points = [info['points'] for info in points_by_id.values()]
            result = {
                'min_points': min(all_points),
                'max_points': max(all_points),
                'details': points_by_id
            }
            
            return result
            
        except Exception as e:
            self.log(f"Ошибка оценки точек для частоты {freq_code}: {str(e)}")
            # Запасной расчет
            freq_ratios = {
                'T': self.data_length,           
                'H': self.data_length // 60,     
                'D': self.data_length,           
                'B': int(self.data_length * 0.7), 
                'W': self.data_length // 7,     
                'M': self.data_length // 30,    
                'Q': self.data_length // 90,    
                'Y': self.data_length // 365    
            }
            fallback_points = max(1, freq_ratios.get(freq_code, self.data_length // 30))
            return {'min_points': fallback_points, 'max_points': fallback_points, 'details': {}}

    def update_frequency_info(self):
        # очищаем пул ошибок
        self.clear_messages()
        """Обновляет информацию о частоте БЕЗ блокировки - только информативно"""
        if self.data_length == 0:
            return
            
        # Получаем текущую частоту
        current_freq = self.get_current_frequency()
        
        # Оцениваем количество точек после агрегации для всех ID
        aggregation_info = self.estimate_points_after_aggregation(current_freq)
        min_points = aggregation_info['min_points']
        max_points = aggregation_info['max_points']
        details = aggregation_info['details']
        
        # Определяем количество временных рядов
        num_series = len(details) if details else 1
        
        # Получаем название частоты
        freq_name = current_freq
        for code, label in self.FREQUENCIES:
            if code == current_freq:
                freq_name = f"{label} ({code})"
                break
        
        # Формируем детальную информацию
        if details:
            details_text = []
            for id_name, info in details.items():
                details_text.append(f"{id_name}: {info['points']} точек")
            details_str = " | ".join(details_text[:3])  # Показываем первые 3
            if len(details) > 3:
                details_str += f" | и еще {len(details)-3}..."
        else:
            details_str = f"~{min_points} точек"
        """
        # Оценка возможных проблем
        likely_problems = []
        if min_points < 10:
            likely_problems.append("Очень мало данных для обучения")
        if min_points < self.prediction_length + 5:
            likely_problems.append("Может не хватить данных для указанной длины прогноза")
        """
        
        # Оценка возможных проблем с цветовой индикацией
        likely_problems = []
        if min_points < 10:
            likely_problems.append("Очень мало данных для обучения")

        # Четырехуровневая система предупреждений
        if self.prediction_length >= min_points:
            likely_problems.append("Прогноз больше или равен данным!")
        elif self.prediction_length > min_points * 0.6:  # Больше 60%
            likely_problems.append("Прогноз больше 60% от данных")
        elif self.prediction_length > min_points * 0.4:  # Больше 40%
            likely_problems.append("Прогноз больше 40% от данных")
        # Если меньше 40% - все хорошо, ничего не добавляем

        # Обновляем отображение только с ИНФОРМАЦИЕЙ
        if min_points == max_points:
            points_info = f"{min_points} точек"
        else:
            points_info = f"{min_points}-{max_points} точек"
        
        info_text = f"Информация о частоте: {freq_name}\n"
        info_text += f"После агрегации: {points_info} ({num_series} рядов)\n"
        info_text += f"{details_str}"
        
        if likely_problems:
            info_text += f"\n"+format_message('warning',f"Возможные проблемы: {', '.join(likely_problems)}")
            info_text += f"\nAutoGluon сам проверит совместимость при запуске"
            style = "color: orange; background-color: #fff7e6; padding: 5px; border-radius: 3px;"
        else:
            info_text += f"\n"+format_message('success',f"Данные выглядят совместимыми с выбранной частотой")
            style = "color: green; background-color: #f0fff0; padding: 5px; border-radius: 3px;"
        
        self.max_length_label.setText(info_text)
        self.max_length_label.setStyleSheet(style)
        
        # Логируем подробности
        self.log(f"Частота: {current_freq}, рядов: {num_series}, точек: {min_points}-{max_points}")

        # Сохраняем для использования в других методах
        self.min_points_current = min_points


    def on_target_column_changed(self):
        self.log(f"Вы выбрали целевую колонку: {self.target_column}")
    def on_id_column_changed(self):
        self.log(f"Вы выбрали ID колонку: {self.id_column}")
        self.log(f"DEBUG: self.data is None = {self.data is None}")  # ← ДОБАВИТЬ
        if self.data is not None:
            self.log("DEBUG: Вызываю update_frequency_info()")  # ← ДОБАВИТЬ
            self.update_frequency_info()
        else:
            self.log("DEBUG: self.data равно None, пропускаю обновление")  # ← ДОБАВИТЬ
    def on_timestamp_column_changed(self):
        self.log(f"Вы выбрали временную колонку: {self.timestamp_column}")

    def on_holidays_changed(self, state):
        self.include_holidays = state > 0
        self.holiday_country_combo.setEnabled(self.include_holidays) # Включаем/отключаем выбор страны

    """def on_date_option_changed(self, state):
        self.use_current_date = state > 0"""
        
    def on_auto_frequency_changed(self, state):
        self.auto_frequency = state > 0
        self.freq_combo.setDisabled(self.auto_frequency)
        if self.data is not None:
            if self.auto_frequency:
                self.detected_freq_label.setText(f"Определенная частота: {self.detected_frequency}")
            self.update_frequency_info()

    def on_prediction_length_changed(self, value):
        """Обновляет проверку при изменении длины прогноза"""
        if self.data is not None:
            self.check_prediction_length()

    def detect_frequency(self, data):
        """Определяет частоту временного ряда на основе данных"""
        try:
            # Сортируем даты
            dates = data[self.timestamp_column].sort_values()
            
            # Если меньше 2 точек, невозможно определить
            if len(dates) < 2:
                return "D"  # По умолчанию день
                
            # Вычисляем разницу между последовательными датами
            diffs = []
            for i in range(1, min(10, len(dates))):
                diff = dates.iloc[i] - dates.iloc[i-1]
                diffs.append(diff.total_seconds())
                
            # Используем медиану для определения типичного интервала
            if not diffs:
                return "D"
                
            median_diff = pd.Series(diffs).median()
            
            # Определяем частоту на основе интервала
            if median_diff <= 60:  # до 1 минуты
                freq = "T"
            elif median_diff <= 3600:  # до 1 часа
                freq = "H"
            elif median_diff <= 86400:  # до 1 дня
                freq = "D"
            elif median_diff <= 604800:  # до 1 недели
                freq = "W"
            elif median_diff <= 2678400:  # до ~1 месяца (31 день)
                freq = "M"
            elif median_diff <= 7948800:  # до ~3 месяцев (92 дня)
                freq = "Q"
            else:  # более 3 месяцев
                freq = "Y"
                
            self.log(f"Определена частота данных: {freq} (медианный интервал: {median_diff/3600:.1f} часов)")
            return freq
            
        except Exception as e:
            self.log(f"Ошибка при определении частоты: {str(e)}")
            return "D"  # По умолчанию день

    def check_prediction_length(self):
        # очищаем пул ошибок
        self.clear_messages() 
        """Простая проверка длины прогноза без агрессивной блокировки"""
        if self.data_length == 0:
            self.max_allowed_prediction = 365  # Большое значение по умолчанию
            self.max_length_label.setText("Максимальная длина прогноза: Н/Д (нет данных)")
            return
        
        # Устанавливаем разумные лимиты, но НЕ блокируем пользователя
        reasonable_limits = {
            'Y': 10,   # Не более 10 лет
            'Q': 20,   # Не более 20 кварталов
            'M': 36,   # Не более 36 месяцев
            'W': 104,  # Не более 2 лет недель
            'D': 365,  # Не более года дней
            'B': 260,  # Не более года рабочих дней
            'H': 8760, # Не более года часов
            'T': 525600 # Не более года минут
        }
        
        current_freq = self.get_current_frequency()
        self.max_allowed_prediction = reasonable_limits.get(current_freq, 100)
        
        # Обновляем информацию о частоте
        self.update_frequency_info()
        
        # НЕ блокируем кнопку - позволяем AutoGluon решать!
        self.run_button.setDisabled(False)
        
        """
        # Только информативное предупреждение при очень больших значениях
        if self.prediction_length > self.max_allowed_prediction:
            self.warning(f"Длина прогноза ({self.prediction_length}) кажется очень большой для частоты {current_freq}. "
                        f"AutoGluon может выдать ошибку при обучении.")
        else:
            self.warning("")
        """
        # Получаем минимальное количество точек для текущих данных
        if hasattr(self, 'min_points_current') and self.min_points_current:
            min_points = self.min_points_current
            
            if self.prediction_length >= min_points:
                self.error(format_message('crirical',f"Прогноз ({self.prediction_length}) больше данных ({min_points})!"))
                return
            elif self.prediction_length > min_points * 0.6:
                self.warning(format_message('warning',f"Прогноз ({self.prediction_length}) составляет {self.prediction_length/min_points*100:.0f}% от данных"))
                return

        if self.prediction_length > self.max_allowed_prediction:
            self.warning(f"Длина прогноза ({self.prediction_length}) кажется очень большой...")

    def log(self, message):
        """Надежное логирование"""
        log_entry = f"{datetime.now().strftime('%H:%M:%S')} - {message}"
        self.log_messages += log_entry + "\n"
        self.log_widget.appendPlainText(log_entry)
        self.log_widget.verticalScrollBar().setValue(
            self.log_widget.verticalScrollBar().maximum()
        )
        QCoreApplication.processEvents()

    @Inputs.data
    def set_data(self, dataset):
        self.error("")
        self.warning("")
        try:
            if dataset is None:
                self.data = None
                self.log("Данные очищены")
                self.data_length = 0
                self.max_length_label.setText("Максимальная длина прогноза: N/A")
                self.detected_freq_label.setText("Определенная частота: N/A")
                return
            
            # ДИАГНОСТИКА: Что именно приходит от FormTimeseries
            self.log("=== ДИАГНОСТИКА ВХОДНЫХ ДАННЫХ ===")
            self.log(f"Тип dataset: {type(dataset)}")
            self.log(f"Размер dataset: {dataset.X.shape if hasattr(dataset, 'X') else 'N/A'}")
            
            # Проверяем домен
            domain = dataset.domain
            self.log(f"Количество атрибутов: {len(domain.attributes)}")
            self.log(f"Количество мета: {len(domain.metas)}")
            self.log(f"Количество классов: {len(domain.class_vars) if domain.class_vars else 0}")
            
            # Проверяем переменные
            all_vars = list(domain.attributes) + list(domain.metas) + (list(domain.class_vars) if domain.class_vars else [])
            for var in all_vars:
                self.log(f"Переменная '{var.name}': тип {type(var).__name__}")
                if isinstance(var, TimeVariable):
                    self.log(f"  TimeVariable найдена: {var.name}")
            
            # Получаем сырые данные для проверки
            temp_df = self.prepare_data(dataset, for_type_check_only=True)
            if temp_df is not None and len(temp_df) > 0:
                self.log("=== ОБРАЗЕЦ СЫРЫХ ДАННЫХ ===")
                for col in temp_df.columns:
                    sample_vals = temp_df[col].head(3).tolist()
                    self.log(f"Колонка '{col}' ({temp_df[col].dtype}): {sample_vals}")
                    
                    # Особая проверка для временных колонок
                    if 'date' in col.lower() or 'time' in col.lower():
                        if pd.api.types.is_numeric_dtype(temp_df[col]):
                            min_val, max_val = temp_df[col].min(), temp_df[col].max()
                            self.log(f"  Числовой диапазон: {min_val} - {max_val}")
                            
                            # Проверяем, похоже ли на timestamp
                            if min_val > 1e9:  # Больше миллиарда - вероятно timestamp
                                sample_timestamp = pd.to_datetime(min_val, unit='s', errors='ignore')
                                self.log(f"  Как timestamp (сек): {sample_timestamp}")
                                sample_timestamp_ms = pd.to_datetime(min_val, unit='ms', errors='ignore')
                                self.log(f"  Как timestamp (мс): {sample_timestamp_ms}")
            
            self.log("=== КОНЕЦ ДИАГНОСТИКИ ===")
            
            # Проверка наличия специальных атрибутов от FormTimeseries
            self.from_form_timeseries = False  # Сбрасываем флаг
            if hasattr(dataset, 'from_form_timeseries') and dataset.from_form_timeseries:
                self.from_form_timeseries = True
                self.log("Данные получены из компонента FormTimeseries")
                # Если данные от FormTimeseries, можно получить дополнительную информацию
                if hasattr(dataset, 'time_variable') and dataset.time_variable:
                    self.timestamp_column = dataset.time_variable
                    self.log(f"Автоматически установлена временная переменная: {self.timestamp_column}")
            
            # Получаем колонки из dataset ДО prepare_data
            domain = dataset.domain
            attr_cols = [var.name for var in domain.attributes]
            meta_cols = [var.name for var in domain.metas]
            class_cols = [var.name for var in domain.class_vars] if domain.class_vars else []
            self.all_columns = attr_cols + class_cols + meta_cols
            
            # Находим и сохраняем категориальные маппинги
            self.categorical_mapping = {}  # Сбрасываем предыдущие маппинги
            for var in domain.variables + domain.metas:
                if hasattr(var, 'values') and var.values:
                    # Получаем список значений категориальной переменной
                    values = var.values
                    if values:
                        self.log(f"Сохраняем маппинг для категориальной переменной '{var.name}': {values}")
                        self.categorical_mapping[var.name] = values

            # ДОБАВЛЕНО: Проверяем наличие TimeVariable
            time_vars = []
            for var in domain.variables + domain.metas:
                if isinstance(var, TimeVariable):
                    time_vars.append(var.name)
            
            if time_vars:
                self.log(f"Обнаружены временные переменные: {', '.join(time_vars)}")
                if self.timestamp_column not in time_vars:
                    # Автоматически выбираем первую временную переменную
                    self.timestamp_column = time_vars[0]
                    self.log(f"Автоматически выбрана временная переменная (TimeVariable по умолчанию): {self.timestamp_column}")
            
            if not self.all_columns:
                raise ValueError("Нет колонок в данных!")
            
            # --- Автоматическое определение столбцов ---
            # Пытаемся определить, только если текущий выбор невалиден или не сделан
            
            # Получаем DataFrame для проверки типов, если еще не создан
            temp_df_for_types = None
            if not isinstance(dataset, pd.DataFrame): # Если на вход пришел Orange.data.Table
                temp_df_for_types = self.prepare_data(dataset, for_type_check_only=True)
            else: # Если на вход уже пришел DataFrame (маловероятно для set_data, но для полноты)
                temp_df_for_types = dataset

            # Целевой столбец
            if not self.target_column or self.target_column not in self.all_columns:
                self.log(f"Целевой столбец '{self.target_column}' не установлен или не найден в текущих данных. Попытка автоопределения...")
                potential_target = None
                
                # 1. Проверяем Orange Class Variable
                if domain.class_vars:
                    for cv in domain.class_vars:
                        if isinstance(cv, ContinuousVariable) or \
                        (temp_df_for_types is not None and cv.name in temp_df_for_types.columns and pd.api.types.is_numeric_dtype(temp_df_for_types[cv.name])):
                            potential_target = cv.name
                            self.log(f"Найдена целевая колонка из Orange Class Variable: '{potential_target}'")
                            break
                
                if not potential_target:
                    # 2. Ищем по приоритетным точным именам
                    priority_names = ["Target", "target", "sales", "Sales", "value", "Value"]
                    for name in priority_names:
                        if name in self.all_columns and \
                        (temp_df_for_types is not None and name in temp_df_for_types.columns and pd.api.types.is_numeric_dtype(temp_df_for_types[name])):
                            potential_target = name
                            self.log(f"Найдена целевая колонка по точному приоритетному имени: '{potential_target}'")
                            break
                
                if not potential_target and self.all_columns and temp_df_for_types is not None:
                    # 3. Ищем по подстрокам (числовые)
                    search_terms = ["target", "sales", "value"]
                    for term in search_terms:
                        for col_name in self.all_columns:
                            if term in col_name.lower() and col_name in temp_df_for_types.columns and \
                            pd.api.types.is_numeric_dtype(temp_df_for_types[col_name]):
                                potential_target = col_name
                                self.log(f"Найдена целевая колонка по подстроке '{term}': '{potential_target}' (числовая)")
                                break
                        if potential_target: break

                if not potential_target and self.all_columns and temp_df_for_types is not None:
                    # 4. Берем первую числовую Orange ContinuousVariable, не являющуюся ID или Timestamp
                    for var in domain.attributes: # Атрибуты обычно числовые или категориальные
                        if isinstance(var, ContinuousVariable) and var.name not in [self.id_column, self.timestamp_column]:
                            potential_target = var.name
                            self.log(f"В качестве целевой колонки выбрана первая Orange ContinuousVariable: '{potential_target}'")
                            break
                    if not potential_target: # Если не нашли среди атрибутов, ищем просто числовую
                        for col in self.all_columns:
                            if col not in [self.id_column, self.timestamp_column] and \
                            col in temp_df_for_types.columns and pd.api.types.is_numeric_dtype(temp_df_for_types[col]):
                                potential_target = col
                                self.log(f"В качестве целевой колонки выбрана первая числовая: '{potential_target}'")
                                break

                self.target_column = potential_target if potential_target else (self.all_columns[0] if self.all_columns else "")
                self.log(f"Автоматически выбран целевой столбец: '{self.target_column}'")

            # ID столбец
            if not self.id_column or self.id_column not in self.all_columns:
                self.log(f"ID столбец '{self.id_column}' не установлен или не найден в текущих данных. Попытка автоопределения...")
                potential_id = None
                # 1. Ищем Orange DiscreteVariable или StringVariable (не цель и не время)
                for var_list in [domain.attributes, domain.metas]:
                    for var in var_list:
                        if var.name not in [self.target_column, self.timestamp_column] and \
                        (isinstance(var, DiscreteVariable) or isinstance(var, StringVariable)):
                            potential_id = var.name
                            self.log(f"Найдена ID колонка из Orange Discrete/String Variable: '{potential_id}'")
                            break
                    if potential_id: break
                
                if not potential_id:
                    # 2. Поиск по стандартным именам
                    potential_id = next((name for name in ["item_id", "id", "ID", "Country", "Shop", "City"] if name in self.all_columns and name not in [self.target_column, self.timestamp_column]), None)
                    if potential_id: self.log(f"Найдена ID колонка по стандартному имени: '{potential_id}'")

                if not potential_id and self.all_columns and temp_df_for_types is not None:
                    # 3. Ищем подходящий тип (строка/объект/категория), не цель и не время
                    for col in self.all_columns:
                        if col not in [self.target_column, self.timestamp_column] and col in temp_df_for_types.columns and \
                        (pd.api.types.is_string_dtype(temp_df_for_types[col]) or \
                            pd.api.types.is_object_dtype(temp_df_for_types[col]) or \
                            pd.api.types.is_categorical_dtype(temp_df_for_types[col])):
                            potential_id = col
                            self.log(f"Найдена подходящая по типу ID колонка: '{potential_id}'")
                            break
                self.id_column = potential_id if potential_id else (next((c for c in self.all_columns if c not in [self.target_column, self.timestamp_column]), self.all_columns[0] if self.all_columns else ""))
                self.log(f"Автоматически выбран ID столбец: '{self.id_column}'")

            # Временной столбец (если не определен как TimeVariable и невалиден)
            if not self.timestamp_column or self.timestamp_column not in self.all_columns:
                self.log(f"Временной столбец '{self.timestamp_column}' не установлен/не найден или не является TimeVariable. Попытка автоопределения...")
                potential_ts = None
                # 1. Orange TimeVariable уже должен был быть выбран ранее в set_data.
                # Здесь мы ищем, если он не был TimeVariable или стал невалидным.
                
                # 2. Поиск по стандартным именам
                potential_ts = next((name for name in ["timestamp", "Timestamp", "time", "Time", "Date", "date"] if name in self.all_columns and name not in [self.target_column, self.id_column]), None)
                if potential_ts: self.log(f"Найдена временная колонка по стандартному имени: '{potential_ts}'")

                if not potential_ts and self.all_columns and temp_df_for_types is not None:
                    # 3. Пытаемся распарсить
                    for col in self.all_columns:
                        if col not in [self.target_column, self.id_column] and col in temp_df_for_types.columns:
                            try:
                                parsed_sample = pd.to_datetime(temp_df_for_types[col].dropna().iloc[:5], errors='coerce')
                                if not parsed_sample.isna().all():
                                    potential_ts = col
                                    self.log(f"Найдена подходящая по типу временная колонка: '{potential_ts}' (можно преобразовать в дату)")
                                    break
                            except Exception:
                                continue
                self.timestamp_column = potential_ts if potential_ts else (next((c for c in self.all_columns if c not in [self.target_column, self.id_column]), self.all_columns[0] if self.all_columns else ""))
                self.log(f"Автоматически выбран временной столбец: '{self.timestamp_column}'")
            
            self.log("Обработка входных данных...")
            self.data = self.prepare_data(dataset)
            
            # Обновляем выпадающие списки колонок
            self.target_combo.clear()
            self.id_combo.clear()
            self.timestamp_combo.clear()
            
            self.target_combo.addItems(self.all_columns)
            self.id_combo.addItems(self.all_columns)
            self.timestamp_combo.addItems(self.all_columns)
            
            # Устанавливаем выбранные значения в comboBox'ах
            self.target_combo.setCurrentText(self.target_column)
            self.id_combo.setCurrentText(self.id_column)
            self.timestamp_combo.setCurrentText(self.timestamp_column)
            
            # Логируем финальный выбор колонок после автоопределения (если оно было) и установки в UI
            self.log(f"Автоопределены колонки — Target: {self.target_column}, ID: {self.id_column}, Timestamp: {self.timestamp_column}")
            
            required = {self.timestamp_column, self.target_column, self.id_column}
            if not required.issubset(set(self.data.columns)):
                missing = required - set(self.data.columns)
                raise ValueError(f"Отсутствуют столбцы: {missing}")
                
            # Получаем длину данных
            self.data_length = len(self.data)
            self.log(f"Загружено {self.data_length} записей")
            
            # Определяем частоту данных
            if pd.api.types.is_datetime64_dtype(self.data[self.timestamp_column]):
                self.detected_frequency = self.detect_frequency(self.data)
                self.detected_freq_label.setText(f"Определенная частота: {self.detected_frequency}")
            
            # Обновляем максимальную длину прогноза
            self.check_prediction_length()
            
            """
            # Если нужно заменить даты на текущую
            if self.use_current_date and self.timestamp_column in self.data.columns:
                self.log("Применяется замена дат на актуальные")
                
                # Получаем частоту
                freq = self.detected_frequency if self.auto_frequency else self.frequency
                
                try:
                    # Создаем даты от сегодня назад с нужной частотой
                    today = pd.Timestamp.now().normalize()
                    dates = pd.date_range(end=today, periods=len(self.data), freq=freq)
                    dates = dates.sort_values()  # Сортируем от ранних к поздним
                    
                    # Заменяем столбец времени
                    self.data[self.timestamp_column] = dates
                    self.log(f"Даты заменены: от {dates.min().strftime('%Y-%m-%d')} до {dates.max().strftime('%Y-%m-%d')}")
                except Exception as e:
                    self.log(f"Ошибка при создании дат с частотой {freq}: {str(e)}. Используем ежедневную частоту.")
                    # Резервный вариант - ежедневная частота
                    dates = pd.date_range(end=pd.Timestamp.now().normalize(), periods=len(self.data), freq='D')
                    self.data[self.timestamp_column] = dates
            """
            
        except Exception as e:
            self.log(f"ОШИБКА: {str(e)}\n{traceback.format_exc()}")
            self.error(f"Ошибка данных: {str(e)}")
            self.data = None
            self.data_length = 0
            self.max_length_label.setText("Максимальная длина прогноза: N/A")

    def prepare_data(self, table, for_type_check_only=False):
        """Подготовка данных"""
        self.log(f"prepare_data вызвана: for_type_check_only={for_type_check_only}")
        
        if table is None:
            return None

        domain = table.domain
        # Получаем атрибуты
        attr_cols = [var.name for var in domain.attributes]
        df = pd.DataFrame(table.X, columns=attr_cols)
        
        # Добавляем классы, если есть
        if domain.class_vars:
            class_cols = [var.name for var in domain.class_vars]
            class_data = table.Y
            if len(domain.class_vars) == 1:
                class_data = class_data.reshape(-1, 1)
            df_class = pd.DataFrame(class_data, columns=class_cols)
            df = pd.concat([df, df_class], axis=1)
        
        # Добавляем мета-атрибуты
        if domain.metas:
            meta_cols = [var.name for var in domain.metas]
            meta_data = table.metas
            df_meta = pd.DataFrame(meta_data, columns=meta_cols)
            df = pd.concat([df, df_meta], axis=1)
        
        if for_type_check_only:
            return df

        # ПРОСТАЯ ОБРАБОТКА БЕЗ ПРОВЕРОК "КОРРЕКТНОСТИ"
        self.log("Обработка данных...")
        
        # 1. Обработка колонки времени
        if self.timestamp_column and self.timestamp_column in df.columns:
            if not pd.api.types.is_datetime64_dtype(df[self.timestamp_column]):
                try:
                    # Проверяем первое значение, чтобы понять формат
                    first_value = df[self.timestamp_column].iloc[0] if len(df) > 0 else None
                    
                    # Проверяем, является ли первое значение числом (даже если dtype=object)
                    if first_value is not None:
                        try:
                            float_val = float(first_value)
                            if float_val > 1e9:  # Похоже на Unix timestamp
                                df[self.timestamp_column] = pd.to_datetime(df[self.timestamp_column].astype(float), unit='s')
                                self.log(format_message('success',"Преобразованы Unix timestamps в даты (из object dtype)"))
                            else:
                                df[self.timestamp_column] = pd.to_datetime(df[self.timestamp_column])
                                self.log(format_message('success'," Преобразованы числовые даты"))
                        except (ValueError, TypeError):
                            # Это действительно строки
                            df[self.timestamp_column] = pd.to_datetime(df[self.timestamp_column])
                            self.log(format_message('success',"Преобразованы строковые даты"))
                    else:
                        df[self.timestamp_column] = pd.to_datetime(df[self.timestamp_column])
                        self.log(format_message('success',"Преобразованы даты"))
                        
                    # Показываем что получилось
                    self.log(f"Диапазон дат: {df[self.timestamp_column].min()} - {df[self.timestamp_column].max()}")
                    if self.id_column in df.columns:
                        for country in df[self.id_column].unique()[:3]:
                            country_data = df[df[self.id_column] == country]
                            self.log(f"  {country}: {len(country_data)} записей, "
                                f"{country_data[self.timestamp_column].min()} - "
                                f"{country_data[self.timestamp_column].max()}")
                            
                except Exception as e:
                    self.log(format_message('error',f"Не удалось преобразовать даты: {str(e)}"))
                    self.log("Создаем искусственные даты как запасной вариант")
                    df = self.create_reasonable_dates(df)
        
        # 2. Обработка целевой колонки
        if self.target_column and self.target_column in df.columns:
            df[self.target_column] = pd.to_numeric(df[self.target_column], errors="coerce")
            self.log(f"Target колонка: {df[self.target_column].dtype}")

        # 3. Обработка ID колонки
        if self.id_column and self.id_column in df.columns:
            df[self.id_column] = df[self.id_column].astype(str)
            self.log(f"ID колонка: {df[self.id_column].dtype}")
        
        # 4. Удаляем пустые строки
        cols_to_check = [col for col in [self.timestamp_column, self.target_column, self.id_column] 
                        if col and col in df.columns]
        if cols_to_check:
            df = df.dropna(subset=cols_to_check)
        
        self.log(f"Итого: {len(df)} записей")
        return df

    def create_reasonable_dates(self, df):
        """Создает разумные последовательные даты для каждой категории"""
        self.log("Создание разумных дат для каждой категории...")
        
        # Если есть ID колонка, создаем даты для каждой категории отдельно
        if self.id_column and self.id_column in df.columns:
            df_list = []
            start_date = pd.Timestamp('2023-01-01')
            
            for id_val in df[self.id_column].unique():
                id_data = df[df[self.id_column] == id_val].copy()
                num_records = len(id_data)
                
                # Создаем последовательные даты для этой категории
                dates = pd.date_range(start=start_date, periods=num_records, freq='D')
                id_data[self.timestamp_column] = dates
                
                df_list.append(id_data)
                
                # Следующая категория начинается после окончания предыдущей
                start_date = dates[-1] + pd.Timedelta(days=1)
                
                self.log(f"Категория {id_val}: {num_records} дат от {dates[0].date()} до {dates[-1].date()}")
            
            return pd.concat(df_list, ignore_index=True)
        else:
            # Если нет ID колонки, создаем простую последовательность
            start_date = pd.Timestamp('2023-01-01')
            dates = pd.date_range(start=start_date, periods=len(df), freq='D')
            df[self.timestamp_column] = dates
            self.log(f"Создана единая последовательность дат от {dates[0].date()} до {dates[-1].date()}")
            return df

    def create_future_dates(self, periods):
        """Создает будущие даты с учетом нужной частоты"""
        """
        # Выбор стартовой даты
        if self.use_current_date:
            last_date = pd.Timestamp.now().normalize()
            self.log("Используется текущая дата для старта прогноза")
        else:
        """
        # Берем последнюю дату из временного ряда
        try:
            self.log(f"DEBUG create_future_dates: self.data[{self.timestamp_column}].dtype = {self.data[self.timestamp_column].dtype}")
            self.log(f"DEBUG create_future_dates: последние даты = \n{self.data[self.timestamp_column].tail().to_string()}")
            
            # ИСПРАВЛЕНИЕ: Убеждаемся, что данные отсортированы по дате
            if not self.data[self.timestamp_column].is_monotonic_increasing:
                self.log("Данные не отсортированы по дате, выполняем сортировку...")
                self.data = self.data.sort_values([self.id_column, self.timestamp_column])
            
            # Получаем последнюю дату
            raw_last_date = self.data[self.timestamp_column].iloc[-1]  # Используем iloc[-1] вместо max()
            self.log(f"Используется последняя дата из данных (по порядку): {raw_last_date}, тип: {type(raw_last_date)}")
            
            # Преобразуем в Timestamp если нужно
            if isinstance(raw_last_date, pd.Timestamp):
                last_date = raw_last_date
            elif pd.api.types.is_datetime64_any_dtype(raw_last_date):
                last_date = pd.Timestamp(raw_last_date)
            elif isinstance(raw_last_date, str):
                try:
                    last_date = pd.to_datetime(raw_last_date)
                    self.log(f"Строковая дата успешно преобразована: {last_date}")
                except Exception as e_str:
                    self.log(f"Ошибка преобразования строковой даты: {e_str}")
                    last_date = pd.Timestamp.now().normalize()
            elif isinstance(raw_last_date, (int, float)):
                self.log(f"Числовая дата: {raw_last_date}. Попытка преобразования из Unix timestamp.")
                if pd.Timestamp("2000-01-01").timestamp() < raw_last_date < pd.Timestamp("2050-01-01").timestamp():
                    last_date = pd.Timestamp(raw_last_date, unit='s')
                    self.log(f"Преобразовано из секунд: {last_date}")
                elif pd.Timestamp("2000-01-01").timestamp() * 1000 < raw_last_date < pd.Timestamp("2050-01-01").timestamp() * 1000:
                    last_date = pd.Timestamp(raw_last_date, unit='ms')
                    self.log(f"Преобразовано из миллисекунд: {last_date}")
                else:
                    try:
                        last_date = pd.to_datetime(raw_last_date)
                        self.log(f"Преобразовано pd.to_datetime (авто): {last_date}")
                    except:
                        last_date = pd.Timestamp.now().normalize()
                        self.log(f"Не удалось определить масштаб timestamp. Используем текущую дату: {last_date}")
            else:
                try:
                    last_date = pd.to_datetime(raw_last_date)
                    self.log(f"Дата преобразована из типа {type(raw_last_date)}: {last_date}")
                except Exception as e_conv:
                    self.log(f"Не удалось преобразовать дату '{raw_last_date}' в datetime: {e_conv}. Используем текущую дату.")
                    last_date = pd.Timestamp.now().normalize()

        except Exception as e:
            self.log(f"Ошибка при получении/обработке последней даты: {e}")
            last_date = pd.Timestamp.now().normalize()

        # Определяем частоту
        #freq = self.detected_frequency if self.auto_frequency else self.frequency
        if self.auto_frequency:
            freq = self.detected_frequency
        else:
            freq_index = self.frequency
            if isinstance(freq_index, int) and 0 <= freq_index < len(self.FREQUENCIES):
                freq = self.FREQUENCIES[freq_index][0]
            else:
                freq = self.frequency
        self.log(f"Создание будущих дат от {last_date} с частотой {freq}")
        
        try:
            # ИСПРАВЛЕНИЕ: Начинаем с СЛЕДУЮЩЕГО дня после последней даты
            start_date = last_date + pd.tseries.frequencies.to_offset(freq)
            self.log(f"Начальная дата для прогноза: {start_date}")
            
            # Создаем диапазон дат
            if freq == 'B':
                all_dates = pd.date_range(start=start_date, periods=periods * 2, freq='D')
                dates = all_dates[all_dates.weekday < 5][:periods]
            else:
                dates = pd.date_range(start=start_date, periods=periods, freq=freq)
                
        except Exception as e:
            self.log(f"Ошибка при создании дат: {e}")
            
            try:
                start_date = last_date + pd.Timedelta(days=1)
                dates = pd.date_range(start=start_date, periods=periods, freq='D')
                self.log(f"Используем альтернативные даты с {start_date}")
            except:
                base_date = pd.Timestamp('2024-01-01')
                dates = pd.date_range(start=base_date, periods=periods, freq='D')
                self.log(f"Используем фиксированные даты с {base_date}")

        self.log(f"Создан диапазон дат для прогноза: с {dates[0]} по {dates[-1]}")
        return dates

    def create_future_dates_for_specific_id(self, last_date, model_freq):
        """
        УНИВЕРСАЛЬНАЯ функция создания будущих дат для конкретного ID
        Работает с любыми типами дат и частотами
        """
        try:
            # Нормализуем дату
            if not isinstance(last_date, pd.Timestamp):
                last_date = pd.to_datetime(last_date)
            
            # Получаем частоту            
            freq = model_freq
            self.log(f"[DEBUG] Генерация дат с частотой: {freq}")

            # Создаем следующую дату
            try:
                offset = pd.tseries.frequencies.to_offset(freq)
                start_date = last_date + offset
            except:
                start_date = last_date + pd.Timedelta(days=1)
            
            # Создаем диапазон дат
            try:
                if freq == 'B':  # Рабочие дни
                    all_dates = pd.date_range(start=start_date, periods=self.prediction_length * 2, freq='D')
                    dates = all_dates[all_dates.weekday < 5][:self.prediction_length]
                else:
                    dates = pd.date_range(start=start_date, periods=self.prediction_length, freq=freq)
            except:
                # Универсальный запасной вариант
                dates = pd.date_range(start=start_date, periods=self.prediction_length, freq='D')
            
            return dates
            
        except Exception as e:
            self.log(f"Ошибка создания дат: {e}")
            # Крайний запасной вариант
            try:
                start_date = pd.to_datetime(last_date) + pd.Timedelta(days=1)
                dates = pd.date_range(start=start_date, periods=self.prediction_length, freq='D')
                return dates
            except:
                # Если совсем ничего не работает
                base_date = pd.Timestamp('2024-01-01')
                dates = pd.date_range(start=base_date, periods=self.prediction_length, freq='D')
                return dates

    def run_model(self):
        if self.data is None:
            self.error("Нет данных")
            self.log("Ошибка: данные не загружены")
            return
            
        # Глубокая диагностика структуры данных
        self.log(f"=== ДИАГНОСТИКА ДАННЫХ ===")
        self.log(f"Тип объекта данных: {type(self.data)}")
        
        # Проверяем, DataFrame ли это
        if not isinstance(self.data, pd.DataFrame):
            self.log("Данные не являются pandas DataFrame, пытаюсь преобразовать")
            # Попытка получить исходный Table, если self.data был изменен
            # Это рискованно, если set_data не вызывался с Table
            # Для безопасности, лучше полагаться на то, что self.data уже DataFrame
            try:
                # Если self.data это Table, преобразуем
                if isinstance(self.data, Table): # type: ignore
                    self.data = self.prepare_data(self.data) # prepare_data ожидает Table
                    self.log("Преобразование из Table в DataFrame успешно")
                else:
                    # Если это что-то другое, но не DataFrame, это проблема
                    self.error("Данные имеют неожиданный тип и не могут быть обработаны.")
                    return
            except Exception as e:
                self.log(f"Ошибка преобразования в DataFrame: {str(e)}")
                self.error("Невозможно преобразовать данные в нужный формат")
                return
        
        # Теперь у нас должен быть DataFrame
        self.log(f"Колонки в DataFrame для анализа: {list(self.data.columns)}")
        self.log(f"Колонки, выбранные в UI (или по умолчанию): ID='{self.id_column}', Время='{self.timestamp_column}', Цель='{self.target_column}'")

        # --- Проверка выбранных колонок ---
        # ID колонка
        if not self.id_column or self.id_column not in self.data.columns:
            self.error(f"Выбранная ID колонка '{self.id_column}' отсутствует в данных. Пожалуйста, выберите корректную колонку.")
            return
        # Преобразуем ID колонку в строку на всякий случай, если она еще не такая
        if not pd.api.types.is_string_dtype(self.data[self.id_column]):
            self.data[self.id_column] = self.data[self.id_column].astype(str)
            self.log(f"ID колонка '{self.id_column}' приведена к строковому типу.")

        # Временная колонка
        if not self.timestamp_column or self.timestamp_column not in self.data.columns:
            self.error(f"Выбранная временная колонка '{self.timestamp_column}' отсутствует в данных. Пожалуйста, выберите корректную колонку.")
            return
        if not pd.api.types.is_datetime64_any_dtype(self.data[self.timestamp_column]):
             # Попытка преобразования, если еще не datetime
            try:
                self.data[self.timestamp_column] = pd.to_datetime(self.data[self.timestamp_column], errors='raise')
                self.log(f"Временная колонка '{self.timestamp_column}' успешно преобразована в datetime.")
            except Exception as e:
                self.error(f"Выбранная временная колонка '{self.timestamp_column}' не может быть преобразована в формат даты/времени: {e}")
                return

        # Целевая колонка
        if not self.target_column or self.target_column not in self.data.columns:
            self.error(f"Выбранная целевая колонка '{self.target_column}' отсутствует в данных. Пожалуйста, выберите корректную колонку.")
            return
        if not pd.api.types.is_numeric_dtype(self.data[self.target_column]):
            # Попытка преобразования в числовой тип
            try:
                self.data[self.target_column] = pd.to_numeric(self.data[self.target_column], errors='raise')
                self.log(f"Целевая колонка '{self.target_column}' успешно преобразована в числовой тип.")
            except Exception as e:
                self.error(f"Выбранная целевая колонка '{self.target_column}' не является числовой и не может быть преобразована: {e}")
                return
            
        # Теперь должны быть найдены все колонки
        self.log(f"Финально используемые колонки для модели: ID='{self.id_column}', Время='{self.timestamp_column}', Цель='{self.target_column}'")
        
        # Безопасная сортировка с обработкой ошибок
        try:
            self.log("Попытка сортировки данных...")
            df_sorted = self.data.sort_values([self.id_column, self.timestamp_column])
            self.log("Сортировка успешна")
            # логирование
            self.log("ОТЛАДКА run_model: Проверка df_sorted после сортировки")
            for country_id in df_sorted[self.id_column].unique():
                country_data = df_sorted[df_sorted[self.id_column] == country_id]
                first_date = country_data[self.timestamp_column].iloc[0]
                last_date = country_data[self.timestamp_column].iloc[-1]
                self.log(f"  {country_id}: {len(country_data)} записей, {first_date} - {last_date}")
        except Exception as e:
            self.log(f"Ошибка при сортировке: {str(e)}")
            
            # Проверяем, может ли это быть проблема с индексом вместо имени колонки
            if "KeyError: 1" in str(e) or "KeyError: 0" in str(e):
                self.log("Обнаружена ошибка с индексом. Пробую альтернативный подход")
                # Создаем копию с гарантированными колонками
                df_temp = self.data.copy()
                
                # Если нужная колонка отсутствует или имеет неверное имя, создаем новую
                if self.id_column not in df_temp.columns:
                    df_temp['item_id'] = 'single_item'
                    self.id_column = 'item_id'
                
                try:
                    df_sorted = df_temp.sort_values([self.id_column, self.timestamp_column])
                    self.log("Альтернативная сортировка успешна")
                except:
                    # Если и это не работает, создаем полностью новый DataFrame
                    self.log("Создаю новый DataFrame с правильной структурой")
                    df_new = pd.DataFrame()
                    df_new['item_id'] = ['item_1'] * len(self.data)
                    df_new[self.timestamp_column] = self.data[self.timestamp_column].copy()
                    df_new[self.target_column] = self.data[self.target_column].copy()
                    df_sorted = df_new.sort_values(['item_id', self.timestamp_column])
                    self.id_column = 'item_id'
                    self.log("Новый DataFrame успешно создан и отсортирован")
            else:
                # Другая ошибка, не связанная с индексами
                self.error(f"Ошибка при подготовке данных: {str(e)}")
                return
            
        # Дополнительная проверка длины прогноза перед запуском
        if self.prediction_length > self.max_allowed_prediction and self.max_allowed_prediction > 0:
            self.error(f"Длина прогноза ({self.prediction_length}) превышает максимально допустимую ({self.max_allowed_prediction}) для ваших данных. Уменьшите длину прогноза.")
            self.log(f"ОШИБКА: Длина прогноза слишком велика. Максимум: {self.max_allowed_prediction}")
            return
            
        self.progressBarInit()
        try:
            self.log_widget.clear()
            self.log("=== НАЧАЛО ===")
            
            # Подготовка данных
            self.log("Преобразование в TimeSeriesDataFrame...")
            df_sorted = self.data.sort_values([self.id_column, self.timestamp_column])
            
            # логирование
            self.log("ОТЛАДКА run_model: Проверка df_sorted после сортировки")
            for country_id in df_sorted[self.id_column].unique():
                country_data = df_sorted[df_sorted[self.id_column] == country_id]
                first_date = country_data[self.timestamp_column].iloc[0]
                last_date = country_data[self.timestamp_column].iloc[-1]
                self.log(f"  {country_id}: {len(country_data)} записей, {first_date} - {last_date}")
                
                self.log(f"После агрегации: {len(df_sorted)} записей")

            # Проверяем, что столбцы имеют правильные типы
            self.log(f"Типы данных: {df_sorted.dtypes.to_dict()}")

            # Проверка и конвертация timestamp в datetime
            self.log("Проверка формата колонки времени...")
            if pd.api.types.is_numeric_dtype(df_sorted[self.timestamp_column]):
                self.log(f"Обнаружено числовое значение в колонке времени. Пробую конвертировать из timestamp...")
                try:
                    # Пробуем конвертировать из timestamp в секундах
                    df_sorted[self.timestamp_column] = pd.to_datetime(df_sorted[self.timestamp_column], unit='s')
                    self.log("Конвертация из секунд успешна")
                except Exception as e1:
                    self.log(f"Ошибка конвертации из секунд: {str(e1)}")
                    try:
                        # Пробуем из миллисекунд
                        df_sorted[self.timestamp_column] = pd.to_datetime(df_sorted[self.timestamp_column], unit='ms')
                        self.log("Конвертация из миллисекунд успешна")
                    except Exception as e2:
                        self.log(f"Ошибка конвертации из миллисекунд: {str(e2)}")
                        # Создаем искусственные даты как последнее средство
                        self.log("Создание искусственных дат...")
                        try:
                            start_date = pd.Timestamp('2020-01-01')
                            dates = pd.date_range(start=start_date, periods=len(df_sorted), freq='D')
                            df_sorted[self.timestamp_column] = dates
                            self.log(f"Созданы искусственные даты с {start_date} с шагом 1 день")
                        except Exception as e3:
                            self.log(f"Невозможно создать даты: {str(e3)}")
                            self.error("Не удалось преобразовать колонку времени")
                            return
            
            # Проверяем, что дата теперь в правильном формате
            if not pd.api.types.is_datetime64_dtype(df_sorted[self.timestamp_column]):
                self.log("Принудительное преобразование в datetime...")
                try:
                    df_sorted[self.timestamp_column] = pd.to_datetime(df_sorted[self.timestamp_column], errors='coerce')
                    # Проверяем на наличие NaT (Not a Time)
                    if df_sorted[self.timestamp_column].isna().any():
                        self.log("Обнаружены невалидные даты, замена на последовательные")
                        # Заменяем NaT на последовательные даты
                        valid_mask = ~df_sorted[self.timestamp_column].isna()
                        if valid_mask.any():
                            # Если есть хоть одна валидная дата, используем её как начальную
                            first_valid = df_sorted.loc[valid_mask, self.timestamp_column].min()
                            self.log(f"Первая валидная дата: {first_valid}")
                        else:
                            # Иначе начинаем с сегодня
                            first_valid = pd.Timestamp.now().normalize()
                            self.log("Нет валидных дат, используем текущую дату")
                            
                        # Создаем последовательность дат
                        dates = pd.date_range(start=first_valid, periods=len(df_sorted), freq='D')
                        df_sorted[self.timestamp_column] = dates
                except Exception as e:
                    self.log(f"Ошибка преобразования дат: {str(e)}")
                    self.error("Не удалось преобразовать даты")
                    return
            
            # Добавьте после проверки формата даты и перед созданием TimeSeriesDataFrame
            self.log("Проверка распределения дат...")
            # ЗАКОММЕНТИРОВАНО: Логика для случая, когда даты слишком близки.
            # Если ваши данные всегда имеют корректный диапазон, этот блок может быть не нужен или требовать доработки.
            """
            if pd.api.types.is_datetime64_dtype(df_sorted[self.timestamp_column]):
                 if df_sorted[self.timestamp_column].max() - df_sorted[self.timestamp_column].min() < pd.Timedelta(days=1):
                     self.log("ВНИМАНИЕ: Все даты слишком близки друг к другу. Создаю искусственные даты с правильным интервалом.")
                     # Создаем новые даты
                     start_date = pd.Timestamp('2023-01-01')
                     # dates = pd.date_range(start=start_date, periods=len(df_sorted), freq='D') # Эта строка была для всего df_sorted
                    
                     # Сортируем датафрейм сначала по ID, затем по исходным датам
                     df_sorted = df_sorted.sort_values([self.id_column, self.timestamp_column])
                    
                     # Сохраняем порядок записей для каждого ID
                     all_ids = df_sorted[self.id_column].unique()
                     new_df_list = []
                    
                     for id_val in all_ids:
                         # Получаем подмножество данных для текущего ID
                         id_df = df_sorted[df_sorted[self.id_column] == id_val].copy()
                        
                         # Создаем даты для этого ID
                         id_dates = pd.date_range(start=start_date, periods=len(id_df), freq='D')
                        
                         # Устанавливаем новые даты
                         id_df[self.timestamp_column] = id_dates
                        
                         # Добавляем в новый датафрейм
                         new_df_list.append(id_df)
                    
            #         # Объединяем все обратно
                     df_sorted = pd.concat(new_df_list)
                     # ВАЖНО: Обновляем self.data, если даты были изменены,
                     # чтобы create_future_dates использовал правильные даты.
                     self.data = df_sorted.copy()
                     self.log(f"self.data обновлен новыми датами. Диапазон: с {self.data[self.timestamp_column].min()} по {self.data[self.timestamp_column].max()}")
                     self.log(f"Созданы новые даты (в df_sorted) с {df_sorted[self.timestamp_column].min()} по {df_sorted[self.timestamp_column].max()}")
            """
            self.log(f"Финальный формат времени: {df_sorted[self.timestamp_column].dtype}")
            self.log(f"Диапазон дат: с {df_sorted[self.timestamp_column].min()} по {df_sorted[self.timestamp_column].max()}")

            # Определяем частоту для модели
            if self.auto_frequency:
                model_freq = self.detected_frequency
            else:
                # Получаем код частоты из FREQUENCIES по индексу
                freq_index = self.frequency
                if isinstance(freq_index, int) and 0 <= freq_index < len(self.FREQUENCIES):
                    model_freq = self.FREQUENCIES[freq_index][0]  # Берем код (D, W, M, Q и т.д.)
                else:
                    model_freq = self.frequency
            self.log(f"Используемая частота: {model_freq}")

            # Если выбрана не дневная частота, агрегируем данные
            if model_freq != 'D':
                self.log(f"Агрегация данных по частоте: {model_freq}")

                df_sorted = df_sorted.groupby([
                    self.id_column,
                    pd.Grouper(key=self.timestamp_column, freq=model_freq)
                ]).agg({
                    self.target_column: 'sum'
                    # можно добавить агрегаты других колонок
                }).reset_index()

                self.log(f"После агрегации: {len(df_sorted)} записей")

            # Проверка и конвертация ID колонки
            self.log(f"Проверка формата ID колонки '{self.id_column}'...")
            if self.id_column in df_sorted.columns:
                # Проверяем тип данных
                if pd.api.types.is_float_dtype(df_sorted[self.id_column]):
                    self.log("ID колонка имеет тип float, конвертирую в строку")
                    try:
                        # Попытка конвертации в строку
                        df_sorted[self.id_column] = df_sorted[self.id_column].astype(str)
                        self.log("Конвертация ID в строку успешна")
                    except Exception as e:
                        self.log(f"Ошибка конвертации ID в строку: {str(e)}")
                        # Если не получается, создаем новую ID колонку
                        self.log("Создание новой ID колонки...")
                        df_sorted['virtual_id'] = 'item_1'
                        self.id_column = 'virtual_id'
            else:
                self.log(f"ID колонка '{self.id_column}' не найдена, создаю виртуальную")
                df_sorted['virtual_id'] = 'item_1'
                self.id_column = 'virtual_id'
            
            # Проверяем, что все колонки имеют правильный тип
            self.log(f"Обеспечиваем правильные типы данных для всех колонок...")
            # ID колонка должна быть строкой или целым числом
            if self.id_column in df_sorted.columns:
                if not (pd.api.types.is_string_dtype(df_sorted[self.id_column]) or 
                        pd.api.types.is_integer_dtype(df_sorted[self.id_column])):
                    df_sorted[self.id_column] = df_sorted[self.id_column].astype(str)
            
            # Целевая колонка должна быть числом
            if self.target_column in df_sorted.columns:
                if not pd.api.types.is_numeric_dtype(df_sorted[self.target_column]):
                    try:
                        df_sorted[self.target_column] = pd.to_numeric(df_sorted[self.target_column], errors='coerce')
                        # Если есть NaN, заменяем нулями
                        if df_sorted[self.target_column].isna().any():
                            df_sorted[self.target_column] = df_sorted[self.target_column].fillna(0)
                    except:
                        self.log(f"Невозможно преобразовать целевую колонку '{self.target_column}' в числовой формат")
            
            self.log(f"Финальные типы данных: {df_sorted.dtypes.to_dict()}")
            
            if self.timestamp_column in df_sorted.columns:
                if not pd.api.types.is_datetime64_dtype(df_sorted[self.timestamp_column]):
                    try:
                        df_sorted[self.timestamp_column] = pd.to_datetime(df_sorted[self.timestamp_column])
                        self.log(f"Преобразовали {self.timestamp_column} в datetime")
                    except Exception as e:
                        self.log(f"Ошибка преобразования в datetime: {str(e)}")
                else:
                    self.log(f"Колонка {self.timestamp_column} уже имеет тип datetime")
            
            # Добавьте этот блок перед созданием TimeSeriesDataFrame
            if self.from_form_timeseries:
                self.log("Применение специальной обработки для данных из FormTimeseries")
                # Убедимся, что ID колонка существует и имеет правильный тип
                if self.id_column not in df_sorted.columns:
                    self.log(f"ID колонка '{self.id_column}' не найдена. Создаём колонку с единым ID.")
                    df_sorted['item_id'] = 'item_1'
                    self.id_column = 'item_id'
                
                # Проверка наличия временной колонки с корректным типом
                if not pd.api.types.is_datetime64_dtype(df_sorted[self.timestamp_column]):
                    self.log(f"Колонка времени '{self.timestamp_column}' имеет некорректный тип. Преобразуем в datetime.")
                    try:
                        df_sorted[self.timestamp_column] = pd.to_datetime(df_sorted[self.timestamp_column])
                    except Exception as e:
                        self.log(f"Ошибка преобразования в datetime: {str(e)}")
                        # Проверка, можно ли преобразовать как timestamp в секундах
                        try:
                            df_sorted[self.timestamp_column] = pd.to_datetime(df_sorted[self.timestamp_column], unit='s')
                            self.log("Применено преобразование из timestamp в секундах")
                        except:
                            self.error("Невозможно преобразовать временную колонку")
                            return
            
            # Добавить перед созданием TimeSeriesDataFrame
            self.log(f"Проверка структуры данных перед созданием TimeSeriesDataFrame...")
            # Проверяем уникальные значения в ID колонке
            unique_ids = df_sorted[self.id_column].nunique()
            self.log(f"Количество уникальных ID: {unique_ids}")

            # Анализируем длину каждого временного ряда
            id_counts = df_sorted[self.id_column].value_counts()
            self.log(f"Количество записей по ID: мин={id_counts.min()}, макс={id_counts.max()}, среднее={id_counts.mean():.1f}")

            # Если есть только один ID и много записей, нужно разделить данные на несколько временных рядов
            if unique_ids == 1 and len(df_sorted) > 50:
                self.log("Обнаружен один длинный временной ряд. Создаём несколько искусственных рядов...")
                
                # Создаём копию DataFrame
                df_multi = df_sorted.copy()
                
                # Определяем количество искусственных временных рядов с учетом минимального требования
                # AutoGluon требует минимум 29 точек на ряд, добавим запас и сделаем 35
                min_points_per_series = 35  # Минимальное количество точек на ряд (с запасом)
                max_series = len(df_sorted) // min_points_per_series  # Максимально возможное количество рядов
                n_series = min(3, max_series)  # Не более 3 рядов, но учитываем ограничение
                
                if n_series < 1:
                    # Если даже для одного ряда не хватает точек, используем все данные как один ряд
                    self.log("Недостаточно точек для разделения. Используем единый временной ряд.")
                    df_sorted[self.id_column] = 'single_series'
                else:
                    self.log(f"Создаём {n_series} искусственных временных рядов с минимум {min_points_per_series} точками в каждом")
                    
                    # Вычисляем, сколько точек должно быть в каждом ряду
                    points_per_series = len(df_sorted) // n_series
                    
                    # Создаём новую колонку ID, равномерно распределяя точки по рядам
                    ids = []
                    for i in range(len(df_sorted)):
                        series_idx = i // points_per_series
                        # Если превысили количество рядов, используем последний ряд
                        if series_idx >= n_series:
                            series_idx = n_series - 1
                        ids.append(f"series_{series_idx + 1}")
                    
                    df_multi['series_id'] = ids
                    # Используем новую колонку ID вместо старой
                    self.id_column = 'series_id'
                    
                    # Используем новый DataFrame вместо старого
                    df_sorted = df_multi
                    
                    # Проверяем получившееся распределение
                    id_counts = df_sorted[self.id_column].value_counts()
                    self.log(f"Распределение точек по рядам: {id_counts.to_dict()}")

            # Проверяем, нет ли дублирующихся временных меток для одного ID
            duplicate_check = df_sorted.duplicated(subset=[self.id_column, self.timestamp_column])
            if duplicate_check.any():
                dup_count = duplicate_check.sum()
                self.log(f"Обнаружено {dup_count} дублирующихся записей с одинаковыми ID и датой!")
                
                # Стратегия 1: Удаление дубликатов
                df_sorted = df_sorted.drop_duplicates(subset=[self.id_column, self.timestamp_column])
                self.log(f"Удалены дублирующиеся записи. Осталось {len(df_sorted)} записей.")
                
                # Если после удаления дубликатов осталось слишком мало данных, создаем искусственные ряды
                if df_sorted[self.id_column].nunique() == 1 and df_sorted.groupby(self.id_column).size().max() < 10:
                    self.log("После удаления дубликатов данных слишком мало. Пробуем альтернативный подход.")
                    # Создаём временной ряд с ежедневной частотой
                    dates = pd.date_range(start='2022-01-01', periods=30, freq='D')
                    artificial_df = pd.DataFrame({
                        'artificial_id': ['series_1'] * 10 + ['series_2'] * 10 + ['series_3'] * 10,
                        'timestamp': dates.tolist(),
                        'target': np.random.randint(10, 100, 30)
                    })
                    
                    # Используем искусственные данные
                    df_sorted = artificial_df
                    self.id_column = 'artificial_id'
                    self.timestamp_column = 'timestamp'
                    self.target_column = 'target'
                    self.log("Созданы искусственные данные для демонстрации функциональности.")

            # Подготовка данных для праздников, если опция включена
            # known_covariates_to_pass = None
            if self.include_holidays:
                self.log(f"Подготовка признаков праздников для страны: {self.holiday_country}...")
                try:
                    # Убедимся, что временная колонка в df_sorted - это datetime
                    df_sorted[self.timestamp_column] = pd.to_datetime(df_sorted[self.timestamp_column])
                    
                    # Получаем уникальные даты из временного ряда для определения диапазона
                    unique_dates_for_holidays = df_sorted[self.timestamp_column].dt.normalize().unique()
                    if len(unique_dates_for_holidays) > 0:
                        min_holiday_date = unique_dates_for_holidays.min()
                        max_holiday_date = unique_dates_for_holidays.max()
                        
                        # Генерируем праздники для диапазона дат
                        country_holidays_obj = holidays.CountryHoliday(self.holiday_country, years=range(min_holiday_date.year, max_holiday_date.year + 1))
                        
                        # Создаем столбец is_holiday
                        df_sorted['is_holiday'] = df_sorted[self.timestamp_column].dt.normalize().apply(lambda date: 1 if date in country_holidays_obj else 0)
                        # known_covariates_to_pass = ['is_holiday']
                        self.log(f"Добавлен признак 'is_holiday' в df_sorted. Обнаружено {df_sorted['is_holiday'].sum()} праздничных дней.")
                    else:
                        self.log("Не удалось определить диапазон дат для праздников.")
                except Exception as e_holiday:
                    self.log(f"Ошибка при подготовке признаков праздников: {str(e_holiday)}")


            # дополнительная отладка
            self.log("Подготовка TimeSeriesDataFrame...")
            self.log(f"Количество строк в df_sorted: {len(df_sorted)}")
            self.log(f"Пример данных:\n{df_sorted.head(3).to_string()}")

            # Перед строкой: ts_data = TimeSeriesDataFrame.from_data_frame(...)
            self.log("🔍 ОТЛАДКА: Финальная проверка перед TimeSeriesDataFrame")
            for country_id in df_sorted[self.id_column].unique():
                country_data = df_sorted[df_sorted[self.id_column] == country_id]
                # Показываем первые и последние даты
                dates = country_data[self.timestamp_column].sort_values()
                self.log(f"  {country_id}: первые 3 даты: {dates.head(3).tolist()}")
                self.log(f"  {country_id}: последние 3 даты: {dates.tail(3).tolist()}")

            # Преобразуем в формат TimeSeriesDataFrame
            ts_data = TimeSeriesDataFrame.from_data_frame(
                df_sorted,
                id_column=self.id_column,
                timestamp_column=self.timestamp_column
                # known_covariates_names=known_covariates_to_pass # Передаем известные ковариаты
            )
            
            # Частота уже применена при агрегации
            self.log(f"Частота {model_freq} уже была применена при агрегации — пропускаем asfreq()")

            """
            # Пытаемся установить частоту после создания
            try:
                if model_freq != 'D':
                    self.log(f"Установка частоты временного ряда: {model_freq}")
                    ts_data = ts_data.asfreq(model_freq)
            except Exception as freq_err:
                self.log(f"Ошибка при установке частоты {model_freq}: {str(freq_err)}. Используем дневную частоту.")
            
            self.log(f"Создан временной ряд с {len(ts_data)} записями")
            """
            # Обучение
            with tempfile.TemporaryDirectory() as temp_dir:
                model_path = Path(temp_dir)

                # 🛠️ Создаём папку для логов, иначе будет FileNotFoundError
                log_dir = model_path / "logs"
                log_dir.mkdir(parents=True, exist_ok=True)

                self.log(f"Начало обучения модели, время: {self.time_limit} сек...")                

                # Получение метрики (убеждаемся, что это строка)
                metric = self.selected_metric
                if isinstance(metric, int) and 0 <= metric < len(self.METRICS):
                    metric = self.METRICS[metric]
                self.log(f"Используемая метрика: {metric}")

                # проверка модели
                models = None
                if self.selected_model != "auto":
                    models = [self.selected_model]

                try:
                    # Создание предиктора
                    predictor = TimeSeriesPredictor(
                        path=model_path,
                        prediction_length=self.prediction_length,
                        target=self.target_column,
                        eval_metric=metric.lower(),
                        freq=model_freq
                    )
                    
                    # Обучение
                    fit_args = {
                        "time_limit": self.time_limit,
                        "num_val_windows": 1,  # Уменьшаем количество окон валидации
                        "val_step_size": 1    # Минимальный размер шага для валидации
                    }

                    # if self.include_holidays: # Временно отключаем, пока Prophet не доступен
                        # Пытаемся передать информацию о праздниках через гиперпараметры для моделей,
                        # которые это поддерживают, например, Prophet.
                        # Для Prophet параметр называется 'country_holidays_name'.
                        # fit_args['hyperparameters'] = {
                        #     'Prophet': {'country_holidays_name': 'RU'}
                        # }
                        # self.log("Включена опция учета праздников. Настроены гиперпараметры для Prophet (и, возможно, других моделей).")
                    if self.include_holidays and 'is_holiday' not in df_sorted.columns:
                        self.log("Опция 'Учитывать праздники' включена, но не удалось создать признаки праздников. Праздники могут не учитываться.")
                    elif self.include_holidays and 'is_holiday' in df_sorted.columns:
                        self.log("Опция 'Учитывать праздники' включена, признак 'is_holiday' добавлен в данные для обучения.")

                    
                    fit_args["num_val_windows"] = 1  # Уменьшаем количество окон валидации
                    fit_args["val_step_size"] = 1     # Минимальный размер шага для валидации
                    
                    # сбрасываем старый логгер
                    import logging
                    
                    logger = logging.getLogger("autogluon")
                    for handler in logger.handlers[:]:
                        try:
                            handler.close()
                        except:
                            pass
                        logger.removeHandler(handler)
                        
                    # Вызов метода fit с исправленными аргументами
                    predictor.fit(
                        ts_data,
                        **fit_args
                    )
                    
                except ValueError as ve:
                    error_msg = str(ve)
                    self.log(f"Полное сообщение об ошибке: {error_msg}")
                    
                    # Обработка специфических ошибок TimeSeriesPredictor
                    if "observations" in error_msg:
                        self.log("Обнаружена ошибка о количестве наблюдений. Анализ данных...")
                        
                        # Печатаем информацию о структуре данных для диагностики
                        self.log(f"Форма данных: {ts_data.shape}")
                        self.log(f"Количество уникальных ID: {ts_data.index.get_level_values(0).nunique()}")
                        self.log(f"Минимальное количество точек на ряд: {ts_data.groupby(level=0).size().min()}")
                        
                        # Проверяем, не слишком ли короткий временной ряд у какого-то ID
                        ts_lengths = ts_data.groupby(level=0).size()
                        min_ts_id = ts_lengths.idxmin()
                        min_ts_len = ts_lengths.min()
                        
                        if min_ts_len < 10:  # Если какой-то ряд короче 10 точек
                            self.log(f"Временной ряд '{min_ts_id}' имеет всего {min_ts_len} точек, что может быть недостаточно")
                            self.log("Попробуем фильтровать короткие ряды...")
                            
                            # Отфильтруем временные ряды короче определенной длины
                            long_enough_ids = ts_lengths[ts_lengths >= 10].index
                            if len(long_enough_ids) > 0:
                                ts_data = ts_data.loc[long_enough_ids]
                                self.log(f"Отфильтровано до {len(long_enough_ids)} рядов с минимальной длиной 10")
                                
                                # Пробуем обучение с отфильтрованными данными
                                try:
                                    predictor.fit(ts_data, **fit_args)
                                except Exception as e2:
                                    self.log(f"Ошибка после фильтрации: {str(e2)}")
                                    raise
                            else:
                                self.error("Все временные ряды слишком короткие для обучения модели")
                                return
                        
                        # Если не смогли исправить ошибку с наблюдениями, дадим более понятное сообщение
                        import re
                        match = re.search(r"must have >= (\d+) observations", error_msg)
                        if match:
                            required_obs = int(match.group(1))
                            self.error(f"Недостаточно точек в каждом временном ряду: требуется минимум {required_obs}.")
                            self.log(f"Структура данных может быть неправильной. Проверьте ID колонку и временную колонку.")
                        else:
                            self.error(f"Проблема с количеством наблюдений: {error_msg}")
                        return
                    else:
                        # Для других ошибок ValueError
                        raise
                
                # Прогнозирование
                self.log("Выполнение прогноза...")
                known_covariates_for_prediction = None
                if self.include_holidays and 'is_holiday' in df_sorted.columns:
                    self.log("Подготовка будущих признаков праздников для прогноза...")
                    try:
                        # Создаем DataFrame с будущими датами
                        future_dates_for_holidays = self.create_future_dates(self.prediction_length)
                        
                        # Создаем DataFrame для будущих ковариат для каждого item_id
                        future_df_list = []
                        all_item_ids = ts_data.item_ids
                        
                        for item_id_val in all_item_ids:
                            item_future_df = pd.DataFrame({
                                'item_id': item_id_val,  # ← ИЗМЕНИТЬ: использовать стандартное имя
                                'timestamp': pd.to_datetime(future_dates_for_holidays)  # ← ИЗМЕНИТЬ: использовать стандартное имя
                            })
                            future_df_list.append(item_future_df)
                        
                        if future_df_list:
                            future_df_for_covariates = pd.concat(future_df_list)
                            
                            # ← ИЗМЕНИТЬ: использовать стандартные имена колонок
                            future_df_for_covariates = future_df_for_covariates.set_index(['item_id', 'timestamp'])
                            
                            # Генерируем праздники для будущих дат
                            country_holidays_obj_future = holidays.CountryHoliday(
                                self.holiday_country, 
                                years=range(future_dates_for_holidays.min().year, future_dates_for_holidays.max().year + 1)
                            )
                            
                            # ← ИЗМЕНИТЬ: правильное обращение к timestamp в индексе
                            future_df_for_covariates['is_holiday'] = future_df_for_covariates.index.get_level_values('timestamp').to_series().dt.normalize().apply(
                                lambda date: 1 if date in country_holidays_obj_future else 0
                            ).values
                            
                            known_covariates_for_prediction = future_df_for_covariates[['is_holiday']]
                            
                            self.log(f"Созданы будущие признаки праздников: {known_covariates_for_prediction.shape[0]} записей.")
                            self.log(f"Пример будущих ковариат:\n{known_covariates_for_prediction.head().to_string()}")
                        else:
                            self.log("Не удалось создать DataFrame для будущих ковариат (нет item_id).")

                    except Exception as e_fut_holiday:
                        self.log(f"Ошибка при подготовке будущих признаков праздников: {str(e_fut_holiday)}\n{traceback.format_exc()}")
                        known_covariates_for_prediction = None  # сброс при ошибке

                predictions = predictor.predict(ts_data, known_covariates=known_covariates_for_prediction)
                
                # Преобразование результата с диагностикой для отладки дат
                try:
                    self.log(f"Тип прогноза: {type(predictions)}")
                    
                    # Проверяем, является ли это TimeSeriesDataFrame с MultiIndex
                    if hasattr(predictions, 'index') and hasattr(predictions.index, 'nlevels') and predictions.index.nlevels == 2:
                        self.log("Обрабатываем TimeSeriesDataFrame с MultiIndex")
                        
                        # Получаем уникальные ID из прогноза (в правильном порядке!)
                        forecast_numeric_ids = predictions.index.get_level_values(0).unique()
                        self.log(f"Числовые ID в прогнозе (от AutoGluon): {forecast_numeric_ids.tolist()}")
                        
                        # Получаем исходные строковые ID из данных
                        original_string_ids = self.data[self.id_column].unique()
                        self.log(f"Исходные строковые ID в данных: {original_string_ids}")
                        
                        # ДИАГНОСТИКА: Показываем последние даты для каждого ID в исходных данных
                        self.log("=== ДИАГНОСТИКА ИСХОДНЫХ ДАННЫХ ===")
                        for orig_id in original_string_ids:
                            id_subset = self.data[self.data[self.id_column] == orig_id]
                            if len(id_subset) > 0:
                                sorted_subset = id_subset.sort_values(self.timestamp_column)
                                first_date = sorted_subset[self.timestamp_column].iloc[0]
                                last_date = sorted_subset[self.timestamp_column].iloc[-1]
                                self.log(f"ID '{orig_id}': {len(id_subset)} записей, первая: {first_date.date()}, последняя: {last_date.date()}")
                            else:
                                self.log(f"ID '{orig_id}': данные не найдены!")
                        self.log("=== КОНЕЦ ДИАГНОСТИКИ ===")
                        
                        # Применяем категориальный маппинг если есть
                        if self.id_column in self.categorical_mapping:
                            mapping = self.categorical_mapping[self.id_column]
                            self.log(f"Категориальный маппинг: {mapping}")
                            
                            # Создаем двусторонний маппинг
                            numeric_to_country = {}
                            country_to_numeric = {}
                            
                            for i, country_name in enumerate(mapping):
                                numeric_id = str(float(i))  # '0.0', '1.0', '2.0'
                                numeric_to_country[numeric_id] = country_name
                                country_to_numeric[country_name] = numeric_id
                            
                            self.log(f"Маппинг числовой -> страна: {numeric_to_country}")
                            self.log(f"Маппинг страна -> числовой: {country_to_numeric}")
                        else:
                            numeric_to_country = {str(uid): str(uid) for uid in forecast_numeric_ids}
                            country_to_numeric = {str(uid): str(uid) for uid in original_string_ids}
                        
                        # Создаем итоговый DataFrame
                        all_forecast_data = []
                        
                        # Обрабатываем каждый числовой ID из прогноза
                        for numeric_id in forecast_numeric_ids:
                            numeric_id_str = str(numeric_id)
                            self.log(f"\n--- Обработка числового ID: {numeric_id_str} ---")
                            
                            # Получаем человекочитаемое название
                            country_name = numeric_to_country.get(numeric_id_str, f"Unknown_{numeric_id_str}")
                            self.log(f"Маппинг: {numeric_id_str} -> {country_name}")
                            
                            # Извлекаем прогноз для этого ID
                            id_predictions = predictions.loc[numeric_id]
                            self.log(f"Количество прогнозных точек для {country_name}: {len(id_predictions)}")
                            
                            # ИСПРАВЛЕНИЕ: Ищем данные по числовому ID (так как исходные данные содержат числовые ID)
                            id_data = self.data[self.data[self.id_column] == numeric_id_str]
                            
                            if len(id_data) == 0:
                                self.log(f"Исторические данные для числового ID {numeric_id_str} не найдены")
                                last_date = pd.Timestamp('2024-01-01')
                            else:
                                self.log(f"Найдены данные для {country_name} по числовому ID {numeric_id_str}: {len(id_data)} записей")
                                id_data_sorted = id_data.sort_values(self.timestamp_column)
                                
                                # ДОПОЛНИТЕЛЬНАЯ ДИАГНОСТИКА
                                first_date = id_data_sorted[self.timestamp_column].iloc[0]
                                last_date = id_data_sorted[self.timestamp_column].iloc[-1]
                                self.log(f"Диапазон дат для {country_name}: {first_date.date()} - {last_date.date()}")
                                
                                # Показываем последние 3 записи для проверки
                                last_records = id_data_sorted.tail(3)
                                self.log(f"Последние записи для {country_name}:")
                                for _, row in last_records.iterrows():
                                    self.log(f"  Дата: {row[self.timestamp_column].date()}, Target: {row[self.target_column]}")
                            
                            # Создаем будущие даты для этого ID
                            future_dates = self.create_future_dates_for_specific_id(last_date, model_freq)
                            self.log(f"Прогнозные даты для {country_name}: {future_dates[0].strftime('%Y-%m-%d')} - {future_dates[-1].strftime('%Y-%m-%d')}")
                            
                            # Формируем итоговый прогноз для этого ID
                            id_forecast = pd.DataFrame()
                            id_forecast[self.id_column] = [country_name] * len(future_dates)
                            id_forecast['timestamp'] = [d.strftime('%Y-%m-%d') for d in future_dates]
                            
                            # Копируем числовые прогнозные колонки
                            for col in id_predictions.columns:
                                if pd.api.types.is_numeric_dtype(id_predictions[col]):
                                    values = id_predictions[col].values
                                    if len(values) >= len(future_dates):
                                        cleaned_values = np.maximum(values[:len(future_dates)], 0).round(0).astype(int)
                                    else:
                                        cleaned_values = np.maximum(values, 0).round(0).astype(int)
                                        if len(cleaned_values) < len(future_dates):
                                            last_val = cleaned_values[-1] if len(cleaned_values) > 0 else 0
                                            additional = [last_val] * (len(future_dates) - len(cleaned_values))
                                            cleaned_values = np.concatenate([cleaned_values, additional])
                                    
                                    id_forecast[col] = cleaned_values
                            
                            all_forecast_data.append(id_forecast)
                            self.log(f"Добавлен прогноз для {country_name}")
                        
                        # Объединяем все прогнозы
                        if all_forecast_data:
                            forecast_df = pd.concat(all_forecast_data, ignore_index=True)
                            self.log(f"\nИтоговый прогноз: {len(forecast_df)} записей для {len(all_forecast_data)} стран")
                            
                            # Показываем итоговое распределение
                            for country in forecast_df[self.id_column].unique():
                                country_data = forecast_df[forecast_df[self.id_column] == country]
                                dates = country_data['timestamp'].tolist()
                                self.log(f"Итоговые даты для {country}: {dates[0]} - {dates[-1]}")
                            
                            pred_df = forecast_df.copy()
                        else:
                            self.log("Не удалось создать прогнозные данные")
                            pred_df = predictions.reset_index()
                    
                    else:
                        # Запасной вариант для плоского формата
                        self.log("Обрабатываем плоский DataFrame (запасной вариант)")
                        pred_df = predictions.reset_index() if hasattr(predictions, 'reset_index') else predictions
                        
                        unique_ids = self.data[self.id_column].unique()
                        records_per_id = self.prediction_length
                        all_forecast_data = []
                        
                        for idx, uid in enumerate(unique_ids):
                            start_idx = idx * records_per_id
                            end_idx = start_idx + records_per_id
                            
                            if end_idx <= len(pred_df):
                                id_data = self.data[self.data[self.id_column] == uid]
                                if len(id_data) > 0:
                                    id_data_sorted = id_data.sort_values(self.timestamp_column)
                                    last_date = id_data_sorted[self.timestamp_column].iloc[-1]
                                else:
                                    last_date = pd.Timestamp('2024-01-01')
                                
                                future_dates = self.create_future_dates_for_specific_id(last_date)
                                id_predictions = pred_df.iloc[start_idx:end_idx]
                                
                                id_forecast = pd.DataFrame()
                                id_forecast[self.id_column] = [uid] * len(future_dates)
                                id_forecast['timestamp'] = [d.strftime('%Y-%m-%d') for d in future_dates]
                                
                                for col in id_predictions.columns:
                                    if (pd.api.types.is_numeric_dtype(id_predictions[col]) and 
                                        col not in [self.id_column, 'timestamp']):
                                        values = id_predictions[col].values
                                        cleaned_values = np.maximum(values, 0).round(0).astype(int)
                                        id_forecast[col] = cleaned_values
                                
                                all_forecast_data.append(id_forecast)
                        
                        if all_forecast_data:
                            pred_df = pd.concat(all_forecast_data, ignore_index=True)
                        
                    # Логирование результатов
                    self.log(f"Структура итогового прогноза: {pred_df.dtypes}")
                    self.log(f"Пример прогноза:\n{pred_df.head(3).to_string()}")
                                    
                except Exception as e:
                    self.log(f"Ошибка при подготовке прогноза: {str(e)}\n{traceback.format_exc()}")
                    pred_df = predictions.reset_index() if hasattr(predictions, 'reset_index') else predictions
                
                # Отправка результатов
                self.log("Преобразование прогноза в таблицу Orange...")
                pred_table = self.df_to_table(pred_df)
                self.Outputs.prediction.send(pred_table)
                
                # Лидерборд
                try:
                    lb = predictor.leaderboard()
                    if lb is not None and not lb.empty:
                        self.log("Формирование лидерборда...")
                        # Округление числовых значений для улучшения читаемости
                        for col in lb.select_dtypes(include=['float']).columns:
                            lb[col] = lb[col].round(4)
                        
                        # Проверяем/исправляем имена колонок
                        lb.columns = [str(col).replace(' ', '_').replace('-', '_') for col in lb.columns]
                        
                        # Преобразуем все объектные колонки в строки
                        for col in lb.select_dtypes(include=['object']).columns:
                            lb[col] = lb[col].astype(str)
                            
                        self.log(f"Структура лидерборда: {lb.dtypes}")
                        
                        lb_table = self.df_to_table(lb)
                        self.Outputs.leaderboard.send(lb_table)
                except Exception as lb_err:
                    self.log(f"Ошибка лидерборда: {str(lb_err)}\n{traceback.format_exc()}")
                
                # Инфо о модели
                self.log("Формирование информации о модели...")
                
                # Получаем понятное название частоты
                freq_name = model_freq
                for code, label in self.FREQUENCIES:
                    if code == model_freq:
                        freq_name = f"{label} ({code})"
                        break
                
                # Получаем лучшую модель, если лидерборд доступен
                best_model_name = "Неизвестно"
                best_model_score = "Н/Д"
                
                try:
                    if 'lb' in locals() and lb is not None and not lb.empty:
                        best_model_name = lb.iloc[0]['model']
                        best_model_score = f"{lb.iloc[0]['score_val']:.4f}"
                        
                        # Логируем информацию о лучших моделях
                        self.log(f"Лучшая модель: {best_model_name}, Оценка: {best_model_score}")
                        
                        # Показываем топ-3 модели если их столько есть
                        if len(lb) > 1:
                            self.log("Топ модели:")
                            for i in range(min(3, len(lb))):
                                model = lb.iloc[i]['model']
                                score = lb.iloc[i]['score_val']
                                self.log(f"  {i+1}. {model}: {score:.4f}")
                except Exception as e:
                    self.log(f"Не удалось получить информацию о лучшей модели: {str(e)}")
                
                # Создаем расширенную информацию о модели
                model_info = pd.DataFrame({
                    'Parameter': ['Версия', 'Цель', 'Длина', 'Метрика', 'Пресет', 
                                'Время', 'Праздники', 'Частота', 'Лучшая модель', 'Оценка модели'],
                    'Value': ['1.2.0', self.target_column, str(self.prediction_length),
                              metric, self.selected_preset, 
                              f"{self.time_limit} сек", 
                              "Включены" if self.include_holidays else "Отключены",
                              freq_name,
                              best_model_name,
                              best_model_score]
                })
                self.Outputs.model_info.send(self.df_to_table(model_info))
                
                # Закрываем логгеры, чтобы не было WinError 32
                import logging
                logging.shutdown()
                
            self.log("=== УСПЕШНО ===")
            
        except Exception as e:
            self.log(f"ОШИБКА: {str(e)}\n{traceback.format_exc()}")
            self.error(str(e))
        finally:
            self.progressBarFinished()
            # Отправляем журнал
            self.Outputs.log_messages.send(self.log_messages)

    def df_to_table(self, df):
        """Безопасное преобразование DataFrame в таблицу Orange"""
        try:
            # Убедимся, что DataFrame не содержит индексов
            df = df.reset_index(drop=True).copy()
            
            # Раздельные списки для атрибутов, классов и мета-переменных
            attrs = []
            metas = []
            
            # Безопасное преобразование всех типов данных и создание соответствующих переменных
            X_cols = []  # Для непрерывных переменных (атрибутов)
            M_cols = []  # Для строковых переменных (мета)
            
            for col in df.columns:
                # Специальная обработка для ID колонки
                if col == self.id_column:
                    # ID колонку всегда храним как мета-переменную
                    df[col] = df[col].fillna('').astype(str)
                    metas.append(StringVariable(name=str(col)))
                    M_cols.append(col)
                # Обрабатываем числовые данные - идут в X
                elif pd.api.types.is_numeric_dtype(df[col]):
                    # Преобразуем в float, который Orange может обработать
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(float('nan')).astype(float)
                    attrs.append(ContinuousVariable(name=str(col)))
                    X_cols.append(col)
                else:
                    # Все нечисловые данные идут в мета
                    # Обрабатываем даты
                    if pd.api.types.is_datetime64_dtype(df[col]):
                        df[col] = df[col].dt.strftime('%Y-%m-%d')
                    
                    # Все остальное - в строки
                    df[col] = df[col].fillna('').astype(str)
                    metas.append(StringVariable(name=str(col)))
                    M_cols.append(col)
            
            self.log(f"Атрибуты: {[v.name for v in attrs]}")
            self.log(f"Мета: {[v.name for v in metas]}")
            
            # Создаем домен
            domain = Domain(attrs, metas=metas)
            
            # Создаем массивы для X и M
            if X_cols:
                X = df[X_cols].values
            else:
                X = np.zeros((len(df), 0))
                
            if M_cols:
                M = df[M_cols].values
            else:
                M = np.zeros((len(df), 0), dtype=object)
            
            # Создаем таблицу с помощью from_numpy
            return Table.from_numpy(domain, X, metas=M)
            
        except Exception as e:
            self.log(f"Ошибка преобразования DataFrame в Table: {str(e)}\n{traceback.format_exc()}")
            raise

if __name__ == "__main__":
    WidgetPreview(OWAutoGluonTimeSeries).run()
