import os
import re
import json
import logging
import sys
import uuid
from typing import List, Optional
import boto3

import tornado
import tornado.web
from jupyter_server.base.handlers import APIHandler

from pydantic import BaseModel, Field

# Configuring the logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Create a handler for the standard output (stdout)
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)

# Log formatter
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
console_handler.setFormatter(formatter)

# Add the handler to the logger
logger.addHandler(console_handler)


class Summary(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    podName: str
    usage: Optional[float] = None
    cost: Optional[float] = None
    project: str
    lastUpdate: str
    year: int
    month: str


class SummaryList(BaseModel):
    summaries: List[Summary]


class Detail(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    podName: str
    creationTimestamp: str
    deletionTimestamp: str
    cpuLimit: str
    memoryLimit: str
    gpuLimit: str
    volumes: str
    namespace: str
    notebook_duration: str
    session_cost: float
    instance_id: str
    instance_type: str
    region: str
    pricing_type: str
    cost: float
    instanceRAM: int
    instanceCPU: int
    instanceGPU: int
    instanceId: str


class DetailList(BaseModel):
    details: List[Detail]


class LogsHandler(APIHandler):
    @tornado.web.authenticated
    def get(self):
        logger.info("Getting usages and cost stats")
        try:
            # Verificar que las variables de entorno necesarias están definidas
            required_env_vars = ["OSS_S3_BUCKET_NAME", "OSSPI", "OSSProject"]
            for var in required_env_vars:
                if var not in os.environ:
                    raise EnvironmentError(
                        f"Missing required environment variable: {var}"
                    )

            bucket_path = os.environ["OSS_S3_BUCKET_NAME"]
            osspi = os.environ.get("OSSPI", "No")
            oss_project = os.environ.get("OSSProject", "").strip()

            full_url = self.request.full_url()
            full_url = "http://localhost:63118/user/yovian/jupyterlab-resource-tracker"
            match = re.search("(\/user\/)(.*)(\/jupyterlab-resource-tracker)", full_url)
            username = match.group(2)

            # Extraer bucket y prefijo a partir de una sola variable
            try:
                bucket_name, prefix = bucket_path.split("/", 1)
            except ValueError:
                raise EnvironmentError(f"Variable OSS_S3_BUCKET_NAME inválida; debe tener formato 'bucket/prefijo': {bucket_path}")

            logs = self.load_logs_from_s3_folder(bucket_name, prefix, osspi, oss_project, username)

            for log in logs:
                if "cost" in log and log["cost"] is None:
                    log["cost"] = 0.0
                if "usage" in log and log["usage"] is None:
                    log["usage"] = 0.0
            summary_list = SummaryList(summaries=logs)

        except FileNotFoundError as e:
            logger.error("Log file not found: %s", e)
            self.set_status(404)
            self.finish(json.dumps({"error": "Required log file not found."}))
        except EnvironmentError as e:
            logger.error("Environment configuration error: %s", e)
            self.set_status(500)
            self.finish(json.dumps({"error": str(e)}))
        except json.JSONDecodeError as e:
            logger.error("Invalid JSON format in log file: %s", e)
            self.set_status(400)
            self.finish(json.dumps({"error": "Invalid log file format."}))

        self.set_status(200)
        self.finish(
            json.dumps(
                {
                    "summary": [s.model_dump() for s in summary_list.summaries],
                    "details": [],
                }
            )
        )

    def load_logs_from_s3_folder(
        self, bucket: str, prefix: str, osspi: str, oss_project: str, username: str
    ) -> list:
        """
        Lista todos los objetos en S3 bajo el prefijo dado y procesa cada archivo JSONL.
        Filtra por proyecto y, si OSSPI == "No", por podName == jupyter-{username}.
        """
        data = []
        s3_client = boto3.client("s3")
        try:
            # Paginador para listar todos los objetos bajo el prefijo
            paginator = s3_client.get_paginator("list_objects_v2")
            page_iterator = paginator.paginate(Bucket=bucket, Prefix=prefix)
            
            for page in page_iterator:
                for obj in page.get("Contents", []):
                    key = obj["Key"]
                    # Sólo procesar archivos que terminen en .log o .jsonl si se desea
                    if not key.endswith(".log") and not key.endswith(".jsonl"):
                        continue
                    # Obtener el objeto completo
                    s3_obj = s3_client.get_object(Bucket=bucket, Key=key)
                    for line in s3_obj["Body"].iter_lines():
                        line = line.strip()
                        if not line:
                            continue
                        try:
                            record = json.loads(line)
                        except json.JSONDecodeError:
                            logger.error("Formato JSON inválido en %s: %s", key, line)
                            continue  # Saltar líneas malformadas
                        # Filtrar por proyecto
                        if record.get("project") != oss_project:
                            continue
                        # Filtrar por OSSPI / nombre de pod
                        if osspi.lower() == "yes":
                            data.append(record)
                        else:
                            expected_podname = f"jupyter-{username}"
                            if record.get("podName") == expected_podname:
                                data.append(record)
        except Exception as e:
            logger.error("Error al procesar S3 folder %s/%s: %s", bucket, prefix, e)
            raise FileNotFoundError(f"No se pudo leer archivos en S3 en {bucket}/{prefix}") from e

        return data