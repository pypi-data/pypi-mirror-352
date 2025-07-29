import aiohttp
import asyncio
import json
from typing import Any, Dict, List, Optional
from aiohttp.client_exceptions import ClientResponseError

from .async_http_client import get_async, post_async
from .azure_ai_language_job_responses import KeyPhraseJobResponse, SentimentAnalysisJobResponse


async def _post_text_analytics(
    endpoint: str, key: str, payload: dict, max_retries: int = 10, backoff: float = 1.0
) -> Optional[Dict[str, Any]]:
    """
    Generic call to the Analyze-Text API.
    """
    url = f"{endpoint}/language/:analyze-text?api-version=2024-11-01"
    headers = {
        "Content-Type": "application/json",
        "Ocp-Apim-Subscription-Key": key,
    }

    for attempt in range(1, max_retries + 1):
        try:
            resp = await post_async(url, json=payload, headers=headers)
            if resp.success:
                return resp.content
            else:
                return None
        except ClientResponseError as e:
            if e.status == 429:  # Too Many Requests
                if attempt < max_retries:
                    print(
                        f"[ERROR] __post_text_analytics failed (attempt {attempt+1}/{max_retries}): {e}"
                    )
                    await asyncio.sleep(backoff * (2 ** (attempt - 1)))
                else:
                    # all retries failed
                    raise
            else:
                # Raise other exceptions immediately
                raise
        except Exception:
            raise


async def _post_text_analytics_job(
    endpoint: str, key: str, payload: dict, max_retries: int = 10, backoff: float = 1.0
) -> Optional[str]:
    """
    Generic call to the Analyze-Text API. Returns the operation location header.
    """
    url = f"{endpoint}/language/analyze-text/jobs?api-version=2024-11-01"
    headers = {
        "Content-Type": "application/json",
        "Content-Length": str(len(json.dumps(payload))),
        "Ocp-Apim-Subscription-Key": key,
    }

    for attempt in range(1, max_retries + 1):
        try:
            resp = await post_async(url, json=payload, headers=headers)
            if resp.success:
                return resp.headers.get("operation-location", "")
            else:
                return None
        except ClientResponseError as e:
            if e.status == 429:  # Too Many Requests
                if attempt < max_retries:
                    print(
                        f"[ERROR] __post_text_analytics_job failed (attempt {attempt+1}/{max_retries}): {e}"
                    )
                    await asyncio.sleep(backoff * (2 ** (attempt - 1)))
                else:
                    # all retries failed
                    raise
            else:
                # Raise other exceptions immediately
                raise
        except Exception:
            raise


async def _get_text_analytics_job_result(
    operation_location: str,
    key: str,
    max_retries: int = 10,
    backoff: float = 1.0,
) -> Optional[Dict[str, Any]]:
    """
    Get the result of a text analytics job.
    """
    headers = {
        "Content-Type": "application/json",
        "Ocp-Apim-Subscription-Key": key,
    }

    last_exc = None
    for attempt in range(1, max_retries + 1):
        try:
            resp = await get_async(operation_location, headers=headers)
            if resp.success:
                return resp.content
            else:
                return None
        except Exception as ex:
            last_exc = ex
            if attempt < max_retries:
                await asyncio.sleep(backoff * (2 ** (attempt - 1)))
            else:
                # all retries failed
                raise RuntimeError(
                    f"get_text_analytics_job_result failed after {max_retries} attempts"
                ) from last_exc


async def detect_language(endpoint: str, key: str, id: str, text: str) -> Dict[str, str]:
    """
    Call the Analyze-Text LanguageDetection task
    """
    try:
        payload = {
            "kind": "LanguageDetection",
            "parameters": {"modelVersion": "latest"},
            "analysisInput": {"documents": [{"id": id, "text": text[:5120]}]},
        }

        resp = await _post_text_analytics(endpoint, key, payload)
        if not resp:
            return {
                "id": id,
                "language": "en",  # default to english if no response
            }

        lang = resp["results"]["documents"][0]["detectedLanguage"]["iso6391Name"]
        return {
            "id": id,
            "detectedLanguage": lang,
        }
    except Exception as e:
        print(f"[ERROR] detect_language failed for id {id}: {e}")
        raise


async def detect_languages_bulk(
    endpoint: str,
    key: str,
    conversations: List[Dict[str, str]],
    id_column_name: str = "conversation_id",
    text_column_name: str = "messages",
) -> List[Dict[str, str]]:
    async with aiohttp.ClientSession():
        tasks = [
            detect_language(
                endpoint,
                key,
                row[id_column_name],
                row[text_column_name],
            )
            for row in conversations
        ]
        return await asyncio.gather(*tasks)


