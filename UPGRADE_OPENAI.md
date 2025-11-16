# Upgrade OpenAI SDK

The backend requires OpenAI SDK version 1.55.0 or higher to use the Responses API.

## To upgrade:

1. **If using a virtual environment:**
   ```bash
   source .venv/bin/activate  # or venv/bin/activate
   pip install --upgrade "openai>=1.55.0"
   ```

2. **If using system Python:**
   ```bash
   pip install --upgrade "openai>=1.55.0"
   ```

3. **Or reinstall all dependencies:**
   ```bash
   pip install -r requirements.txt --upgrade
   ```

4. **Restart the backend server** after upgrading.

## Verify the upgrade:

```bash
python -c "import openai; print(openai.__version__); from openai import OpenAI; client = OpenAI(api_key='test'); print('Has responses:', hasattr(client, 'responses'))"
```

You should see version 1.55.0 or higher and `Has responses: True`.

