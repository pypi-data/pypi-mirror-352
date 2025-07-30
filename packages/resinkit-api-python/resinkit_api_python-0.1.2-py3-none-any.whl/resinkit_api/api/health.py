from fastapi import APIRouter
import httpx
import asyncio
from typing import Dict, Any
import aiomysql
from aiokafka import AIOKafkaProducer
import logging

router = APIRouter(tags=["health"])

logger = logging.getLogger(__name__)


@router.get("/health")
async def health_check():
    return {"status": "OK"}


@router.get("/sysinfo")
async def system_info():
    """
    Check the health status of all ResinKit components
    """
    components = {
        "flink_job_manager": await check_flink_job_manager(),
        "flink_sql_gateway": await check_flink_sql_gateway(),
        "kafka": await check_kafka(),
        "mariadb": await check_mariadb(),
        "minio": await check_minio()
    }
    
    # Overall system status
    all_healthy = all(comp["status"] == "healthy" for comp in components.values())
    
    return {
        "system_status": "healthy" if all_healthy else "degraded",
        "timestamp": asyncio.get_event_loop().time(),
        "components": components
    }


async def check_flink_job_manager() -> Dict[str, Any]:
    """Check Flink Job Manager health at http://localhost:8081"""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get("http://localhost:8081/overview")
            if response.status_code == 200:
                data = response.json()
                return {
                    "status": "healthy",
                    "endpoint": "http://localhost:8081",
                    "details": {
                        "taskmanagers": data.get("taskmanagers", 0),
                        "slots_total": data.get("slots-total", 0),
                        "slots_available": data.get("slots-available", 0)
                    }
                }
            else:
                return {
                    "status": "unhealthy",
                    "endpoint": "http://localhost:8081",
                    "error": f"HTTP {response.status_code}"
                }
    except Exception as e:
        return {
            "status": "unhealthy",
            "endpoint": "http://localhost:8081",
            "error": str(e)
        }


async def check_flink_sql_gateway() -> Dict[str, Any]:
    """Check Flink SQL Gateway health at http://localhost:8083"""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get("http://localhost:8083/v1/info")
            if response.status_code == 200:
                data = response.json()
                return {
                    "status": "healthy",
                    "endpoint": "http://localhost:8083",
                    "details": {
                        "product_name": data.get("productName", "unknown"),
                        "version": data.get("version", "unknown")
                    }
                }
            else:
                return {
                    "status": "unhealthy",
                    "endpoint": "http://localhost:8083",
                    "error": f"HTTP {response.status_code}"
                }
    except Exception as e:
        return {
            "status": "unhealthy",
            "endpoint": "http://localhost:8083",
            "error": str(e)
        }


async def check_kafka() -> Dict[str, Any]:
    """Check Kafka health at localhost:9092"""
    try:
        producer = AIOKafkaProducer(
            bootstrap_servers='localhost:9092',
            request_timeout_ms=5000,
            connections_max_idle_ms=5000
        )
        await producer.start()
        
        # Get cluster metadata to verify connection
        cluster = producer.client.cluster
        brokers = list(cluster.brokers())
        
        await producer.stop()
        
        return {
            "status": "healthy",
            "endpoint": "localhost:9092",
            "details": {
                "brokers_count": len(brokers),
                "broker_ids": [broker.nodeId for broker in brokers]
            }
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "endpoint": "localhost:9092",
            "error": str(e)
        }


async def check_mariadb() -> Dict[str, Any]:
    """Check MariaDB health at localhost:3306"""
    try:
        connection = await aiomysql.connect(
            host='localhost',
            port=3306,
            user='resinkit',
            password='inspect_mariadb',
            db='flink',
            connect_timeout=5
        )
        
        async with connection.cursor() as cursor:
            await cursor.execute("SELECT VERSION()")
            version = await cursor.fetchone()
            await cursor.execute("SELECT COUNT(*) as table_count FROM information_schema.tables WHERE table_schema = 'flink'")
            table_count = await cursor.fetchone()
        
        connection.close()
        
        return {
            "status": "healthy",
            "endpoint": "localhost:3306",
            "details": {
                "version": version[0] if version else "unknown",
                "database": "flink",
                "table_count": table_count[0] if table_count else 0
            }
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "endpoint": "localhost:3306",
            "error": str(e)
        }


async def check_minio() -> Dict[str, Any]:
    """Check MinIO health at http://127.0.0.1:9000"""
    try:
        # Check MinIO health endpoint
        async with httpx.AsyncClient(timeout=5.0) as client:
            # Try to access MinIO health endpoint
            auth = httpx.BasicAuth("admin", "minio123")
            response = await client.get("http://127.0.0.1:9000/minio/health/live", auth=auth)
            
            if response.status_code == 200:
                # Try to list buckets to verify credentials
                try:
                    buckets_response = await client.get("http://127.0.0.1:9000/", auth=auth)
                    return {
                        "status": "healthy",
                        "endpoint": "http://127.0.0.1:9000",
                        "details": {
                            "health_check": "passed",
                            "credentials": "valid"
                        }
                    }
                except:
                    return {
                        "status": "healthy",
                        "endpoint": "http://127.0.0.1:9000",
                        "details": {
                            "health_check": "passed",
                            "credentials": "not_verified"
                        }
                    }
            else:
                return {
                    "status": "unhealthy",
                    "endpoint": "http://127.0.0.1:9000",
                    "error": f"Health check failed: HTTP {response.status_code}"
                }
    except Exception as e:
        return {
            "status": "unhealthy",
            "endpoint": "http://127.0.0.1:9000",
            "error": str(e)
        }


# Add other existing endpoints here if any