async def get_key_phrases(
    endpoint: str,
    key: str,
    id: str,
    text: str,
    language: str,
) -> Dict[str, Any]:
    """
    Call the Analyze-Text KeyPhraseExtraction task.
    """
    try:
        payload = {
            "kind": "KeyPhraseExtraction",
            "analysisInput": {"documents": [{"id": id, "language": language, "text": text}]},
            "tasks": [
                {
                    "kind": "KeyPhraseExtraction",
                    "parameters": {"modelVersion": "latest"},
                }
            ]
        }

        operation_location = await _post_text_analytics_job(endpoint, key, payload)
        if not operation_location:
            return {
                "id": id,
                "keyPhrases": [],
            }

        results = None
        while True:
            job_result = await _get_text_analytics_job_result(
                operation_location=operation_location,
                key=key,
            )
            if not job_result:
                raise RuntimeError(
                    f"get_key_phrases failed to get job result for id {id}"
                )

            job_response = KeyPhraseJobResponse(**job_result)
            # print(f"get_key_phrases: job {job_response.jobId} status: {job_response.status}")

            if job_response.status in ["notStarted", "running"]:
                await asyncio.sleep(5)
                continue

            if job_response.status == "succeeded":
                results = job_response.tasks.items[0].results
                break
            elif job_response.status == "failed":
                raise RuntimeError(
                    f"get_key_phrases failed for id {id}: {job_response.errors}"
                )

        if not results:
            return {
                "id": id,
                "keyPhrases": [],
            }

        return {
            "id": id,
            "keyPhrases": results.documents[0].keyPhrases if results.documents else [],
        }
    except Exception as e:
        print(f"[ERROR] get_key_phrases: {e}")
        raise


async def get_key_phrases_bulk(
    endpoint: str,
    key: str,
    conversations: List[Dict[str, str]],
    id_column_name: str = "conversation_id",
    text_column_name: str = "messages",
    language_column_name: str = "detected_language",
) -> List[Dict[str, Any]]:
    async with aiohttp.ClientSession():
        tasks = [
            get_key_phrases(
                endpoint=endpoint,
                key=key,
                id=row[id_column_name],
                text=row[text_column_name],
                language=row[language_column_name],
            )
            for row in conversations
        ]
        return await asyncio.gather(*tasks)


async def get_sentiment_analysis(
    endpoint: str,
    key: str,
    id: str,
    text: str,
    language: str,
) -> Dict[str, Any]:
    """
    Call the Analyze-Text SentimentAnalysis task.
    """
    try:
        payload = {
            "kind": "SentimentAnalysis",
            "analysisInput": {"documents": [{"id": id, "language": language, "text": text}]},
            "tasks": [
                {
                    "kind": "SentimentAnalysis",
                    "parameters": {"modelVersion": "latest"},
                }
            ]
        }

        operation_location = await _post_text_analytics_job(endpoint, key, payload)
        if not operation_location:
            return {
                "id": id,
                "positive": None,
                "neutral": None,
                "negative": None,
            }

        results = None
        while True:
            job_result = await _get_text_analytics_job_result(
                operation_location=operation_location,
                key=key,
            )
            if not job_result:
                raise RuntimeError(
                    f"get_sentiment_analysis failed to get job result for id {id}"
                )

            job_response = SentimentAnalysisJobResponse(**job_result)
            # print(f"get_sentiment_analysis: job {job_response.jobId} status: {job_response.status}")

            if job_response.status in ["notStarted", "running"]:
                await asyncio.sleep(5)
                continue

            if job_response.status == "succeeded":
                results = job_response.tasks.items[0].results
                break
            elif job_response.status == "failed":
                raise RuntimeError(
                    f"get_key_phrases failed for id {id}: {job_response.errors}"
                )

        if not results:
            return {
                "id": id,
                "positive": None,
                "neutral": None,
                "negative": None,
            }

        scores = results.documents[0].confidenceScores
        return {
            "id": id,
            "positive": scores.positive,
            "neutral": scores.neutral,
            "negative": scores.negative,
        }
    except Exception as e:
        print(f"[ERROR] get_sentiment_analysis id {id}: {e}")
        raise


async def get_sentiment_analysis_bulk(
    endpoint: str,
    key: str,
    conversations: List[Dict[str, str]],
    id_column_name: str = "conversation_id",
    text_column_name: str = "messages",
    language_column_name: str = "detected_language",
) -> List[Dict[str, Any]]:
    async with aiohttp.ClientSession():
        tasks = [
            get_sentiment_analysis(
                endpoint=endpoint,
                key=key,
                id=row[id_column_name],
                text=row[text_column_name],
                language=row[language_column_name],
            )
            for row in conversations
        ]
        return await asyncio.gather(*tasks)
