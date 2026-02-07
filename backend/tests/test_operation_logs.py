"""
测试操作日志查询API

需求: 17.10
"""

import pytest
from datetime import datetime, timedelta
from uuid import uuid4
from app.models.operation_log import OperationLog
from app.models.self_evaluation import SelfEvaluation
from app.models.teaching_office import TeachingOffice


def test_get_operation_logs_without_filters(client, db, teaching_office_user, teaching_office_token):
    """
    测试查询所有操作日志（无筛选条件）
    
    需求: 17.10
    """
    # 创建测试数据
    target_id = uuid4()
    logs = [
        OperationLog(
            operation_type="submit",
            operator_id=teaching_office_user.id,
            operator_name=teaching_office_user.name,
            operator_role=teaching_office_user.role,
            target_id=target_id,
            target_type="self_evaluation",
            details={"action": "submit_form"},
            operated_at=datetime.utcnow() - timedelta(hours=i)
        )
        for i in range(5)
    ]
    db.add_all(logs)
    db.commit()
    
    # 查询日志
    response = client.get(
        "/api/logs",
        headers={"Authorization": f"Bearer {teaching_office_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 5
    assert len(data["logs"]) == 5
    assert data["skip"] == 0
    assert data["limit"] == 100
    
    # 验证日志按时间倒序排列
    for i in range(len(data["logs"]) - 1):
        current_time = datetime.fromisoformat(data["logs"][i]["operated_at"].replace("Z", "+00:00"))
        next_time = datetime.fromisoformat(data["logs"][i + 1]["operated_at"].replace("Z", "+00:00"))
        assert current_time >= next_time


def test_get_operation_logs_filter_by_operation_type(client, db, teaching_office_user, teaching_office_token):
    """
    测试按操作类型筛选日志
    
    需求: 17.10
    """
    target_id = uuid4()
    
    # 创建不同类型的日志
    logs = [
        OperationLog(
            operation_type="submit",
            operator_id=teaching_office_user.id,
            operator_name=teaching_office_user.name,
            operator_role=teaching_office_user.role,
            target_id=target_id,
            target_type="self_evaluation",
            details={}
        ),
        OperationLog(
            operation_type="ai_score",
            operator_id=teaching_office_user.id,
            operator_name=teaching_office_user.name,
            operator_role=teaching_office_user.role,
            target_id=target_id,
            target_type="self_evaluation",
            details={}
        ),
        OperationLog(
            operation_type="submit",
            operator_id=teaching_office_user.id,
            operator_name=teaching_office_user.name,
            operator_role=teaching_office_user.role,
            target_id=uuid4(),
            target_type="self_evaluation",
            details={}
        ),
    ]
    db.add_all(logs)
    db.commit()
    
    # 筛选 submit 类型的日志
    response = client.get(
        "/api/logs?operation_type=submit",
        headers={"Authorization": f"Bearer {teaching_office_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert len(data["logs"]) == 2
    for log in data["logs"]:
        assert log["operation_type"] == "submit"


def test_get_operation_logs_filter_by_operator(client, db, teaching_office_user, evaluation_team_user, teaching_office_token):
    """
    测试按操作人筛选日志
    
    需求: 17.10
    """
    target_id = uuid4()
    
    # 创建不同操作人的日志
    logs = [
        OperationLog(
            operation_type="submit",
            operator_id=teaching_office_user.id,
            operator_name=teaching_office_user.name,
            operator_role=teaching_office_user.role,
            target_id=target_id,
            target_type="self_evaluation",
            details={}
        ),
        OperationLog(
            operation_type="manual_score",
            operator_id=evaluation_team_user.id,
            operator_name=evaluation_team_user.name,
            operator_role=evaluation_team_user.role,
            target_id=target_id,
            target_type="self_evaluation",
            details={}
        ),
        OperationLog(
            operation_type="submit",
            operator_id=teaching_office_user.id,
            operator_name=teaching_office_user.name,
            operator_role=teaching_office_user.role,
            target_id=uuid4(),
            target_type="self_evaluation",
            details={}
        ),
    ]
    db.add_all(logs)
    db.commit()
    
    # 筛选特定操作人的日志
    response = client.get(
        f"/api/logs?operator_id={teaching_office_user.id}",
        headers={"Authorization": f"Bearer {teaching_office_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert len(data["logs"]) == 2
    for log in data["logs"]:
        assert log["operator_id"] == str(teaching_office_user.id)


def test_get_operation_logs_filter_by_time_range(client, db, teaching_office_user, teaching_office_token):
    """
    测试按时间范围筛选日志
    
    需求: 17.10
    """
    target_id = uuid4()
    now = datetime.utcnow()
    
    # 创建不同时间的日志
    logs = [
        OperationLog(
            operation_type="submit",
            operator_id=teaching_office_user.id,
            operator_name=teaching_office_user.name,
            operator_role=teaching_office_user.role,
            target_id=target_id,
            target_type="self_evaluation",
            details={},
            operated_at=now - timedelta(days=5)
        ),
        OperationLog(
            operation_type="ai_score",
            operator_id=teaching_office_user.id,
            operator_name=teaching_office_user.name,
            operator_role=teaching_office_user.role,
            target_id=target_id,
            target_type="self_evaluation",
            details={},
            operated_at=now - timedelta(days=2)
        ),
        OperationLog(
            operation_type="manual_score",
            operator_id=teaching_office_user.id,
            operator_name=teaching_office_user.name,
            operator_role=teaching_office_user.role,
            target_id=target_id,
            target_type="self_evaluation",
            details={},
            operated_at=now
        ),
    ]
    db.add_all(logs)
    db.commit()
    
    # 筛选最近3天的日志
    start_date = (now - timedelta(days=3)).isoformat()
    response = client.get(
        f"/api/logs?start_date={start_date}",
        headers={"Authorization": f"Bearer {teaching_office_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert len(data["logs"]) == 2


def test_get_operation_logs_with_pagination(client, db, teaching_office_user, teaching_office_token):
    """
    测试分页功能
    
    需求: 17.10
    """
    target_id = uuid4()
    
    # 创建10条日志
    logs = [
        OperationLog(
            operation_type="submit",
            operator_id=teaching_office_user.id,
            operator_name=teaching_office_user.name,
            operator_role=teaching_office_user.role,
            target_id=target_id,
            target_type="self_evaluation",
            details={"index": i},
            operated_at=datetime.utcnow() - timedelta(hours=i)
        )
        for i in range(10)
    ]
    db.add_all(logs)
    db.commit()
    
    # 第一页（前5条）
    response = client.get(
        "/api/logs?skip=0&limit=5",
        headers={"Authorization": f"Bearer {teaching_office_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 10
    assert len(data["logs"]) == 5
    assert data["skip"] == 0
    assert data["limit"] == 5
    
    # 第二页（后5条）
    response = client.get(
        "/api/logs?skip=5&limit=5",
        headers={"Authorization": f"Bearer {teaching_office_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 10
    assert len(data["logs"]) == 5
    assert data["skip"] == 5
    assert data["limit"] == 5


def test_get_operation_logs_combined_filters(client, db, teaching_office_user, evaluation_team_user, teaching_office_token):
    """
    测试组合多个筛选条件
    
    需求: 17.10
    """
    target_id = uuid4()
    now = datetime.utcnow()
    
    # 创建多种类型的日志
    logs = [
        OperationLog(
            operation_type="submit",
            operator_id=teaching_office_user.id,
            operator_name=teaching_office_user.name,
            operator_role=teaching_office_user.role,
            target_id=target_id,
            target_type="self_evaluation",
            details={},
            operated_at=now - timedelta(days=1)
        ),
        OperationLog(
            operation_type="submit",
            operator_id=teaching_office_user.id,
            operator_name=teaching_office_user.name,
            operator_role=teaching_office_user.role,
            target_id=target_id,
            target_type="self_evaluation",
            details={},
            operated_at=now - timedelta(days=5)
        ),
        OperationLog(
            operation_type="manual_score",
            operator_id=evaluation_team_user.id,
            operator_name=evaluation_team_user.name,
            operator_role=evaluation_team_user.role,
            target_id=target_id,
            target_type="self_evaluation",
            details={},
            operated_at=now - timedelta(days=1)
        ),
    ]
    db.add_all(logs)
    db.commit()
    
    # 组合筛选：操作类型=submit，操作人=teaching_office_user，最近3天
    start_date = (now - timedelta(days=3)).isoformat()
    response = client.get(
        f"/api/logs?operation_type=submit&operator_id={teaching_office_user.id}&start_date={start_date}",
        headers={"Authorization": f"Bearer {teaching_office_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert len(data["logs"]) == 1
    assert data["logs"][0]["operation_type"] == "submit"
    assert data["logs"][0]["operator_id"] == str(teaching_office_user.id)


def test_get_operation_log_detail(client, db, teaching_office_user, teaching_office_token):
    """
    测试查询单个日志详情
    
    需求: 17.10
    """
    # 创建测试日志
    log = OperationLog(
        operation_type="submit",
        operator_id=teaching_office_user.id,
        operator_name=teaching_office_user.name,
        operator_role=teaching_office_user.role,
        target_id=uuid4(),
        target_type="self_evaluation",
        details={"action": "submit_form", "data": {"field1": "value1"}}
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    
    # 查询日志详情
    response = client.get(
        f"/api/logs/{log.id}",
        headers={"Authorization": f"Bearer {teaching_office_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(log.id)
    assert data["operation_type"] == "submit"
    assert data["operator_id"] == str(teaching_office_user.id)
    assert data["operator_name"] == teaching_office_user.name
    assert data["details"]["action"] == "submit_form"


def test_get_operation_log_detail_not_found(client, teaching_office_token):
    """
    测试查询不存在的日志
    
    需求: 17.10
    """
    fake_id = uuid4()
    response = client.get(
        f"/api/logs/{fake_id}",
        headers={"Authorization": f"Bearer {teaching_office_token}"}
    )
    
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_get_logs_by_evaluation(client, db, teaching_office_user, teaching_office_token):
    """
    测试查询特定自评表的所有日志
    
    需求: 17.10
    """
    evaluation_id = uuid4()
    other_evaluation_id = uuid4()
    
    # 创建针对特定自评表的日志
    logs = [
        OperationLog(
            operation_type="submit",
            operator_id=teaching_office_user.id,
            operator_name=teaching_office_user.name,
            operator_role=teaching_office_user.role,
            target_id=evaluation_id,
            target_type="self_evaluation",
            details={}
        ),
        OperationLog(
            operation_type="ai_score",
            operator_id=teaching_office_user.id,
            operator_name=teaching_office_user.name,
            operator_role=teaching_office_user.role,
            target_id=evaluation_id,
            target_type="self_evaluation",
            details={}
        ),
        OperationLog(
            operation_type="submit",
            operator_id=teaching_office_user.id,
            operator_name=teaching_office_user.name,
            operator_role=teaching_office_user.role,
            target_id=other_evaluation_id,
            target_type="self_evaluation",
            details={}
        ),
    ]
    db.add_all(logs)
    db.commit()
    
    # 查询特定自评表的日志
    response = client.get(
        f"/api/logs/by-evaluation/{evaluation_id}",
        headers={"Authorization": f"Bearer {teaching_office_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert len(data["logs"]) == 2
    for log in data["logs"]:
        assert log["target_id"] == str(evaluation_id)


def test_get_operation_logs_requires_authentication(client):
    """
    测试未认证用户无法查询日志
    
    需求: 17.10
    """
    response = client.get("/api/logs")
    assert response.status_code == 401


def test_get_operation_logs_empty_result(client, teaching_office_token):
    """
    测试查询结果为空的情况
    
    需求: 17.10
    """
    response = client.get(
        "/api/logs",
        headers={"Authorization": f"Bearer {teaching_office_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert len(data["logs"]) == 0


def test_get_operation_logs_filter_by_target_type(client, db, teaching_office_user, teaching_office_token):
    """
    测试按目标对象类型筛选日志
    
    需求: 17.10
    """
    # 创建不同目标类型的日志
    logs = [
        OperationLog(
            operation_type="submit",
            operator_id=teaching_office_user.id,
            operator_name=teaching_office_user.name,
            operator_role=teaching_office_user.role,
            target_id=uuid4(),
            target_type="self_evaluation",
            details={}
        ),
        OperationLog(
            operation_type="upload",
            operator_id=teaching_office_user.id,
            operator_name=teaching_office_user.name,
            operator_role=teaching_office_user.role,
            target_id=uuid4(),
            target_type="attachment",
            details={}
        ),
        OperationLog(
            operation_type="submit",
            operator_id=teaching_office_user.id,
            operator_name=teaching_office_user.name,
            operator_role=teaching_office_user.role,
            target_id=uuid4(),
            target_type="self_evaluation",
            details={}
        ),
    ]
    db.add_all(logs)
    db.commit()
    
    # 筛选 self_evaluation 类型的日志
    response = client.get(
        "/api/logs?target_type=self_evaluation",
        headers={"Authorization": f"Bearer {teaching_office_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert len(data["logs"]) == 2
    for log in data["logs"]:
        assert log["target_type"] == "self_evaluation"
