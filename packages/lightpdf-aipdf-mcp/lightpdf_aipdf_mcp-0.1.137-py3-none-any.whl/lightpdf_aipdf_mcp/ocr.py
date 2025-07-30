from dataclasses import dataclass
import os
import httpx
from typing import Optional, Dict, Any
from .common import Logger, BaseResult, FileHandler, BaseApiClient

@dataclass
class OcrResult(BaseResult):
    """OCR结果数据类"""
    pass

class OcrClient(BaseApiClient):
    """文档OCR识别器"""
    def __init__(self, logger: Logger, file_handler: FileHandler):
        super().__init__(logger, file_handler)
        api_endpoint = os.getenv("API_ENDPOINT", "techsz.aoscdn.com/api")
        self.api_base_url = f"https://{api_endpoint}/tasks/document/ocr"

    async def ocr_document(self, file_path: str, format: str = "pdf", password: Optional[str] = None, original_name: Optional[str] = None, language: Optional[str] = None) -> OcrResult:
        if not self.api_key:
            await self.logger.error("未找到API_KEY。请在客户端配置API_KEY环境变量。")
            return OcrResult(success=False, file_path=file_path, error_message="未找到API_KEY", original_name=original_name)

        # 构建API参数
        extra_params = {
            "format": format or "pdf"
        }
        if language:
            extra_params["language"] = language
        else:
            extra_params["language"] = "English,Digits,ChinesePRC"
        if password:
            extra_params["password"] = password
        if original_name:
            extra_params["filename"] = os.path.splitext(original_name)[0]

        async with httpx.AsyncClient(timeout=3600.0) as client:
            task_id = None
            try:
                # 创建OCR任务
                task_id = await self._create_task(client, file_path, extra_params)
                # 等待任务完成
                download_url = await self._wait_for_task(client, task_id, "OCR识别")

                await self.logger.log("info", "OCR识别完成。可通过下载链接获取结果文件。")
                return OcrResult(
                    success=True,
                    file_path=file_path,
                    error_message=None,
                    download_url=download_url,
                    original_name=original_name,
                    task_id=task_id
                )
            except Exception as e:
                return OcrResult(
                    success=False,
                    file_path=file_path,
                    error_message=str(e),
                    download_url=None,
                    original_name=original_name,
                    task_id=task_id
                )

    async def _create_task(self, client: httpx.AsyncClient, file_path: str, extra_params: dict = None) -> str:
        await self.logger.log("info", "正在提交OCR任务...")
        headers = {"X-API-KEY": self.api_key}
        data = {}
        if extra_params:
            data.update(extra_params)
        # 检查是否为OSS路径
        if self.file_handler.is_oss_id(file_path):
            data["resource_id"] = file_path.split("oss_id://")[1]
            headers["Content-Type"] = "application/json"
            response = await client.post(
                self.api_base_url,
                json=data,
                headers=headers
            )
        elif self.file_handler.is_url(file_path):
            data["url"] = file_path
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
        return await self._handle_api_response(response, "创建OCR任务") 