from dataclasses import dataclass
import os
import httpx
from typing import Optional
from .common import Logger, BaseResult, FileHandler, BaseApiClient

@dataclass
class SummarizeResult(BaseResult):
    """摘要结果数据类，结构与 TranslateResult 完全一致"""
    summary: Optional[str] = None

class Summarizer(BaseApiClient):
    """PDF文档摘要器，结构与 Translator 完全一致"""
    def __init__(self, logger: Logger, file_handler: FileHandler):
        super().__init__(logger, file_handler)

    async def summarize_pdf(self, file_path: str, prompt: str, language: Optional[str] = None, password: Optional[str] = None, original_name: Optional[str] = None) -> SummarizeResult:
        if not self.api_key:
            await self.logger.error("未找到API_KEY。请在客户端配置API_KEY环境变量。")
            return SummarizeResult(success=False, file_path=file_path, error_message="未找到API_KEY", original_name=original_name)

        # 构建API参数
        extra_params = {
            "po": "lightpdf"
        }
        if password:
            extra_params["password"] = password
        if original_name:
            extra_params["filename"] = os.path.splitext(original_name)[0]

        async with httpx.AsyncClient(timeout=3600.0) as client:
            task_id = None
            headers = {"X-API-KEY": self.api_key}
            try:
                # Phase 1: Embedding
                response_action="摘要任务1"
                self.api_base_url = f"https://{self.api_endpoint}/tasks/llm/embedding"

                data = extra_params.copy() if extra_params else {}

                await self.logger.log("info", f"正在提交{response_action}...{data}")
                # 检查是否为OSS路径
                if self.file_handler.is_oss_id(file_path):
                    data = data.copy()
                    data["resource_id"] = file_path.split("oss_id://")[1]
                    headers["Content-Type"] = "application/json"
                    response = await client.post(
                        self.api_base_url,
                        json=data,
                        headers=headers
                    )
                elif self.file_handler.is_url(file_path):
                    file_path_mod = file_path
                    if isinstance(file_path, str) and "arxiv.org/pdf/" in file_path:
                        from urllib.parse import urlparse, urlunparse
                        url_obj = urlparse(file_path)
                        if not url_obj.path.endswith(".pdf"):
                            new_path = url_obj.path + ".pdf"
                            file_path_mod = urlunparse(url_obj._replace(path=new_path))
                    data = data.copy()
                    data["url"] = file_path_mod
                    headers["Content-Type"] = "application/json"
                    response = await client.post(
                        self.api_base_url,
                        json=data,
                        headers=headers
                    )
                else:
                    with open(file_path, "rb") as f:
                        files = {"file": f}
                        response = await client.post(
                            self.api_base_url,
                            files=files,
                            data=data,
                            headers=headers
                        )

                task_id = await self._handle_api_response(response, response_action)
                await self.logger.log("info", f"摘要任务1，task_id: {task_id}")

                file_hash = await self._wait_for_task(client, task_id, "摘要1")

                # Phase 2: Summarize
                response_action="摘要任务2"
                self.api_base_url = f"https://{self.api_endpoint}/tasks/llm/conversation"

                data = extra_params.copy() if extra_params else {}
                data["template_id"] = "63357fa3-ba37-47d5-b9c3-8b10ed0a59d6"
                data["response_type"] = 4
                data["file_hash"] = file_hash
                data["prompt"] = prompt
                data["language"] = language

                await self.logger.log("info", f"正在提交{response_action}...{data}")
                response = await client.post(
                    self.api_base_url,
                    json=data,
                    headers=headers
                )

                task_id = await self._handle_api_response(response, response_action)
                await self.logger.log("info", f"摘要任务2，task_id: {task_id}")

                content = await self._wait_for_task(client, task_id, "摘要2", is_raw=True)

                summary = content.get("answer", {}).get("text", "")

                await self.logger.log("info", f"摘要完成。")
                return SummarizeResult(
                    success=True,
                    file_path=file_path,
                    error_message=None,
                    summary=summary,
                    original_name=original_name,
                    task_id=task_id
                )
            except Exception as e:
                return SummarizeResult(
                    success=False,
                    file_path=file_path,
                    error_message=str(e),
                    summary=None,
                    original_name=original_name,
                    task_id=task_id
                )