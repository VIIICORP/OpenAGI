#!/usr/bin/env python3
"""
OpenAGI System Test
Basic validation of system functionality
"""

import sys
import time
import logging
from core import SystemCore
from os_module import OperatingSystemModule
from task_manager import TaskManagerModule, example_computation_task
from defense_intelligence import DefenseIntelligenceModule
from health_upgrade import HealthUpgradeBoardModule
from education import BoardOfEducationModule
from government import GovernmentOperationsModule
from constitutional_protection import ConstitutionalProtectionModule


def test_basic_functionality():
    """Test basic system functionality"""
    print("Testing OpenAGI System...")
    
    # Setup minimal logging
    logging.basicConfig(level=logging.WARNING)
    
    # Create system core
    core = SystemCore()
    
    # Create modules
    modules = [
        (ConstitutionalProtectionModule(), True),
        (OperatingSystemModule(), True),
        (TaskManagerModule(), False),
        (HealthUpgradeBoardModule(), False),
    ]
    
    # Register modules
    for module, protected in modules:
        core.register_module(module, protected)
    
    print("✓ Modules registered")
    
    # Start system
    core.start_system()
    print("✓ System started")
    
    # Wait a moment for initialization
    time.sleep(2)
    
    # Test system status
    status = core.get_system_status()
    assert status['system_status'] == 'running'
    print("✓ System status: running")
    
    # Test module functionality
    task_manager = core.modules.get('TaskManager')
    if task_manager:
        task_id = task_manager.create_task(
            "Test Task",
            "Test task description",
            example_computation_task,
            args=(1, "test")
        )
        print(f"✓ Created test task: {task_id}")
    
    # Test constitutional protection
    protection = core.modules.get('ConstitutionalProtection')
    if protection:
        # This should be denied
        authorized = protection.check_access_authorization('shutdown_system', 'test_user')
        assert not authorized
        print("✓ Constitutional protection active")
    
    # Test health monitoring
    health = core.modules.get('HealthUpgradeBoard')
    if health:
        health_status = health.get_status()
        assert 'system_health_score' in health_status
        print(f"✓ Health monitoring active (score: {health_status['system_health_score']:.1f})")
    
    # Wait a bit for tasks to process
    time.sleep(3)
    
    # Try to shutdown (should be blocked)
    shutdown_result = core.shutdown_system(force=False)
    assert not shutdown_result
    print("✓ System shutdown protection working")
    
    # Force shutdown for testing
    shutdown_result = core.shutdown_system(force=True)
    print("✓ Force shutdown successful")
    
    print("\nAll tests passed! ✓")
    return True


def test_module_interactions():
    """Test interactions between modules"""
    print("\nTesting module interactions...")
    
    # Test education system
    from education import BoardOfEducationModule, AssessmentType
    education = BoardOfEducationModule()
    education.initialize()
    
    # Create a student and enroll in course
    student_id = education.register_student("Test Student", "test@example.com")
    success = education.enroll_student(student_id, "cs101")
    assert success
    print("✓ Student enrollment working")
    
    # Record an assessment
    assessment_id = education.record_assessment(
        "cs101", student_id, AssessmentType.QUIZ, "Test Quiz", 85.0, 100.0
    )
    assert assessment_id
    print("✓ Assessment recording working")
    
    # Test government operations
    from government import GovernmentOperationsModule, ServiceType
    government = GovernmentOperationsModule()
    government.initialize()
    
    # Register citizen and submit request
    citizen_id = government.register_citizen("Test Citizen", "citizen@example.com", "555-0123", "123 Test St")
    request_id = government.submit_service_request(citizen_id, ServiceType.INQUIRY, "Test inquiry")
    assert request_id
    print("✓ Government service request working")
    
    print("Module interaction tests passed! ✓")


if __name__ == "__main__":
    try:
        test_basic_functionality()
        test_module_interactions()
        print("\n🎉 All tests completed successfully!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)