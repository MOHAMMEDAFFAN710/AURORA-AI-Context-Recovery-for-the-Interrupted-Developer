from typing import Dict


def generate(kind: str, name: str | None = None, language: str | None = None) -> Dict[str, str]:
    k = (kind or "").lower()
    lang = (language or "python").lower()
    nm = name or "sample"
    if k == "rest-api" and lang == "python":
        content = (
            "from fastapi import FastAPI, Depends\n"
            "app = FastAPI()\n"
            "@app.get('/health')\n"
            "async def health():\n"
            "    return {'status': 'ok'}\n"
        )
        return {"name": f"{nm}_api.py", "language": "python", "content": content}
    if k == "auth-middleware" and lang == "python":
        content = (
            "from fastapi import Request\n"
            "from starlette.middleware.base import BaseHTTPMiddleware\n"
            "class AuthMiddleware(BaseHTTPMiddleware):\n"
            "    async def dispatch(self, request: Request, call_next):\n"
            "        token = request.headers.get('authorization')\n"
            "        response = await call_next(request)\n"
            "        return response\n"
        )
        return {"name": f"{nm}_auth.py", "language": "python", "content": content}
    if k == "rest-api" and lang in {"node", "javascript", "js"}:
        content = (
            "const express = require('express');\n"
            "const app = express();\n"
            "app.get('/health', (req, res) => res.json({ status: 'ok' }));\n"
            "module.exports = app;\n"
        )
        return {"name": f"{nm}_api.js", "language": "javascript", "content": content}
    return {"name": f"{nm}.{lang}", "language": lang, "content": ""}
