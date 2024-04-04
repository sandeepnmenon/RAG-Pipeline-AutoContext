# RAG-Pipeline-AutoContext
1. Activate the environment
2. Create the `.env` file in the root directory and add the following variables:
```bash
OPENAI_API_KEY='sk-<your-openai-api-key>'
LOCAL_DB_PATH='local.sqlite'
```
3. 
```bash
uvicorn src.app:app --reload --port 8010
```