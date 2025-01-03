import pytest
from src.targets import TargetGenerator, Target, SecurityLevel, TargetType

def test_target_generator():
    generator = TargetGenerator()
    
    # Test get_targets_for_mission
    targets = generator.get_targets_for_mission("INF_001")
    assert len(targets) == 3
    assert targets[0].id == "MEGA_001"
    
    # Test get_target_by_id
    target = generator.get_target_by_id("MEGA_001")
    assert target is not None
    assert target.name == "MegaCorp Industries - Serveur RH"
    assert target.security_level == SecurityLevel.LOW 