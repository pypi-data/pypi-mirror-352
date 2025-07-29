from datetime import datetime
from typing import Dict, Any, Optional, Literal, List
from pydantic import BaseModel, Field
import uuid
import secrets
import copy
from mindbank_poc.common.logging import get_logger

class ConnectorStage(str):
    """Этапы жизненного цикла коннектора (новая модель)."""
    SETUP = "setup"          # Начальная настройка (старое, возможно, удалить или переименовать)
    SETUP_REQUIRED = "setup_required" # Ожидает выполнения сложной первоначальной настройки коннектором
    CONFIGURATION = "configuration"  # Настройка параметров
    READY = "ready"          # Готов к работе
    DISABLED = "disabled"    # Отключен
    DONE = "done"            # Завершен

class ConnectorMessage(BaseModel):
    """Сообщение от коннектора."""
    level: str  # info, warning, error
    text: str

class ConfigValidation(BaseModel):
    """Результат валидации конфигурации."""
    valid: bool = True
    errors: List[str] = Field(default_factory=list)
    missing_fields: List[Dict[str, str]] = Field(default_factory=list)
    invalid_fields: List[Dict[str, str]] = Field(default_factory=list)

class Connector(BaseModel):
    """Модель коннектора в системе."""
    connector_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: str
    metadata: Dict[str, Any]
    config_schema: Dict[str, Any]
    config: Dict[str, Any] = Field(default_factory=dict)
    
    # Поля для нового флоу конфигурации
    setup_url: Optional[str] = None
    setup_instructions: Optional[str] = None
    
    # Динамические опции, предоставляемые коннектором
    dynamic_options: Dict[str, Any] = Field(default_factory=dict)
    dynamic_options_updated_at: Optional[datetime] = None
    
    # Основные поля согласно ТЗ
    stage: str = ConnectorStage.CONFIGURATION # Начальное значение по умолчанию
    config_validation: ConfigValidation = Field(default_factory=ConfigValidation)
    messages: List[ConnectorMessage] = Field(default_factory=list)
    capabilities: List[str] = Field(default_factory=list)
    supported_archetypes: List[str] = Field(default_factory=list, description="Список поддерживаемых архитипов данных")
    enabled: bool = True
    
    # Поля для аутентификации
    access_token: str = Field(default_factory=lambda: secrets.token_urlsafe(32))
    previous_token: Optional[str] = None
    token_updated_at: datetime = Field(default_factory=datetime.now)
    
    # Служебные поля
    last_handshake: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    def update_stage(self, new_stage: str):
        """Обновляет этап жизненного цикла коннектора."""
        self.stage = new_stage
        self.updated_at = datetime.now()
    
    def update_config(self, new_config: Dict[str, Any]):
        """
        Обновляет конфигурацию коннектора.
        Генерирует новый токен доступа и сохраняет старый.
        Этап и валидность конфигурации будут обновлены в сервисе.
        """
        self.config = new_config
        # self.rotate_token()
        self.updated_at = datetime.now()
    
    def update_partial_config(self, partial_config: Dict[str, Any]):
        """
        Обновляет часть конфигурации коннектора.
        Этап и валидность конфигурации будут обновлены в сервисе.
        """
        for key, value in partial_config.items():
            if isinstance(value, dict) and key in self.config and isinstance(self.config[key], dict):
                self.config[key].update(value)
            else:
                self.config[key] = value
        
        self.updated_at = datetime.now()
    
    def validate_config(self) -> ConfigValidation:
        """
        Проверяет валидность текущей конфигурации на основе config_schema.
        Проверяет наличие всех обязательных полей и их типы.
        
        Returns:
            ConfigValidation с результатами проверки
        """
        config_to_validate = copy.deepcopy(self.config)
        # logger = get_logger("ConnectorModel") # Логгер уже есть на уровне модуля, если он там объявлен
        # logger.info(f"[VALIDATE_CONFIG_DEBUG] Inside validate_config for {self.connector_id}. Original self.config: {self.config}")
        # logger.info(f"[VALIDATE_CONFIG_DEBUG] Using config_to_validate: {config_to_validate}")

        validation = ConfigValidation(valid=True)
        properties = self.config_schema.get('properties', {})
        required_fields = self.config_schema.get('required', [])
        
        missing = []
        for field in required_fields:
            # Используем config_to_validate вместо self.config
            if field not in config_to_validate or config_to_validate.get(field) is None:
                missing.append({"field": field, "error": "Field is required but missing"})
                validation.errors.append(f"Missing required field: {field}")
        
        invalid = []
        # Используем config_to_validate.items() вместо self.config.items()
        for field_name, field_value in config_to_validate.items():
            if field_name in properties and 'type' in properties[field_name]:
                expected_type = properties[field_name]['type']
                actual_type_name = type(field_value).__name__
                error_message = None

                if expected_type == 'string' and not isinstance(field_value, str):
                    error_message = f"Expected string, got {actual_type_name}"
                elif expected_type == 'integer' and not isinstance(field_value, int):
                    error_message = f"Expected integer, got {actual_type_name}"
                elif expected_type == 'number' and not isinstance(field_value, (int, float)):
                    error_message = f"Expected number, got {actual_type_name}"
                elif expected_type == 'boolean' and not isinstance(field_value, bool):
                    error_message = f"Expected boolean, got {actual_type_name}"
                elif expected_type == 'array' and not isinstance(field_value, list):
                    error_message = f"Expected array, got {actual_type_name}"
                elif expected_type == 'object' and not isinstance(field_value, dict):
                    error_message = f"Expected object, got {actual_type_name}"
                
                if error_message:
                    invalid.append({"field": field_name, "error": error_message})
                    validation.errors.append(f"Invalid field type: {field_name} - {error_message}")

        if missing or invalid:
            validation.valid = False
            validation.missing_fields = missing
            validation.invalid_fields = invalid
        
        # logger.info(f"[VALIDATE_CONFIG_DEBUG] Returning validation: {validation.model_dump()}, self.config after validation: {self.config}")
        return validation
    
    def reset_config(self):
        """Сбрасывает runtime-конфигурацию и переводит в этап configuration."""
        self.config = {}
        self.config_validation = ConfigValidation()
        self.update_stage(ConnectorStage.CONFIGURATION)
        # self.rotate_token()
    
    def reset_setup(self):
        """Сбрасывает всю настройку и переводит в этап setup или setup_required."""
        self.config = {}
        self.config_validation = ConfigValidation()
        # self.steps = [] # Удаляем, т.к. steps удалено
        # Логика установки stage должна быть в сервисе, т.к. зависит от наличия setup_url
        # Пока установим в CONFIGURATION, сервис должен будет решить правильный stage.
        self.update_stage(ConnectorStage.CONFIGURATION) # Временно, сервис уточнит
        self.enabled = False
        # self.rotate_token()
    
    def toggle(self, enabled: bool):
        """Включает или выключает коннектор."""
        self.enabled = enabled
        
        if not enabled:
            self.update_stage(ConnectorStage.DISABLED)
        else:
            if self.stage == ConnectorStage.DISABLED: # или был SETUP_REQUIRED и теперь конфиг есть
                # Логика восстановления stage после включения.
                # all_steps_done = all(step.status == StepStatus.DONE for step in self.steps) # Удаляем логику со steps
                # if not self.steps or not all_steps_done: # Удаляем
                #     self.update_stage(ConnectorStage.SETUP)
                # Вместо старой логики со steps, проверяем:
                # Если есть setup_url и конфига все еще нет (или он невалиден) -> SETUP_REQUIRED (или CONFIGURATION)
                # Это должно решаться в сервисе, который имеет полный контекст.
                # Здесь упрощенно: если конфиг не валиден -> CONFIGURATION, иначе READY
                if not self.validate_config().valid:
                    self.update_stage(ConnectorStage.CONFIGURATION)
                else:
                    self.update_stage(ConnectorStage.READY)
        self.updated_at = datetime.now()
    
    def add_message(self, level: str, text: str):
        """Добавляет сообщение в список сообщений."""
        self.messages.append(ConnectorMessage(level=level, text=text))
        if len(self.messages) > 10:
            self.messages = self.messages[-10:]
    
    def clear_messages(self):
        """Очищает список сообщений."""
        self.messages = []
    
    def rotate_token(self):
        """Генерирует новый токен доступа и сохраняет старый в previous_token."""
        self.previous_token = self.access_token
        self.access_token = secrets.token_urlsafe(32)
        self.token_updated_at = datetime.now()
        self.updated_at = datetime.now()
    
    def verify_token(self, token: str) -> bool:
        """Проверяет, соответствует ли предоставленный токен текущему токену доступа."""
        return token == self.access_token
    
    def verify_any_token(self, token: str) -> bool:
        """Проверяет, соответствует ли предоставленный токен текущему или предыдущему токену."""
        is_current = self.verify_token(token)
        is_previous = self.previous_token is not None and token == self.previous_token
        return is_current or is_previous
    
    def record_handshake(self):
        """Записывает время последнего рукопожатия."""
        self.last_handshake = datetime.now()
        self.updated_at = datetime.now()
    
    def check_timeout(self, timeout_seconds: int) -> bool:
        if not self.last_handshake:
            if (datetime.now() - self.created_at).total_seconds() > timeout_seconds:
                 return True
            return False
            
        elapsed = (datetime.now() - self.last_handshake).total_seconds()
        return elapsed > timeout_seconds
    
    def update_dynamic_options(self, new_options: Dict[str, Any], new_schema: Optional[Dict[str, Any]] = None):
        """
        Обновляет динамические опции конфигурации, предоставленные коннектором.
        Также может обновить схему конфигурации, если она была предоставлена.
        
        Args:
            new_options: Новые динамические опции
            new_schema: Новая схема конфигурации (опционально)
        """
        self.dynamic_options = new_options
        self.dynamic_options_updated_at = datetime.now()
        
        # Если предоставлена новая схема, обновляем config_schema
        if new_schema is not None:
            self.config_schema = new_schema
            
        self.updated_at = datetime.now()
