from mindbank_poc.core.schemas.onboarding import OnboardingStepInfo

TELEGRAM_ONBOARDING_STEPS = [
    OnboardingStepInfo(
        step_id="api_id_hash",
        description="Введите api_id и api_hash от my.telegram.org",
        input_schema={
            "type": "object",
            "properties": {
                "api_id": {"type": "integer", "description": "API ID"},
                "api_hash": {"type": "string", "description": "API Hash"}
            },
            "required": ["api_id", "api_hash"]
        },
        messages=["Получите api_id и api_hash на https://my.telegram.org"],
        is_final_step=False
    ),
    OnboardingStepInfo(
        step_id="phone",
        description="Введите номер телефона Telegram",
        input_schema={
            "type": "object",
            "properties": {
                "phone": {"type": "string", "description": "Телефон в формате +38099124567"}
            },
            "required": ["phone"]
        },
        messages=["Введите номер телефона, привязанный к Telegram"],
        is_final_step=False
    ),
    OnboardingStepInfo(
        step_id="code",
        description="Введите код подтверждения из Telegram",
        input_schema={
            "type": "object",
            "properties": {
                "code": {"type": "string", "description": "Код из Telegram"}
            },
            "required": ["code"]
        },
        messages=["Введите код, который пришёл в Telegram"],
        is_final_step=False
    ),
    OnboardingStepInfo(
        step_id="password",
        description="Введите пароль двухфакторной аутентификации (если требуется)",
        input_schema={
            "type": "object",
            "properties": {
                "password": {"type": "string", "description": "Пароль Telegram"}
            },
            "required": ["password"]
        },
        messages=["Введите пароль, если включена двухфакторная аутентификация"],
        is_final_step=False
    ),
    OnboardingStepInfo(
        step_id="done",
        description="Онбординг завершён, сессия создана",
        input_schema=None,
        messages=["Сессия Telegram успешно создана!"],
        is_final_step=True
    ),
]

TELEGRAM_ONBOARDING_STEP_MAP = {step.step_id: step for step in TELEGRAM_ONBOARDING_STEPS}