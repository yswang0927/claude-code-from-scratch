#!/usr/bin/env python3
"""
test_api.py: 简单的API测试脚本

用于验证后端服务是否正常运行
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_health():
    """测试健康检查"""
    print("🔍 Testing health check...")
    try:
        response = requests.get(f"{BASE_URL}/")
        assert response.status_code == 200
        print("✅ Health check passed")
        return True
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_create_session():
    """测试创建会话"""
    print("\n🔍 Testing session creation...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/sessions",
            json={"title": "Test Session"}
        )
        assert response.status_code == 200
        data = response.json()
        session_id = data.get("id")
        print(f"✅ Session created: {session_id}")
        return session_id
    except Exception as e:
        print(f"❌ Session creation failed: {e}")
        return None

def test_list_sessions():
    """测试获取会话列表"""
    print("\n🔍 Testing session listing...")
    try:
        response = requests.get(f"{BASE_URL}/api/sessions")
        assert response.status_code == 200
        data = response.json()
        count = len(data.get("sessions", []))
        print(f"✅ Found {count} sessions")
        return True
    except Exception as e:
        print(f"❌ Session listing failed: {e}")
        return False

def test_get_session(session_id):
    """测试获取会话详情"""
    print(f"\n🔍 Testing get session {session_id}...")
    try:
        response = requests.get(f"{BASE_URL}/api/sessions/{session_id}")
        assert response.status_code == 200
        data = response.json()
        print(f"✅ Session details retrieved: {data.get('title')}")
        return True
    except Exception as e:
        print(f"❌ Get session failed: {e}")
        return False

def test_filesystem():
    """测试文件系统浏览"""
    print("\n🔍 Testing filesystem browsing...")
    try:
        response = requests.get(f"{BASE_URL}/api/filesystem/list?path=.")
        assert response.status_code == 200
        data = response.json()
        count = len(data.get("items", []))
        print(f"✅ Found {count} items in current directory")
        return True
    except Exception as e:
        print(f"❌ Filesystem browsing failed: {e}")
        return False

def test_delete_session(session_id):
    """测试删除会话"""
    print(f"\n🔍 Testing delete session {session_id}...")
    try:
        response = requests.delete(f"{BASE_URL}/api/sessions/{session_id}")
        assert response.status_code == 200
        print(f"✅ Session deleted")
        return True
    except Exception as e:
        print(f"❌ Delete session failed: {e}")
        return False

def main():
    """运行所有测试"""
    print("=" * 60)
    print("🧪 AI Agent Backend API Tests")
    print("=" * 60)
    
    # 等待服务启动
    print("\n⏳ Waiting for server to start...")
    for i in range(10):
        try:
            requests.get(f"{BASE_URL}/", timeout=1)
            break
        except:
            time.sleep(1)
            if i == 9:
                print("❌ Server did not start in time")
                return
    
    # 运行测试
    results = []
    
    # 基础测试
    results.append(("Health Check", test_health()))
    results.append(("List Sessions", test_list_sessions()))
    results.append(("Filesystem", test_filesystem()))
    
    # 会话管理测试
    session_id = test_create_session()
    if session_id:
        results.append(("Create Session", True))
        results.append(("Get Session", test_get_session(session_id)))
        results.append(("Delete Session", test_delete_session(session_id)))
    else:
        results.append(("Create Session", False))
        results.append(("Get Session", False))
        results.append(("Delete Session", False))
    
    # 打印结果
    print("\n" + "=" * 60)
    print("📊 Test Results")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
    
    print("\n" + "=" * 60)
    print(f"Total: {passed}/{total} tests passed")
    print("=" * 60)
    
    if passed == total:
        print("\n🎉 All tests passed! The backend is working correctly.")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please check the logs.")

if __name__ == "__main__":
    main()
