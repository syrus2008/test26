import pytest
from src.gameplay import JeuMission
from src.missions import Mission, MissionType, Faction
from src.save_manager import SaveManager

@pytest.fixture
def mission():
    return Mission(
        id="INF_001",
        titre="Test Mission",
        description="Test Description",
        type=MissionType.INFILTRATION,
        difficulte=1,
        recompense=1000,
        faction=Faction.SPECTRES,
        objectifs=["Test Objective"]
    )

def test_cmd_scan(mission):
    jeu = JeuMission(mission, None, SaveManager(None))
    result = jeu.cmd_scan([])
    assert "Cibles détectées:" in result
    assert len(result) > 1

def test_cmd_connect(mission):
    jeu = JeuMission(mission, None, SaveManager(None))
    result = jeu.cmd_connect(["MEGA_001"])
    assert "Connexion établie" in result[0] 

def test_update_alert_level(mission):
    jeu = JeuMission(mission, None, SaveManager(None))
    jeu.update_alert_level(50)
    assert jeu.alert_level == 50
    jeu.update_alert_level(60)
    assert jeu.alert_level == 100  # Ne doit pas dépasser 100
    assert jeu.detected == True

def test_mission_completion(mission):
    jeu = JeuMission(mission, None, SaveManager(None))
    jeu.systeme_compromis = True
    jeu.check_mission_objectives()
    assert jeu.objectifs_completes[0] == True 

def test_mission_failure(mission):
    jeu = JeuMission(mission, None, SaveManager(None))
    jeu.update_alert_level(100)
    assert not jeu.is_running
    assert jeu.detected

def test_invalid_command(mission):
    jeu = JeuMission(mission, None, SaveManager(None))
    result = jeu.cmd_connect([])
    assert "Usage:" in result[0]

def test_target_analysis(mission):
    jeu = JeuMission(mission, None, SaveManager(None))
    jeu.cmd_connect(["MEGA_001"])
    result = jeu.cmd_analyze([])
    assert "Analyse de sécurité:" in result[0]
    assert len(result) > 3 

def test_mission_objectives():
    # Test setup
    mission = Mission(id="test", type=MissionType.INFILTRATION)
    game = JeuMission(mission, None, MockSaveManager())
    
    # Test initial state
    assert not any(game.objectifs_completes)
    
    # Test objective completion
    game.systeme_compromis = True
    game.check_mission_objectives()
    assert game.objectifs_completes[0] 